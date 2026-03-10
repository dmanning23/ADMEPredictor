interface Props {
  label: string
  value: string
  unit?: string
  colourClass?: string
  badge?: string
  badgeColour?: string
}

export function PropertyCard({ label, value, unit, colourClass = '', badge, badgeColour = 'bg-gray-100 text-gray-700' }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wider text-gray-500">{label}</span>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${colourClass}`}>{value}</span>
        {unit && <span className="text-sm text-gray-400">{unit}</span>}
      </div>
      {badge && (
        <span className={`self-start text-xs px-2 py-0.5 rounded-full font-medium ${badgeColour}`}>
          {badge}
        </span>
      )}
    </div>
  )
}
