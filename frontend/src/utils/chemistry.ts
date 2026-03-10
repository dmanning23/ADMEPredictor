/** Common example molecules for the example picker */
export const EXAMPLE_MOLECULES = [
  { name: 'Aspirin',    smiles: 'CC(=O)OC1=CC=CC=C1C(=O)O' },
  { name: 'Caffeine',   smiles: 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C' },
  { name: 'Ibuprofen',  smiles: 'CC(C)Cc1ccc(cc1)C(C)C(=O)O' },
  { name: 'Paracetamol',smiles: 'CC(=O)Nc1ccc(O)cc1' },
  { name: 'Sildenafil', smiles: 'CCCC1=NN(C2=CC(=C(C=C2)S(=O)(=O)N3CCN(C)CC3)OCC)C(=O)C1' },
] as const

/** Basic Lipinski Rule of Five check (client-side preview only) */
export function checkRuleOfFive(mw: number, logP: number, hbd: number, hba: number) {
  const violations: string[] = []
  if (mw > 500)  violations.push(`MW ${mw.toFixed(0)} > 500`)
  if (logP > 5)  violations.push(`LogP ${logP.toFixed(1)} > 5`)
  if (hbd > 5)   violations.push(`HBD ${hbd} > 5`)
  if (hba > 10)  violations.push(`HBA ${hba} > 10`)
  return { passes: violations.length === 0, violations }
}
