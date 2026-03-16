import type { RDKitModule } from '@rdkit/rdkit'
import '@rdkit/rdkit/dist/RDKit_minimal.js'

let _rdkit: Promise<RDKitModule> | null = null

declare global {
  interface Window {
    initRDKitModule: (options?: { locateFile?: () => string }) => Promise<RDKitModule>
  }
}

export function getRDKit(): Promise<RDKitModule> {
  if (!_rdkit) {
    _rdkit = window.initRDKitModule({ locateFile: () => '/RDKit_minimal.wasm' })
  }
  return _rdkit
}
