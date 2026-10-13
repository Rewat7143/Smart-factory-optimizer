"use client"
import React, { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { getApiBaseUrl } from '@/lib/config'

interface Asset {
  asset_id: string
  name: string
  equipment_type?: string
  manufacturer_model?: string
  location?: string
  rated_capacity_kw?: number
  rated_voltage_v?: number
  phase_config?: string
  pcc_association?: string
  meter_association?: string
  load_classification: string
  priority_order: number
  is_protected: number | boolean
  permitted_actions: string[]
  operating_schedule?: string
  is_archived: number | boolean
  telemetry_status?: string
  pcc_active_power_kw?: number
  pcc_power_factor?: number
  qr_url?: string
}

export default function AssetRegistryPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [selectedClassification, setSelectedClassification] = useState<string>('ALL')
  const [selectedPriority, setSelectedPriority] = useState<string>('ALL')
  const [selectedPcc, setSelectedPcc] = useState<string>('ALL')
  const [showArchived, setShowArchived] = useState<boolean>(false)

  // Pagination
  const [page, setPage] = useState<number>(1)
  const pageSize = 12

  // Archive confirmation modal state
  const [assetToArchive, setAssetToArchive] = useState<Asset | null>(null)
  const [archiving, setArchiving] = useState<boolean>(false)
  const [notification, setNotification] = useState<string | null>(null)

  const baseUrl = getApiBaseUrl()

  const fetchAssets = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (searchQuery) params.append('search', searchQuery)
      if (selectedClassification !== 'ALL') params.append('classification', selectedClassification)
      if (selectedPcc !== 'ALL') params.append('pcc', selectedPcc)
      if (showArchived) params.append('include_archived', 'true')
      params.append('limit', '100')

      const res = await fetch(`${baseUrl}/assets?${params.toString()}`)
      if (!res.ok) throw new Error(`HTTP Error ${res.status}: ${res.statusText}`)
      const data = await res.json()
      setAssets(data.assets || [])
      setTotalCount(data.total || 0)
      setError(null)
    } catch (e: any) {
      console.error('Failed to fetch assets:', e)
      setError(e.message || 'Failed to connect to backend asset registry.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAssets()
  }, [searchQuery, selectedClassification, selectedPcc, showArchived])

  // Filter by priority on client side
  const filteredAssets = useMemo(() => {
    return assets.filter((a) => {
      if (selectedPriority === 'PROTECTED') {
        return a.is_protected || a.load_classification === 'Mandatory'
      }
      if (selectedPriority === 'PRIORITY_1') return a.priority_order === 1
      if (selectedPriority === 'PRIORITY_2') return a.priority_order === 2
      if (selectedPriority === 'PRIORITY_3') return a.priority_order === 3
      return true
    })
  }, [assets, selectedPriority])

  // Paginated assets
  const paginatedAssets = useMemo(() => {
    const start = (page - 1) * pageSize
    return filteredAssets.slice(start, start + pageSize)
  }, [filteredAssets, page])

  const totalPages = Math.ceil(filteredAssets.length / pageSize) || 1

  // Handle Archive Action
  const handleArchiveConfirm = async () => {
    if (!assetToArchive) return
    setArchiving(true)
    try {
      const res = await fetch(`${baseUrl}/assets/${assetToArchive.asset_id}/archive`, {
        method: 'POST',
      })
      if (res.ok) {
        setNotification(`✓ Successfully archived ${assetToArchive.asset_id}`)
        setTimeout(() => setNotification(null), 4000)
        setAssetToArchive(null)
        await fetchAssets()
      } else {
        const err = await res.json()
        alert(`Failed to archive: ${err.detail || 'Server error'}`)
      }
    } catch (e: any) {
      alert(`Archive request failed: ${e.message}`)
    } finally {
      setArchiving(false)
    }
  }

  // Handle Unarchive Action
  const handleUnarchive = async (assetId: string) => {
    try {
      const res = await fetch(`${baseUrl}/assets/${assetId}/unarchive`, { method: 'POST' })
      if (res.ok) {
        setNotification(`✓ Restored ${assetId}`)
        setTimeout(() => setNotification(null), 4000)
        await fetchAssets()
      }
    } catch (e: any) {
      alert(`Unarchive failed: ${e.message}`)
    }
  }

  const getClassificationBadge = (cls: string, isProt: any) => {
    if (isProt || cls === 'Mandatory') {
      return {
        bg: 'bg-emerald-100 text-emerald-900 border-emerald-300',
        label: 'Mandatory • Protected',
      }
    }
    if (cls === 'Flexible') {
      return {
        bg: 'bg-indigo-100 text-indigo-900 border-indigo-300',
        label: 'Flexible Load',
      }
    }
    return {
      bg: 'bg-amber-100 text-amber-900 border-amber-300',
      label: 'Opportunistic',
    }
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-700 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-3">
          <span>✓</span>
          <span className="text-xs font-bold">{notification}</span>
        </div>
      )}

      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-slate-300 pb-4 gap-3 sm:gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">
            Asset Registry
          </h1>
          <p className="text-xs sm:text-sm font-semibold tracking-widest text-slate-500 uppercase mt-1">
            Centralized Industrial Load Management &amp; Energy Passport System
          </p>
        </div>

        {/* Action Buttons (Grid on mobile, flex on desktop) */}
        <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-2 w-full md:w-auto">
          <button
            onClick={() => fetchAssets()}
            className="bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-xs flex items-center justify-center gap-1.5 uppercase tracking-wider"
          >
            <span>🔄</span>
            <span>Refresh</span>
          </button>

          <Link
            href="/assets/qr-codes"
            className="bg-indigo-50 border border-indigo-300 hover:bg-indigo-100 text-indigo-950 font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-xs flex items-center justify-center gap-1.5 uppercase tracking-wider"
          >
            <span>🖨️</span>
            <span>QR Center</span>
          </Link>

          <Link
            href="/assets/new"
            className="col-span-2 sm:col-span-1 bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm flex items-center justify-center gap-1.5 uppercase tracking-wider"
          >
            <span>+</span>
            <span>Register Asset</span>
          </Link>
        </div>
      </div>

      {/* SUMMARY STATS STRIP */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4">
        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Total Loads
          </div>
          <div className="text-xl sm:text-2xl lg:text-3xl font-black text-slate-900 mt-1">
            {totalCount}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 font-medium mt-0.5">
            Database persistent
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Protected Base
          </div>
          <div className="text-xl sm:text-2xl lg:text-3xl font-black text-emerald-700 mt-1">
            {assets.filter((a) => a.is_protected || a.load_classification === 'Mandatory').length}
          </div>
          <div className="text-[10px] sm:text-xs text-emerald-600 font-medium mt-0.5">
            Shedding locked
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Flexible / Opp.
          </div>
          <div className="text-xl sm:text-2xl lg:text-3xl font-black text-indigo-700 mt-1">
            {assets.filter((a) => a.load_classification !== 'Mandatory' && !a.is_protected).length}
          </div>
          <div className="text-[10px] sm:text-xs text-indigo-600 font-medium mt-0.5">
            Curtailable
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500">
            Metering Mode
          </div>
          <div className="text-lg sm:text-xl lg:text-2xl font-black text-teal-800 mt-1">
            PCC AGGREGATE
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 font-medium mt-0.5 truncate" title="L&T WL4400 3-Phase Meter Linked">
            Modbus RTU • 91.0 kW Bus
          </div>
        </div>
      </div>

      {/* FILTER & SEARCH BAR */}
      <div className="bg-white border border-slate-300 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="w-full md:w-80 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setPage(1)
            }}
            placeholder="Search by asset ID, name, or area..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-xs font-bold text-slate-800 placeholder-slate-400 focus:outline-none focus:border-teal-600"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2 text-xs font-bold text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
          )}
        </div>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Classification */}
          <select
            value={selectedClassification}
            onChange={(e) => {
              setSelectedClassification(e.target.value)
              setPage(1)
            }}
            className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-800 outline-none"
          >
            <option value="ALL">All Classifications</option>
            <option value="Mandatory">Mandatory</option>
            <option value="Flexible">Flexible</option>
            <option value="Opportunistic">Opportunistic</option>
          </select>

          {/* Priority */}
          <select
            value={selectedPriority}
            onChange={(e) => {
              setSelectedPriority(e.target.value)
              setPage(1)
            }}
            className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-800 outline-none"
          >
            <option value="ALL">All Priorities</option>
            <option value="PROTECTED">Protected Only</option>
            <option value="PRIORITY_1">Priority 1 (High)</option>
            <option value="PRIORITY_2">Priority 2 (Medium)</option>
            <option value="PRIORITY_3">Priority 3 (Flexible)</option>
          </select>

          {/* PCC */}
          <select
            value={selectedPcc}
            onChange={(e) => {
              setSelectedPcc(e.target.value)
              setPage(1)
            }}
            className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-800 outline-none"
          >
            <option value="ALL">All PCC Buses</option>
            <option value="PCC-01">PCC-01</option>
            <option value="PCC-02">PCC-02</option>
          </select>

          {/* Show Archived Toggle */}
          <label className="flex items-center gap-1.5 text-xs font-bold text-slate-600 cursor-pointer ml-2">
            <input
              type="checkbox"
              checked={showArchived}
              onChange={(e) => {
                setShowArchived(e.target.checked)
                setPage(1)
              }}
              className="rounded text-teal-600"
            />
            <span>Show Archived</span>
          </label>
        </div>
      </div>

      {/* ERROR BANNER */}
      {error && (
        <div className="bg-rose-50 border-2 border-rose-300 rounded-xl p-4 text-xs font-bold text-rose-800">
          Error: {error}
        </div>
      )}

      {/* ASSET REGISTRY TABLE */}
      <div className="bg-white border border-slate-300 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 font-bold">
            Loading Asset Registry from Persistent Database...
          </div>
        ) : paginatedAssets.length === 0 ? (
          /* CLEAR EMPTY STATE */
          <div className="p-16 text-center space-y-4">
            <div className="text-4xl">📋</div>
            <div className="text-lg font-bold text-slate-900 uppercase">
              No Registered Assets Found
            </div>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              {searchQuery || selectedClassification !== 'ALL' || selectedPriority !== 'ALL'
                ? 'No assets match the active search filters. Try clearing filters.'
                : 'No factory loads have been registered yet. Add initial loads to enable QR passports and load optimization.'}
            </p>
            <div className="pt-2">
              <Link
                href="/assets/new"
                className="bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs px-5 py-2.5 rounded-xl uppercase tracking-wider inline-flex items-center gap-2"
              >
                <span>+</span>
                <span>Register First Load</span>
              </Link>
            </div>
          </div>
        ) : (
          <>
            {/* MOBILE CARDS VIEW (Optimized for smartphone screens < md) */}
            <div className="md:hidden divide-y divide-slate-100">
              {paginatedAssets.map((asset) => {
                const badge = getClassificationBadge(
                  asset.load_classification,
                  asset.is_protected
                )
                const isArchived = Boolean(asset.is_archived)

                return (
                  <div
                    key={asset.asset_id}
                    className={`p-3.5 space-y-2.5 bg-white ${
                      isArchived ? 'opacity-60 bg-slate-50/50' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 font-bold font-mono text-xs sm:text-sm text-slate-900 truncate">
                        <Link
                          href={`/assets/${asset.asset_id}`}
                          className="text-teal-700 hover:underline"
                        >
                          {asset.asset_id}
                        </Link>
                        <span>•</span>
                        <span className="truncate">{asset.name}</span>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider whitespace-nowrap border ${badge.bg}`}
                      >
                        {badge.label}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-[11px] bg-slate-50 p-2 rounded-lg border border-slate-200">
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Type</span>
                        <span className="font-bold text-slate-800 truncate block">
                          {asset.equipment_type && asset.equipment_type !== 'Not configured'
                            ? asset.equipment_type
                            : '---'}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Capacity</span>
                        <span className="font-bold text-slate-800">
                          {asset.rated_capacity_kw ? `${asset.rated_capacity_kw} kW` : '---'}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">PCC Bus</span>
                        <span className="font-bold text-slate-800">{asset.pcc_association || 'PCC-01'}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-1">
                      <span className="text-[10px] font-mono text-slate-500">
                        Priority {asset.priority_order}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <Link
                          href={`/assets/${asset.asset_id}`}
                          className="bg-slate-900 text-white text-[11px] font-bold px-2.5 py-1.5 rounded-lg"
                        >
                          Passport &rarr;
                        </Link>
                        <Link
                          href={`/assets/${asset.asset_id}/edit`}
                          className="bg-white border border-slate-300 text-slate-700 text-[11px] font-bold px-2 py-1.5 rounded-lg"
                        >
                          Edit
                        </Link>
                        <Link
                          href={`/assets/qr-codes?selected=${asset.asset_id}`}
                          className="bg-indigo-50 border border-indigo-200 text-indigo-900 text-[11px] font-bold px-2 py-1.5 rounded-lg"
                        >
                          QR
                        </Link>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* DESKTOP TABLE VIEW (Visible on >= md screens) */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse">
              <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider">
                <tr>
                  <th className="p-3.5">Asset ID</th>
                  <th className="p-3.5">Name / Model</th>
                  <th className="p-3.5">Equipment Type</th>
                  <th className="p-3.5">Rated Capacity</th>
                  <th className="p-3.5">Classification &amp; Priority</th>
                  <th className="p-3.5">PCC Bus</th>
                  <th className="p-3.5">Telemetry Status</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {paginatedAssets.map((asset) => {
                  const badge = getClassificationBadge(
                    asset.load_classification,
                    asset.is_protected
                  )
                  const isArchived = Boolean(asset.is_archived)

                  return (
                    <tr
                      key={asset.asset_id}
                      className={`hover:bg-slate-50 transition-colors ${
                        isArchived ? 'opacity-60 bg-slate-50/50' : ''
                      }`}
                    >
                      {/* Asset ID */}
                      <td className="p-3.5 font-bold font-mono text-slate-900 whitespace-nowrap">
                        <Link
                          href={`/assets/${asset.asset_id}`}
                          className="hover:text-teal-700 hover:underline inline-flex items-center gap-1"
                        >
                          <span>{asset.asset_id}</span>
                        </Link>
                        {isArchived && (
                          <span className="ml-2 text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded uppercase font-bold">
                            Archived
                          </span>
                        )}
                      </td>

                      {/* Name */}
                      <td className="p-3.5 font-bold text-slate-900">
                        <Link href={`/assets/${asset.asset_id}`} className="hover:text-teal-700">
                          {asset.name}
                        </Link>
                        {asset.manufacturer_model && asset.manufacturer_model !== 'Not configured' && (
                          <div className="text-[11px] font-normal text-slate-500 mt-0.5">
                            {asset.manufacturer_model}
                          </div>
                        )}
                      </td>

                      {/* Equipment Type */}
                      <td className="p-3.5 text-slate-700 whitespace-nowrap">
                        {asset.equipment_type === 'Not configured' ? (
                          <span className="text-slate-400 italic">Not configured</span>
                        ) : (
                          asset.equipment_type
                        )}
                      </td>

                      {/* Rated Capacity */}
                      <td className="p-3.5 font-bold whitespace-nowrap">
                        {asset.rated_capacity_kw !== null && asset.rated_capacity_kw !== undefined ? (
                          <span className="text-slate-900 font-mono">
                            {asset.rated_capacity_kw.toFixed(1)} kW
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">Not configured</span>
                        )}
                      </td>

                      {/* Classification & Priority */}
                      <td className="p-3.5 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${badge.bg}`}
                          >
                            {badge.label}
                          </span>
                          <span className="text-[11px] font-mono text-slate-500">
                            P{asset.priority_order}
                          </span>
                        </div>
                      </td>

                      {/* PCC Association */}
                      <td className="p-3.5 font-mono text-slate-700 whitespace-nowrap">
                        {asset.pcc_association || 'PCC-01'}
                      </td>

                      {/* Telemetry Status */}
                      <td className="p-3.5 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isArchived ? 'bg-slate-400' : 'bg-emerald-500'
                            }`}
                          ></span>
                          <span>{isArchived ? 'Offline' : 'Online (PCC)'}</span>
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="p-3.5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          <Link
                            href={`/assets/${asset.asset_id}`}
                            className="bg-slate-100 hover:bg-slate-200 text-slate-800 px-2.5 py-1 rounded-lg text-xs font-bold"
                            title="Open Energy Passport"
                          >
                            Details
                          </Link>

                          <Link
                            href={`/assets/${asset.asset_id}/edit`}
                            className="bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg text-xs font-bold"
                            title="Edit metadata"
                          >
                            Edit
                          </Link>

                          <Link
                            href={`/assets/qr-codes?selected=${asset.asset_id}`}
                            className="bg-indigo-50 hover:bg-indigo-100 text-indigo-900 border border-indigo-200 px-2 py-1 rounded-lg text-xs font-bold"
                            title="View / Print QR Code"
                          >
                            QR
                          </Link>

                          {isArchived ? (
                            <button
                              onClick={() => handleUnarchive(asset.asset_id)}
                              className="bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 px-2 py-1 rounded-lg text-xs font-bold"
                            >
                              Restore
                            </button>
                          ) : (
                            <button
                              onClick={() => setAssetToArchive(asset)}
                              className="text-slate-400 hover:text-rose-600 px-2 py-1 text-xs font-bold"
                              title="Archive asset"
                            >
                              Archive
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

        {/* Table Footer with Pagination */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs font-bold text-slate-600 gap-3">
          <div>
            Showing {paginatedAssets.length} of {filteredAssets.length} loads (Total in DB: {totalCount})
          </div>

          {totalPages > 1 && (
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-2.5 py-1 rounded bg-white border border-slate-300 disabled:opacity-40"
              >
                &larr; Prev
              </button>
              <span className="px-2">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-2.5 py-1 rounded bg-white border border-slate-300 disabled:opacity-40"
              >
                Next &rarr;
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ARCHIVE CONFIRMATION MODAL */}
      {assetToArchive && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-300 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="text-lg font-bold text-slate-900 uppercase">
                Archive Asset Confirmation
              </h3>
              <button
                onClick={() => setAssetToArchive(null)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-700">
              <p>
                Are you sure you want to archive asset{' '}
                <strong className="text-slate-900 font-mono">{assetToArchive.asset_id}</strong> (
                {assetToArchive.name})?
              </p>
              <div className="bg-amber-50 border border-amber-300 rounded-lg p-3 text-[11px] text-amber-900 space-y-1">
                <div className="font-bold">⚠️ Archiving Policy:</div>
                <div>• Historical telemetry and audit records remain safely preserved in database.</div>
                <div>• Previously printed QR codes will display an "Archived" badge when scanned.</div>
                <div>• Asset can be restored at any time.</div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 flex items-center justify-end gap-2">
              <button
                onClick={() => setAssetToArchive(null)}
                className="px-4 py-2 rounded-lg text-xs font-bold uppercase text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={handleArchiveConfirm}
                disabled={archiving}
                className="px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-rose-700 hover:bg-rose-800 text-white shadow-sm disabled:opacity-50"
              >
                {archiving ? 'Archiving...' : 'Confirm Archive'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
