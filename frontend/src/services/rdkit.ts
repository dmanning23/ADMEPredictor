import type { RDKitModule } from '@rdkit/rdkit'

let _rdkit: Promise<RDKitModule> | null = null

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = import('@rdkit/rdkit/dist/RDKit_minimal.js')
      .then(() => {
        if (typeof window.initRDKitModule !== 'function') {
          throw new Error('RDKit UMD bundle did not register window.initRDKitModule')
        }
        return window.initRDKitModule({ locateFile: () => '/RDKit_minimal.wasm' })
      })
      .catch((err) => {
        _rdkit = null  // allow retry on next call
        return Promise.reject(err)
      })
  }
  return _rdkit
}
