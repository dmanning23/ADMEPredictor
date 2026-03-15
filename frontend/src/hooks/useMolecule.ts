import { useState, useEffect } from 'react'
import { validateSmiles, type ValidationResponse } from '../services/api'
import { quickValidate } from '../services/validation'

export function useMolecule() {
  const [smiles, setSmiles] = useState('')
  const [validation, setValidation] = useState<ValidationResponse | null>(null)
  const [validating, setValidating] = useState(false)

  useEffect(() => {
    const quick = quickValidate(smiles)
    if (!quick.valid) {
      setValidation(null)
      return
    }

    const timer = setTimeout(async () => {
      setValidating(true)
      try {
        const result = await validateSmiles(smiles)
        setValidation(result)
      } catch {
        setValidation(null)
      } finally {
        setValidating(false)
      }
    }, 400) // debounce

    return () => clearTimeout(timer)
  }, [smiles])

  return { smiles, setSmiles, validation, validating }
}
