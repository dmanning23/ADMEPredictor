import type { RDKitModule } from '@rdkit/rdkit'

let _rdkit: Promise<RDKitModule> | null = null

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = import('@rdkit/rdkit')
      .then((m) => {
        // The CJS bundle exports initRDKitModule as module.exports (and .default for TS interop).
        // Vite's CJS→ESM wrapper surfaces it as m.default.
        const initRDKit = (m as unknown as { default: (opts?: { locateFile?: () => string }) => Promise<RDKitModule> }).default
        return initRDKit({ locateFile: () => '/RDKit_minimal.wasm' })
      })
      .catch((err) => {
        _rdkit = null  // allow retry on next call
        return Promise.reject(err)
      })
  }
  return _rdkit
}
