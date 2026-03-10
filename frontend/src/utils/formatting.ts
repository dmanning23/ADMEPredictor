/** Format a regression value for display */
export function formatValue(value: number, decimals = 2): string {
  return value.toFixed(decimals)
}

/** Convert a probability [0,1] to a percentage string */
export function formatPct(probability: number): string {
  return `${(probability * 100).toFixed(1)}%`
}

/** Severity colour classes based on probability (for hERG / CYP3A4) */
export function riskColour(probability: number): string {
  if (probability >= 0.7) return 'text-red-600'
  if (probability >= 0.4) return 'text-amber-500'
  return 'text-green-600'
}

/** Colour for solubility (LogS). Higher (less negative) is better. */
export function solubilityColour(logS: number): string {
  if (logS >= -2) return 'text-green-600'
  if (logS >= -4) return 'text-amber-500'
  return 'text-red-600'
}
