import { useRef, useState } from 'react'
import api from '../api/client'

const ACCEPTED = 'image/jpeg, image/png, image/gif, image/webp'
const MAX_MB = 5

export default function Upload() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)

  const handleFile = (selected) => {
    setResult(null)
    setError('')

    if (!selected) return

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(selected.type)) {
      setError(`File type "${selected.type}" is not allowed. Please upload a JPG, PNG, GIF, or WebP image.`)
      return
    }
    if (selected.size > MAX_MB * 1024 * 1024) {
      setError(`File is too large (${(selected.size / 1024 / 1024).toFixed(1)} MB). Maximum size is ${MAX_MB} MB.`)
      return
    }

    setFile(selected)
    setPreview(URL.createObjectURL(selected))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const { data } = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Image Upload</h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload product photos or receipts. Supported: JPG, PNG, GIF, WebP · Max {MAX_MB} MB.
        </p>
      </div>

      {!result ? (
        <div className="card space-y-5">
          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-drinkoo-400 hover:bg-drinkoo-50 transition-colors"
          >
            {preview ? (
              <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-lg object-contain" />
            ) : (
              <>
                <div className="text-4xl mb-2">🖼️</div>
                <p className="text-gray-600 font-medium">Drag & drop or click to select</p>
                <p className="text-gray-400 text-sm mt-1">JPG, PNG, GIF, WebP · Max {MAX_MB} MB</p>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED}
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </div>

          {file && (
            <div className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3 text-sm">
              <span className="text-gray-700 truncate">{file.name}</span>
              <span className="text-gray-400 ml-2 shrink-0">{(file.size / 1024).toFixed(0)} KB</span>
            </div>
          )}

          {error && <p className="error-text">{error}</p>}

          <div className="flex gap-3">
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="btn-primary flex-1"
            >
              {loading ? 'Uploading…' : 'Upload image'}
            </button>
            {file && (
              <button onClick={reset} className="btn-secondary">
                Clear
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="card text-center space-y-4">
          <div className="text-5xl">✅</div>
          <h2 className="text-xl font-semibold text-gray-800">Upload successful!</h2>
          <div className="text-left bg-gray-50 rounded-lg p-4 text-sm space-y-1">
            <div><span className="font-medium">Original name:</span> {result.original_name}</div>
            <div><span className="font-medium">Stored as:</span> {result.filename}</div>
            <div><span className="font-medium">Type:</span> {result.content_type}</div>
            <div><span className="font-medium">Size:</span> {(result.size_bytes / 1024).toFixed(1)} KB</div>
          </div>
          <button onClick={reset} className="btn-primary">Upload another</button>
        </div>
      )}
    </div>
  )
}
