import { type PredictionResponse } from '../services/api'
import { PropertyCard } from './PropertyCard'
import { formatValue, formatPct, riskColour, solubilityColour } from '../utils/formatting'

interface Props {
  result: PredictionResponse
}

export function PredictionResults({ result }: Props) {
  const { properties: p, warnings, molecular_weight, rule_of_five } = result

  return (
    <div className="flex flex-col gap-6">
      {warnings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
          {warnings.map((w, i) => <p key={i}>{w}</p>)}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {p.solubility && (
          <PropertyCard
            label="Solubility (LogS)"
            value={formatValue(p.solubility.value)}
            unit="log mol/L"
            colourClass={solubilityColour(p.solubility.value)}
          />
        )}
        {p.permeability && (
          <PropertyCard
            label="Permeability (Caco-2)"
            value={formatValue(p.permeability.value)}
            unit="log cm/s"
          />
        )}
        {p.logp && (
          <PropertyCard
            label="Lipophilicity (LogP)"
            value={formatValue(p.logp.value)}
            unit="log"
          />
        )}
        {p.cyp3a4_inhibitor && (
          <PropertyCard
            label="CYP3A4 Inhibition"
            value={formatPct(p.cyp3a4_inhibitor.probability)}
            colourClass={riskColour(p.cyp3a4_inhibitor.probability)}
            badge={p.cyp3a4_inhibitor.prediction ? 'Inhibitor' : 'Non-inhibitor'}
            badgeColour={p.cyp3a4_inhibitor.prediction ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}
          />
        )}
        {p.herg_blocker && (
          <PropertyCard
            label="hERG Blocking"
            value={formatPct(p.herg_blocker.probability)}
            colourClass={riskColour(p.herg_blocker.probability)}
            badge={p.herg_blocker.prediction ? 'Blocker' : 'Non-blocker'}
            badgeColour={p.herg_blocker.prediction ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}
          />
        )}
        {molecular_weight != null && (
          <PropertyCard label="Molecular Weight" value={formatValue(molecular_weight, 1)} unit="Da" />
        )}
      </div>

      {rule_of_five && (
        <div className={`rounded-lg p-3 text-sm ${rule_of_five.passes ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          <strong>Lipinski Rule of Five:</strong>{' '}
          {rule_of_five.passes ? 'Passes' : `Violations: ${rule_of_five.violations.join(', ')}`}
        </div>
      )}
    </div>
  )
}
