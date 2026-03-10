/**
 * CSV batch upload component.
 * Expects a CSV with a "smiles" column.
 * TODO: implement file parsing and batch API call.
 */

interface Props {
  onResults: (smiles: string[]) => void
}

export function BatchUpload({ onResults: _ }: Props) {
  return (
    <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center text-gray-500">
      <p className="font-medium">Batch Upload</p>
      <p className="text-sm mt-1">Upload a CSV with a <code>smiles</code> column (max 100 rows)</p>
      <button className="mt-4 text-sm bg-gray-100 px-4 py-2 rounded-lg hover:bg-gray-200 transition">
        Choose file
      </button>
      <p className="mt-3 text-xs text-gray-400">Coming soon</p>
    </div>
  )
}
