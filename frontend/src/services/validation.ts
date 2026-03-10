/**
 * Client-side SMILES validation (lightweight, before hitting the API).
 * For authoritative validation, call /validate on the backend.
 */

const MAX_LENGTH = 500

const ALLOWED_CHARS = /^[A-Za-z0-9@+\-=\\/\\#$%()[\].,:*]+$/

export function quickValidate(smiles: string): { valid: boolean; error?: string } {
  if (!smiles.trim()) {
    return { valid: false, error: 'SMILES cannot be empty' }
  }
  if (smiles.length > MAX_LENGTH) {
    return { valid: false, error: `SMILES exceeds ${MAX_LENGTH} character limit` }
  }
  if (!ALLOWED_CHARS.test(smiles)) {
    return { valid: false, error: 'SMILES contains invalid characters' }
  }
  return { valid: true }
}
