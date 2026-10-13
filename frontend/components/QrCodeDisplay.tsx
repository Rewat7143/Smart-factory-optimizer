"use client"
import React, { useMemo, useRef } from 'react'
import { generateQrMatrix, getQrSvgPaths, drawQrToCanvas } from '@/lib/qr'

interface QrCodeDisplayProps {
  url: string
  assetId: string
  assetName?: string
  equipmentType?: string
  pcc?: string
  cellSize?: number
  showControls?: boolean
  showLabelBorder?: boolean
  instructionText?: string
  isProduction?: boolean
  warningText?: string | null
}

export default function QrCodeDisplay({
  url,
  assetId,
  assetName,
  equipmentType,
  pcc,
  cellSize = 6,
  showControls = true,
  showLabelBorder = true,
  instructionText = 'Scan for Energy Passport',
  isProduction = true,
  warningText
}: QrCodeDisplayProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  const matrix = useMemo(() => {
    try {
      return generateQrMatrix(url)
    } catch (e) {
      console.error('Failed to generate QR matrix:', e)
      return []
    }
  }, [url])

  const svgData = useMemo(() => {
    if (!matrix || matrix.length === 0) return null
    return getQrSvgPaths(matrix, cellSize, 4)
  }, [matrix, cellSize])

  const handleDownloadPng = () => {
    if (!matrix || matrix.length === 0) return
    const canvas = document.createElement('canvas')
    drawQrToCanvas(canvas, matrix, 12, 4) // High-res 12px cells for print crispness
    const pngUrl = canvas.toDataURL('image/png')
    const link = document.createElement('a')
    link.download = `QR_LABEL_${assetId}.png`
    link.href = pngUrl
    link.click()
  }

  const handleCopyUrl = () => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(url)
      alert(`Permanent URL copied to clipboard:\n${url}`)
    }
  }

  if (!svgData) {
    return <div className="text-xs text-rose-600 font-bold p-4">Error generating QR Code</div>
  }

  return (
    <div className="flex flex-col items-center">
      {/* Warning banner if URL is localhost */}
      {!isProduction && (
        <div className="mb-3 w-full bg-amber-50 border border-amber-300 rounded-lg p-2.5 text-[11px] font-bold text-amber-900 flex items-start gap-2">
          <span>⚠️</span>
          <span>
            {warningText ||
              'Development URL: This QR points to localhost. Outside mobile devices will not be able to resolve this URL. Set NEXT_PUBLIC_APP_URL for production labels.'}
          </span>
        </div>
      )}

      {/* Industrial Physical Label Card (Print-Ready) */}
      <div
        className={`bg-white rounded-xl text-slate-900 flex flex-col items-center text-center p-3 sm:p-4 transition-all w-full max-w-[320px] mx-auto ${
          showLabelBorder
            ? 'border-2 border-slate-800 shadow-sm'
            : ''
        }`}
      >
        {/* Label Header */}
        <div className="w-full border-b-2 border-slate-800 pb-2 mb-2 text-left">
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Factory Energy Autopilot • Asset Passport
          </div>
          <div className="text-sm sm:text-base font-black text-slate-900 uppercase tracking-tight truncate">
            {assetName || assetId}
          </div>
          <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 mt-0.5">
            <span className="font-mono bg-slate-100 px-1.5 py-0.2 rounded border border-slate-300">
              {assetId}
            </span>
            <span>{pcc || 'PCC-01'}</span>
          </div>
        </div>

        {/* QR Code SVG */}
        <div className="p-2 bg-white rounded-lg border border-slate-200 flex items-center justify-center w-full">
          <svg
            viewBox={`0 0 ${svgData.svgSize} ${svgData.svgSize}`}
            className="w-full max-w-[220px] sm:max-w-[240px] h-auto aspect-square block"
          >
            <rect width="100%" height="100%" fill="#FFFFFF" />
            {svgData.rects.map((r, i) => (
              <rect
                key={i}
                x={r.x}
                y={r.y}
                width={r.width}
                height={r.height}
                fill="#000000"
              />
            ))}
          </svg>
        </div>

        {/* Label Footer */}
        <div className="w-full border-t border-slate-200 pt-2 mt-2">
          <div className="text-[10px] font-black uppercase tracking-wider text-teal-800">
            {instructionText}
          </div>
          <div className="text-[9px] font-mono text-slate-400 truncate max-w-[240px] mt-0.5" title={url}>
            {url}
          </div>
        </div>
      </div>

      {/* Control Actions */}
      {showControls && (
        <div className="flex flex-wrap items-center justify-center gap-2 mt-3">
          <button
            onClick={handleDownloadPng}
            className="bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 transition-all"
            title="Download high-resolution PNG image of this label"
          >
            <span>📥</span>
            <span>Download PNG</span>
          </button>

          <button
            onClick={handleCopyUrl}
            className="bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 transition-all"
            title="Copy permanent destination URL to clipboard"
          >
            <span>🔗</span>
            <span>Copy URL</span>
          </button>
        </div>
      )}
    </div>
  )
}
