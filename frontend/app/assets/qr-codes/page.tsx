"use client"
import React, { useEffect, useState, useMemo, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getApiBaseUrl, getAppBaseUrl, isProductionUrl } from '@/lib/config'
import QrCodeDisplay from '@/components/QrCodeDisplay'
import { generateQrMatrix, drawQrToCanvas } from '@/lib/qr'

interface Asset {
  asset_id: string
  name: string
  equipment_type?: string
  location?: string
  pcc_association?: string
  load_classification: string
  is_protected: number | boolean
  is_archived: number | boolean
  qr_url?: string
}

function QrPrintCenterContent() {
  const searchParams = useSearchParams()
  const preselectedId = searchParams.get('selected')

  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedAssetIds, setSelectedAssetIds] = useState<string[]>([])
  const [activePreviewId, setActivePreviewId] = useState<string>('')
  const [cellSize, setCellSize] = useState<number>(6)
  const [customInstruction, setCustomInstruction] = useState<string>('Scan for Energy Passport')
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null)
  const [customBaseUrl, setCustomBaseUrl] = useState<string>('')
  const [printDate, setPrintDate] = useState<string>('')

  useEffect(() => {
    setPrintDate(new Date().toLocaleDateString())
  }, [])

  const baseUrl = getApiBaseUrl()
  const appBaseUrl = getAppBaseUrl()
  const effectiveBaseUrl = (customBaseUrl.trim() || appBaseUrl).replace(/\/+$/, '')
  const isProd = isProductionUrl(effectiveBaseUrl)

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        setLoading(true)
        const res = await fetch(`${baseUrl}/assets?limit=100`)
        if (res.ok) {
          const json = await res.json()
          const items: Asset[] = json.assets || []
          setAssets(items)

          if (preselectedId && items.some((a) => a.asset_id === preselectedId)) {
            setSelectedAssetIds([preselectedId])
            setActivePreviewId(preselectedId)
          } else if (items.length > 0) {
            setSelectedAssetIds([items[0].asset_id])
            setActivePreviewId(items[0].asset_id)
          }
        }
      } catch (e) {
        console.error('Failed to load assets for QR generator:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchAssets()
  }, [preselectedId])

  const activeAsset = useMemo(() => {
    return assets.find((a) => a.asset_id === activePreviewId) || assets[0]
  }, [assets, activePreviewId])

  // Selected asset objects for batch printing
  const selectedAssets = useMemo(() => {
    return assets.filter((a) => selectedAssetIds.includes(a.asset_id))
  }, [assets, selectedAssetIds])

  const handleSelectAll = () => {
    if (selectedAssetIds.length === assets.length) {
      setSelectedAssetIds([])
    } else {
      setSelectedAssetIds(assets.map((a) => a.asset_id))
    }
  }

  const handleToggleSelect = (id: string) => {
    if (selectedAssetIds.includes(id)) {
      setSelectedAssetIds(selectedAssetIds.filter((x) => x !== id))
    } else {
      setSelectedAssetIds([...selectedAssetIds, id])
    }
  }

  const handlePrintSheet = () => {
    if (typeof window !== 'undefined') {
      window.print()
    }
  }

  const handleBatchDownloadPng = () => {
    selectedAssets.forEach((asset, idx) => {
      setTimeout(() => {
        const destUrl = `${effectiveBaseUrl}/assets/${asset.asset_id}`
        const matrix = generateQrMatrix(destUrl)
        const canvas = document.createElement('canvas')
        drawQrToCanvas(canvas, matrix, 12, 4)
        const pngUrl = canvas.toDataURL('image/png')
        const link = document.createElement('a')
        link.download = `QR_LABEL_${asset.asset_id}.png`
        link.href = pngUrl
        link.click()
      }, idx * 250)
    })
  }

  const handleCopyLink = (url: string) => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(url)
      setCopiedUrl(url)
      setTimeout(() => setCopiedUrl(null), 2000)
    }
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* SCREEN-ONLY VIEW (Hidden when printing) */}
      <div className="print:hidden space-y-4 sm:space-y-6">
        
        {/* HEADER */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-slate-300 pb-4 gap-3 sm:gap-4">
          <div className="w-full md:w-auto">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-800 uppercase break-words">
              QR Generator &amp; Print Center
            </h1>
            <p className="text-[11px] sm:text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">
              Generate &amp; Print Permanent Industrial Labels for Factory Loads
            </p>
          </div>

          <div className="grid grid-cols-1 sm:flex sm:flex-wrap items-center gap-2 w-full md:w-auto">
            <Link
              href="/assets"
              className="min-h-[44px] flex items-center justify-center text-center bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3.5 py-2.5 rounded-xl transition-all shadow-xs"
            >
              &larr; Back to Registry
            </Link>

            <button
              onClick={handlePrintSheet}
              disabled={selectedAssets.length === 0}
              className="min-h-[44px] flex items-center justify-center text-center bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm gap-1.5 uppercase tracking-wider disabled:opacity-50"
            >
              <span>🖨️</span>
              <span>Print Label Sheet ({selectedAssets.length})</span>
            </button>

            <button
              onClick={handleBatchDownloadPng}
              disabled={selectedAssets.length === 0}
              className="min-h-[44px] flex items-center justify-center text-center bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm gap-1.5 uppercase tracking-wider disabled:opacity-50"
            >
              <span>📥</span>
              <span>Download Selected PNGs</span>
            </button>
          </div>
        </div>

        {/* DOMAIN CONFIGURATION & LOCAL WARNING */}
        <div className={`p-4 rounded-xl border-2 text-xs font-bold ${
          isProd ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-amber-50 border-amber-300 text-amber-900'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-start gap-2.5">
              <span className="text-xl">{isProd ? '🌐' : '⚠️'}</span>
              <div>
                <div className="uppercase tracking-wider font-black">
                  {isProd ? 'Canonical Production Domain Active' : 'QR Destination Base URL'}
                </div>
                <p className="mt-0.5 font-normal text-slate-700">
                  QR codes encode: <code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono font-bold text-slate-900">{effectiveBaseUrl}/assets/[assetId]</code>
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-600 font-medium">Quick Presets:</span>
              <button
                type="button"
                onClick={() => setCustomBaseUrl('')}
                className="bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 px-2.5 py-1 rounded text-[11px] font-bold"
              >
                Default Origin
              </button>
              <button
                type="button"
                onClick={() => setCustomBaseUrl('http://172.24.132.35:3000')}
                className="bg-teal-700 hover:bg-teal-800 text-white px-2.5 py-1 rounded text-[11px] font-bold"
                title="Allows phone camera on the same local Wi-Fi to scan and open directly"
              >
                📱 Mobile Wi-Fi IP (172.24.132.35:3000)
              </button>
            </div>
          </div>

          <div className="mt-3 pt-2.5 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center gap-2">
            <label className="text-[11px] text-slate-600 font-medium whitespace-nowrap">
              Override Base URL for Sticker Labels:
            </label>
            <input
              type="text"
              value={customBaseUrl}
              onChange={(e) => setCustomBaseUrl(e.target.value)}
              placeholder={`e.g. ${appBaseUrl} or https://your-factory.vercel.app`}
              className="flex-1 bg-white border border-slate-300 rounded px-2.5 py-1 text-slate-900 font-mono text-xs"
            />
          </div>
        </div>

        {/* MAIN TWO-COLUMN WORKSPACE */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT: ASSET SELECTION TABLE (7 COLS) */}
          <div className="lg:col-span-7 bg-white border border-slate-300 rounded-xl p-4 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900">
                  Select Assets for Printing ({selectedAssetIds.length} of {assets.length} selected)
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Select one or more loads to batch-generate labels
                </p>
              </div>

              <button
                onClick={handleSelectAll}
                className="bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold px-3 py-1.5 rounded-lg"
              >
                {selectedAssetIds.length === assets.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            {loading ? (
              <div className="p-8 text-center text-slate-500 font-bold text-xs">
                Loading assets...
              </div>
            ) : (
              <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto text-xs">
                {assets.map((asset) => {
                  const isChecked = selectedAssetIds.includes(asset.asset_id)
                  const isCurrentPreview = activePreviewId === asset.asset_id
                  const permUrl = `${effectiveBaseUrl}/assets/${asset.asset_id}`

                  return (
                    <div
                      key={asset.asset_id}
                      onClick={() => setActivePreviewId(asset.asset_id)}
                      className={`p-3 flex items-center justify-between cursor-pointer transition-colors ${
                        isCurrentPreview
                          ? 'bg-teal-50 border-l-4 border-teal-600'
                          : 'hover:bg-slate-50 border-l-4 border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            e.stopPropagation()
                            handleToggleSelect(asset.asset_id)
                          }}
                          className="rounded text-teal-600"
                        />

                        <div>
                          <div className="font-bold text-slate-900 flex items-center gap-2">
                            <span className="font-mono">{asset.asset_id}</span>
                            <span>&bull;</span>
                            <span>{asset.name}</span>
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5">
                            {asset.equipment_type || 'General Load'} &bull; {asset.pcc_association || 'PCC-01'}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCopyLink(permUrl)
                          }}
                          className="text-[11px] bg-white border border-slate-300 hover:bg-slate-100 px-2 py-1 rounded text-slate-700 font-bold"
                          title="Copy destination URL"
                        >
                          {copiedUrl === permUrl ? '✓ Copied' : '🔗 Link'}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setActivePreviewId(asset.asset_id)
                          }}
                          className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-800 px-2 py-1 rounded font-bold"
                        >
                          Preview &rarr;
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* RIGHT: LIVE LABEL PREVIEW & CUSTOMIZATION (5 COLS) */}
          <div className="lg:col-span-5 bg-white border border-slate-300 rounded-xl p-6 shadow-sm space-y-6">
            <div className="border-b border-slate-200 pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900">
                Live Label Preview
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                WYSIWYG preview before physical printing
              </p>
            </div>

            {activeAsset ? (
              <div className="flex flex-col items-center">
                <QrCodeDisplay
                  url={`${effectiveBaseUrl}/assets/${activeAsset.asset_id}`}
                  assetId={activeAsset.asset_id}
                  assetName={activeAsset.name}
                  equipmentType={activeAsset.equipment_type}
                  pcc={activeAsset.pcc_association}
                  cellSize={cellSize}
                  showControls={true}
                  showLabelBorder={true}
                  instructionText={customInstruction}
                  isProduction={isProd}
                />

                {/* Customization options */}
                <div className="w-full mt-6 pt-4 border-t border-slate-200 space-y-3 text-xs font-bold">
                  <div>
                    <label className="block text-slate-700 mb-1">
                      Label Instruction Text
                    </label>
                    <input
                      type="text"
                      value={customInstruction}
                      onChange={(e) => setCustomInstruction(e.target.value)}
                      placeholder="e.g. Scan for Energy Passport"
                      className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-slate-900"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-700 mb-1">
                      QR Density / Size: {cellSize * 40}px
                    </label>
                    <input
                      type="range"
                      min={4}
                      max={10}
                      value={cellSize}
                      onChange={(e) => setCellSize(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div className="pt-2 text-[11px] text-slate-500 font-mono break-all bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-700 block mb-0.5">Destination URL:</span>
                    {effectiveBaseUrl}/assets/{activeAsset.asset_id}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 font-bold text-xs">
                Select an asset on the left to preview label
              </div>
            )}
          </div>

        </div>

      </div>

      {/* PRINT-ONLY VIEW: PRINT-OPTIMIZED MULTI-LABEL SHEET */}
      <div className="hidden print:block font-mono">
        <div className="text-center mb-6 pb-2 border-b-2 border-black">
          <div className="text-xl font-black uppercase">
            Factory Energy Autopilot • Industrial Equipment Labels
          </div>
          <div className="text-xs font-bold text-slate-600" suppressHydrationWarning>
            PCC Substation &bull; Energy Passport QR System &bull; Printed {printDate}
          </div>
        </div>

        {/* 2-column or 3-column Grid for physical label sticker sheets */}
        <div className="grid grid-cols-2 gap-6 p-4">
          {selectedAssets.map((asset) => {
            const destUrl = `${effectiveBaseUrl}/assets/${asset.asset_id}`
            return (
              <div
                key={asset.asset_id}
                className="border-2 border-black rounded-lg p-4 bg-white flex flex-col items-center text-center break-inside-avoid"
              >
                <div className="w-full border-b border-black pb-1 mb-2 text-left">
                  <div className="text-[9px] font-black uppercase text-slate-700">
                    FACTORY ENERGY AUTOPILOT
                  </div>
                  <div className="text-base font-black text-black uppercase leading-tight truncate">
                    {asset.name}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono font-black text-black mt-0.5">
                    <span>{asset.asset_id}</span>
                    <span>{asset.pcc_association || 'PCC-01'}</span>
                  </div>
                </div>

                <div className="my-1">
                  <QrCodeDisplay
                    url={destUrl}
                    assetId={asset.asset_id}
                    assetName={asset.name}
                    cellSize={5}
                    showControls={false}
                    showLabelBorder={false}
                    instructionText=""
                    isProduction={true}
                  />
                </div>

                <div className="w-full border-t border-black pt-1 mt-1">
                  <div className="text-[10px] font-black uppercase tracking-wider text-black">
                    {customInstruction}
                  </div>
                  <div className="text-[8px] font-mono text-slate-600 truncate mt-0.5">
                    {destUrl}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

    </div>
  )
}

export default function QrPrintCenterPage() {
  return (
    <React.Suspense fallback={<div className="p-12 text-center text-slate-500 font-mono font-bold">Loading QR Print Center...</div>}>
      <QrPrintCenterContent />
    </React.Suspense>
  )
}
