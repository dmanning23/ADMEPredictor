# RDKit.js 2D Molecule Viewer — Design Spec

**Date:** 2026-03-15
**Status:** Approved

## Summary

Replace the `MoleculeViewer` placeholder with a real 2D structure renderer using RDKit.js (WASM). Renders an SVG of the molecule client-side — no backend call required.

## Scope

- One new utility file: `src/services/rdkit.ts`
- One component rewrite: `src/components/MoleculeViewer.tsx`
- One new dependency: `@rdkit/rdkit`

Out of scope: dark mode SVG theming, atom highlighting, interactive molecule editing.

## Architecture

### `src/services/rdkit.ts`

Module-level singleton that lazy-loads and initializes the RDKit WASM module exactly once. Exports a single function:

```ts
export function getRDKit(): Promise<RDKitModule>
```

The promise is cached on first call. Subsequent calls return the same promise regardless of when they're made. This ensures the ~7MB WASM is downloaded only once and never re-initialized even if `MoleculeViewer` mounts/unmounts.

### `src/components/MoleculeViewer.tsx`

Rewrites the existing placeholder component. Behaviour:

1. **On mount** — calls `getRDKit()`, then uses `mol.get_svg()` to produce an SVG string
2. **While loading** — displays canonical SMILES text (existing behaviour, no visual regression)
3. **On success** — converts SVG string to a base64 data URL and renders as `<img>`, avoiding `dangerouslySetInnerHTML` and any XSS risk
4. **On error** (invalid mol or RDKit init failure) — silently falls back to SMILES text display

Props are unchanged: `{ smiles: string, canonicalSmiles: string | null }`.

## Data Flow

```
MoleculeViewer mounts
  → getRDKit()                          (returns cached promise if already called)
  → RDKit.get_mol(smiles)              (returns null if invalid)
  → mol.get_svg()                       (returns SVG string)
  → btoa(svg) → data:image/svg+xml     (safe data URL)
  → <img src={dataUrl} />              (rendered in image context, no script execution)
```

## Loading Strategy

RDKit is loaded via `@rdkit/rdkit` npm package, imported dynamically inside `getRDKit()` so it is excluded from the initial bundle and only fetched when a valid SMILES is first displayed.

## Security

SVG is rendered as an `<img>` via a `data:image/svg+xml;base64,...` URL. This runs entirely in image rendering context — scripts inside the SVG are not executed, eliminating XSS risk. `dangerouslySetInnerHTML` is not used.

## Error Handling

- RDKit init failure: log to console, fall back to SMILES text
- Invalid SMILES: `get_mol()` returns null — check before calling `get_svg()`, fall back to SMILES text
- No error UI shown to user — the validation layer upstream already handles invalid SMILES, so `MoleculeViewer` only renders when `validation.valid === true`

## Files Changed

| File | Action |
|---|---|
| `frontend/src/services/rdkit.ts` | Create |
| `frontend/src/components/MoleculeViewer.tsx` | Rewrite |
| `frontend/package.json` | Add `@rdkit/rdkit` |
