# RDKit.js 2D Molecule Viewer — Design Spec

**Date:** 2026-03-15
**Status:** Approved

## Summary

Replace the `MoleculeViewer` placeholder with a real 2D structure renderer using RDKit.js (WASM). Renders an SVG of the molecule client-side — no backend call required.

## Scope

- One new utility file: `src/services/rdkit.ts`
- One component rewrite: `src/components/MoleculeViewer.tsx`
- One Vite config change: `vite.config.ts` — exclude `@rdkit/rdkit` from dependency pre-bundling
- One new dependency: `@rdkit/rdkit`

Out of scope: dark mode SVG theming, atom highlighting, interactive molecule editing.

## Architecture

### `src/services/rdkit.ts`

Module-level singleton that lazy-loads and initializes the RDKit WASM module exactly once. Exports a single function:

```ts
import type { RDKitModule } from '@rdkit/rdkit'

let _rdkit: Promise<RDKitModule> | null = null

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = import('@rdkit/rdkit').then(m => m.default())
  }
  return _rdkit
}
```

The `RDKitModule` type is imported with `import type` (required by `verbatimModuleSyntax`). The runtime dynamic import is separate. The promise is cached on first call — subsequent calls return the same promise, ensuring WASM is initialized exactly once regardless of component mount/unmount cycles.

### `src/components/MoleculeViewer.tsx`

Rewrites the existing placeholder component. Props are unchanged: `{ smiles: string, canonicalSmiles: string | null }`.

**Input to RDKit:** `canonicalSmiles ?? smiles`. Using the backend-canonicalized form ensures the rendered structure is consistent with what was actually predicted. Falls back to raw `smiles` only if `canonicalSmiles` is null.

**Behaviour on prop change:** The component re-runs the render pipeline whenever `smiles` or `canonicalSmiles` changes. While a new SVG is being generated, the previously rendered structure remains visible (no flash back to text).

**States:**

1. **Idle / RDKit loading** — show canonical SMILES text (existing behaviour, no visual regression)
2. **SVG ready** — render `<img src={dataUrl} />` in a white rounded container (~300×200px, centered)
3. **RDKit init failure** — show "Structure preview unavailable" in place of the SMILES text; log error to console
4. **Mol parse failure** (invalid input to get_mol) — silently show SMILES text; this path should not be reached since the upstream validation gate ensures `validation.valid === true` before this component renders

### SVG → img encoding

`btoa()` throws on non-Latin-1 characters (e.g. Unicode minus signs in atom labels). Use `encodeURIComponent` to safely encode:

```ts
const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
```

This produces a valid data URL without base64 encoding and handles any Unicode characters in the SVG output.

### WASM Memory Management

`get_mol()` returns a WASM-allocated object that must be freed explicitly. Always call `mol.delete()` in a `finally` block:

```ts
const mol = rdkit.get_mol(input)
if (!mol) return fallback
try {
  return mol.get_svg()
} finally {
  mol.delete()
}
```

This applies in both the success path and any error path where `mol` is non-null.

## Vite Configuration

RDKit.js must be excluded from Vite's dependency pre-bundling, and the WASM binary must be explicitly declared as an asset so it is copied into `dist/` at build time. Without both, the dev server works but production builds fail to find the WASM file.

Add to `vite.config.ts`:

```ts
optimizeDeps: {
  exclude: ['@rdkit/rdkit'],
},
assetsInclude: ['**/*.wasm'],
```

`optimizeDeps.exclude` prevents Vite from trying to bundle the WASM module. `assetsInclude` tells Vite to treat `.wasm` files as static assets and copy them to `dist/assets/` at build time, so the RDKit loader can `fetch()` the binary at runtime.

## Data Flow

```
smiles or canonicalSmiles prop changes
  → input = canonicalSmiles ?? smiles
  → getRDKit()                            (returns cached promise)
  → rdkit.get_mol(input)                  (returns null if invalid)
  → mol.get_svg()                         (returns SVG string)
  → mol.delete()                          (free WASM memory, always)
  → encodeURIComponent(svg)
  → <img src="data:image/svg+xml;charset=utf-8,..." />
```

## Error Handling

| Scenario | Behaviour |
|---|---|
| RDKit WASM fails to init | Show "Structure preview unavailable"; log error |
| `get_mol()` returns null | Fall back to SMILES text silently (upstream gate prevents this) |
| `get_svg()` throws | `mol.delete()` still called via `finally`; fall back to SMILES text |
| `canonicalSmiles` is null | Use raw `smiles` as input to `get_mol()` |

## Files Changed

| File | Action |
|---|---|
| `frontend/src/services/rdkit.ts` | Create |
| `frontend/src/components/MoleculeViewer.tsx` | Rewrite |
| `frontend/vite.config.ts` | Add `optimizeDeps.exclude` |
| `frontend/package.json` | Add `@rdkit/rdkit` |
