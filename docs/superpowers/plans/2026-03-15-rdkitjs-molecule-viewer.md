# RDKit.js 2D Molecule Viewer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `MoleculeViewer` placeholder with a real 2D molecule structure renderer using RDKit.js WASM, rendering SVGs client-side with no backend call.

**Architecture:** A module-level singleton (`rdkit.ts`) lazy-loads and caches the RDKit WASM instance once. `MoleculeViewer.tsx` calls it on mount and on prop changes, rendering the resulting SVG as an `<img>` via a data URL to avoid XSS risk. WASM objects are always freed via `mol.delete()` in a `finally` block.

**Tech Stack:** React 19, TypeScript (`verbatimModuleSyntax`), `@rdkit/rdkit` npm package, Vite 7

---

## Chunk 1: Install dependency and configure Vite

### Task 1: Install @rdkit/rdkit and configure Vite

**Files:**
- Modify: `frontend/package.json` (via npm install)
- Modify: `frontend/vite.config.ts`
- Create: `frontend/public/RDKit_minimal.wasm` (copied from node_modules)

- [ ] **Step 1: Install the package**

Run from `frontend/`:
```bash
npm install @rdkit/rdkit
```
Expected: package added to `dependencies` in `package.json`, lockfile updated.

- [ ] **Step 2: Copy the WASM binary to public/**

The RDKit JS loader fetches the WASM by relative path at runtime. Copying it to `public/` makes it available at `/RDKit_minimal.wasm` in both dev and production — no Vite asset pipeline involvement needed.

Run from `frontend/`:
```bash
cp node_modules/@rdkit/rdkit/dist/RDKit_minimal.wasm public/
```

Note: `assetsInclude: ['**/*.wasm']` is intentionally NOT used — it would cause Vite to emit the WASM with a content-hash filename, breaking the RDKit loader's hardcoded relative path.

- [ ] **Step 3: Update vite.config.ts**

Add `optimizeDeps.exclude` to prevent Vite from trying to pre-bundle the WASM module. Keep all existing config:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  optimizeDeps: {
    exclude: ['@rdkit/rdkit'],
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **Step 4: Verify dev server starts**

Run from `frontend/`:
```bash
npm run dev
```
Expected: Vite starts without errors.

- [ ] **Step 5: Verify production build**

Run from `frontend/`:
```bash
npm run build && npm run preview
```
Expected: build completes, `dist/` contains `RDKit_minimal.wasm` (copied from `public/`), preview at `http://localhost:4173` loads.

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/public/RDKit_minimal.wasm
git commit -m "feat: install @rdkit/rdkit and configure Vite for WASM"
```

---

## Chunk 2: RDKit singleton service

### Task 2: Create src/services/rdkit.ts

**Files:**
- Create: `frontend/src/services/rdkit.ts`

This file exports a single `getRDKit()` function. It uses a module-level variable to cache the promise so the ~7MB WASM is only downloaded and initialized once per page load.

Notes:
- `RDKitModule` must use `import type` because `verbatimModuleSyntax` is enabled
- The init function is `initRDKitModule` (named export), not `m.default()` — `@rdkit/rdkit` does not have a typed default export

- [ ] **Step 1: Create the file**

`@rdkit/rdkit` uses a default export (the init function). It also requires a `locateFile` option so the loader knows where to fetch the WASM — without it, it resolves a relative path from inside `node_modules` which will 404. Point it at `/RDKit_minimal.wasm` (the file copied to `public/` in Chunk 1).

```ts
// frontend/src/services/rdkit.ts
import type { RDKitModule } from '@rdkit/rdkit'

let _rdkit: Promise<RDKitModule> | null = null

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = import('@rdkit/rdkit').then((m) =>
      m.default({ locateFile: () => '/RDKit_minimal.wasm' })
    )
  }
  return _rdkit
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npx tsc -p tsconfig.app.json --noEmit
```
Expected: no errors. If you see a type error on `m.default`, the package may expose the init function differently — try `m.default()` without arguments, or check the `dist/RDKit_minimal.d.ts` for what the module actually exports and adjust the call accordingly.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/rdkit.ts
git commit -m "feat: add RDKit.js singleton loader"
```

---

## Chunk 3: MoleculeViewer component

### Task 3: Rewrite MoleculeViewer.tsx

**Files:**
- Modify: `frontend/src/components/MoleculeViewer.tsx`

The component manages three display states: loading/idle (SMILES text), SVG ready (molecule image), and init failure ("Structure preview unavailable"). It re-renders whenever props change, keeping the previous SVG visible during a re-render (no flash to text).

Key implementation notes:
- Input to RDKit is `canonicalSmiles ?? smiles` — the backend-canonicalized form is preferred for consistency with predictions
- `mol.delete()` must be called in a `finally` block — WASM objects are manually memory-managed
- SVG is encoded with `encodeURIComponent` (not `btoa`) to handle Unicode characters in atom labels
- SVG is rendered as `<img src="data:image/svg+xml;charset=utf-8,...">` — rendering in the image element context prevents script execution in the SVG, which is the safe approach for SVG from untrusted sources
- The cleanup function sets `cancelled = true` to prevent stale async updates after unmount or prop change

- [ ] **Step 1: Rewrite the component**

```tsx
// frontend/src/components/MoleculeViewer.tsx
import { useEffect, useState } from 'react'
import { getRDKit } from '../services/rdkit'

interface Props {
  smiles: string
  canonicalSmiles: string | null
}

type ViewerState =
  | { status: 'loading' }
  | { status: 'ready'; dataUrl: string }
  | { status: 'error' }

export function MoleculeViewer({ smiles, canonicalSmiles }: Props) {
  const [state, setState] = useState<ViewerState>({ status: 'loading' })

  useEffect(() => {
    let cancelled = false

    async function render() {
      const input = canonicalSmiles ?? smiles
      try {
        const rdkit = await getRDKit()
        const mol = rdkit.get_mol(input)
        if (!mol) {
          // get_mol returns null for invalid SMILES — treat as error, not loading
          if (!cancelled) setState({ status: 'error' })
          return
        }
        let svg: string
        try {
          svg = mol.get_svg()
        } finally {
          mol.delete()
        }
        const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
        if (!cancelled) setState({ status: 'ready', dataUrl })
      } catch (err) {
        console.error('RDKit render error:', err)
        if (!cancelled) setState({ status: 'error' })
      }
    }

    render()
    return () => { cancelled = true }
  }, [smiles, canonicalSmiles])

  const display = canonicalSmiles ?? smiles

  if (state.status === 'error') {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center text-sm text-gray-500">
        <p className="font-mono text-xs break-all">{display}</p>
        <p className="mt-2 italic text-amber-600">Structure preview unavailable</p>
      </div>
    )
  }

  if (state.status === 'ready') {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col items-center gap-2">
        <img
          src={state.dataUrl}
          alt={`2D structure of ${display}`}
          className="w-72 h-48 object-contain"
        />
        <p className="font-mono text-xs text-gray-400 break-all">{display}</p>
      </div>
    )
  }

  // loading state — matches existing placeholder behaviour
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center text-sm text-gray-500">
      <p className="font-mono text-xs break-all">{display}</p>
      <p className="mt-2 italic">Loading structure…</p>
    </div>
  )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npx tsc -p tsconfig.app.json --noEmit
```
Expected: no errors.

- [ ] **Step 3: Manual smoke test**

Start the full stack (backend + frontend). Type `CC(=O)OC1=CC=CC=C1C(=O)O` (aspirin) in the input. Expected:
1. Input border turns green (validation passes)
2. Viewer briefly shows "Loading structure…"
3. 2D structure image appears (~1-2 seconds on first load while WASM initializes)
4. Subsequent molecules render faster (WASM cached)
5. Open browser devtools → Console — no errors logged

- [ ] **Step 4: Test error state**

Open browser devtools → Network tab → right-click `RDKit_minimal.wasm` and select "Block request URL". Reload and type a valid SMILES. Expected: viewer shows "Structure preview unavailable" in amber text, error logged to console.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/MoleculeViewer.tsx
git commit -m "feat: implement RDKit.js 2D molecule viewer"
```
