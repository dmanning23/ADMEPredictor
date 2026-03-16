import type { RDKitModule } from '@rdkit/rdkit'

let _rdkit: Promise<RDKitModule> | null = null

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = import('@rdkit/rdkit/dist/RDKit_minimal.js').then(() => {
      return window.initRDKitModule({ locateFile: () => '/RDKit_minimal.wasm' })
    })
  }
  return _rdkit
}
