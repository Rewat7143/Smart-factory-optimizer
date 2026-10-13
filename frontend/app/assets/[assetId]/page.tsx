"use client"
import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { getApiBaseUrl } from '@/lib/config'
import QrCodeDisplay from '@/components/QrCodeDisplay'

export default function AssetDetailsPage() {
  const params = useParams()
  const rawId = (params?.assetId as string) || ''
  const assetId = decodeURIComponent(rawId).trim().toUpperCase()

  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState<boolean>(false)

  const baseUrl = getApiBaseUrl()

  const fetchDetails = async () => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 6000)

    try {
      const res = await fetch(`${baseUrl}/assets/${assetId}`, {
        signal: controller.signal
      })
      clearTimeout(timeoutId)

      if (!res.ok) {
        if (res.status === 404) throw new Error(`Asset '${assetId}' not found in registry.`)
        throw new Error(`Server error (${res.status})`)
      }
      const json = await res.json()
      setData(json)
      setError(null)
    } catch (e: any) {
      clearTimeout(timeoutId)
      if (!data) {
        setError(e.message || 'Failed to fetch asset Energy Passport.')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!assetId) return
    fetchDetails()
    const timer = setInterval(fetchDetails, 3000)
    return () => clearInterval(timer)
  }, [assetId])

  const copyUrl = () => {
    if (typeof window !== 'undefined' && navigator?.clipboard) {
      navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (loading && !data) {
    return (
      <div className="max-w-[1400px] mx-auto p-12 text-center text-slate-500 font-bold font-mono">
        <div className="w-8 h-8 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading Energy Passport for {assetId}...
      </div>
    )
  }

  if (error || !data) {
    const isNotFound = error?.toLowerCase().includes('not found') || error?.includes('404')

    return (
      <div className="max-w-[800px] mx-auto p-8 sm:p-12 text-center font-mono space-y-4">
        <div className="text-4xl">{isNotFound ? '📋' : '⚡'}</div>
        <h2 className="text-xl sm:text-2xl font-black text-slate-800 uppercase">
          {isNotFound ? 'Asset Not Found' : 'Telemetry Link Connecting'}
        </h2>
        <p className="text-xs text-slate-600 max-w-md mx-auto">
          {isNotFound
            ? `The requested identifier ${assetId} does not exist in the active asset database.`
            : (error || 'Establishing connection to telemetry stream...')}
        </p>
        <div className="pt-4 flex flex-wrap items-center justify-center gap-3">
          {!isNotFound && (
            <button
              onClick={() => {
                setLoading(true)
                setError(null)
                fetchDetails()
              }}
              className="bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs px-5 py-2.5 rounded-xl uppercase tracking-wider"
            >
              🔄 Retry Connection
            </button>
          )}
          <Link
            href="/assets"
            className="bg-slate-900 text-white font-bold text-xs px-5 py-2.5 rounded-xl uppercase tracking-wider"
          >
            &larr; View Asset Registry
          </Link>
        </div>
      </div>
    )
  }

  const { asset, qr_url, is_production_url, telemetry, energy_stats, ai_insights, control_actions } = data
  const isArchived = Boolean(asset.is_archived)
  const isProtected = Boolean(asset.is_protected) || asset.load_classification === 'Mandatory'
  const effectiveQrUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/assets/${asset.asset_id}`
    : (qr_url || `http://localhost:3000/assets/${asset.asset_id}`)

  return (
    <div className="max-w-[1400px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* ARCHIVED WARNING BANNER */}
      {isArchived && (
        <div className="bg-slate-900 text-white p-3 sm:p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 text-xs font-bold">
            <span className="text-xl">⚠️</span>
            <div>
              <span className="text-amber-400 uppercase font-black">ARCHIVED LOAD PROFILE:</span>{' '}
              This asset is archived. Historical telemetry and audit records remain permanently preserved.
            </div>
          </div>
          <span className="text-[10px] sm:text-[11px] font-mono text-slate-400">
            Archived at {asset.archived_at || 'Recent'}
          </span>
        </div>
      )}

      {/* HEADER SECTION (ENERGY PASSPORT) */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-slate-300 pb-4 gap-3 sm:gap-4">
        <div className="w-full md:w-auto">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5">
            <span className="bg-slate-900 text-white font-mono text-xs font-black px-2.5 py-0.5 rounded uppercase">
              {asset.asset_id}
            </span>
            <span
              className={`text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider border ${
                isProtected
                  ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                  : 'bg-indigo-100 text-indigo-900 border-indigo-300'
              }`}
            >
              {isProtected ? 'Mandatory • Protected' : `${asset.load_classification} Load`}
            </span>
            <span className="text-[10px] font-mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-300">
              Priority {asset.priority_order}
            </span>
            {asset.location && asset.location !== 'Not configured' && (
              <span className="text-[10px] text-slate-500 font-bold">
                📍 {asset.location}
              </span>
            )}
          </div>

          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 uppercase break-words">
            {asset.name}
          </h1>

          <p className="text-[11px] sm:text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">
            Permanent Energy Passport &bull; Point of Common Coupling {asset.pcc_association || 'PCC-01'}
          </p>
        </div>

        {/* Quick Navigation Action Buttons (Grid on mobile, flex on desktop) */}
        <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-2 w-full md:w-auto">
          <Link
            href={`/assets/${asset.asset_id}/edit`}
            className="flex items-center justify-center text-center bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-xs"
          >
            ✏️ Edit Profile
          </Link>

          <Link
            href={`/assets/${asset.asset_id}/control`}
            className="flex items-center justify-center text-center bg-teal-50 border border-teal-300 hover:bg-teal-100 text-teal-950 font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-xs"
          >
            ⚙️ Controls
          </Link>

          <Link
            href={`/assets/${asset.asset_id}/history`}
            className="flex items-center justify-center text-center bg-indigo-50 border border-indigo-300 hover:bg-indigo-100 text-indigo-950 font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-xs"
          >
            📈 History
          </Link>

          <Link
            href={`/assets/qr-codes?selected=${asset.asset_id}`}
            className="flex items-center justify-center text-center bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs px-3 py-2.5 rounded-xl transition-all shadow-sm"
          >
            🖨️ QR Label
          </Link>
        </div>
      </div>

      {/* TRANSPARENT METERING DISCLOSURE BANNER */}
      <div className="bg-slate-100 border border-slate-300 rounded-xl p-3 sm:p-3.5 text-xs text-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-start sm:items-center gap-2">
          <span className="text-base">ℹ️</span>
          <span className="text-[11px] sm:text-xs">
            <strong>Metering Disclosure:</strong> Single aggregate meter installed at Point of Common Coupling ({asset.meter_association || 'RPi-METER-01'}). Machine-level values are derived via virtual energy balance disaggregation.
          </span>
        </div>
        <div className="text-[10px] sm:text-[11px] font-mono text-slate-500 whitespace-nowrap">
          Fresh telemetry • {telemetry.data_freshness_seconds}s ago
        </div>
      </div>

      {/* TOP LIVE TELEMETRY RIBBON (MEASURED AT PCC BUS) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            PCC Power
          </div>
          <div className="text-xl sm:text-2xl font-black text-teal-700 mt-0.5 sm:mt-1">
            {telemetry.pcc_active_power_kw.toFixed(1)}{' '}
            <span className="text-xs font-bold text-slate-500">kW</span>
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5">Aggregate Bus</div>
        </div>

        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Phase Voltage
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-800 mt-0.5 sm:mt-1">
            {telemetry.pcc_voltage_v.toFixed(1)}{' '}
            <span className="text-xs font-bold text-slate-500">V</span>
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5">Line-to-Neutral</div>
        </div>

        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Line Current
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-800 mt-0.5 sm:mt-1">
            {telemetry.pcc_current_a.toFixed(1)}{' '}
            <span className="text-xs font-bold text-slate-500">A</span>
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5">Total Incomer</div>
        </div>

        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Power Factor
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-800 mt-0.5 sm:mt-1">
            {telemetry.pcc_power_factor.toFixed(3)}
          </div>
          <div className="text-[9px] sm:text-[10px] text-emerald-600 mt-0.5 font-bold">Optimal Grid</div>
        </div>

        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Grid Frequency
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-800 mt-0.5 sm:mt-1">
            {telemetry.pcc_frequency_hz.toFixed(2)}{' '}
            <span className="text-xs font-bold text-slate-500">Hz</span>
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5">50 Hz Standard</div>
        </div>

        <div className="bg-white border border-slate-300 p-3 sm:p-4 rounded-xl shadow-xs col-span-2 sm:col-span-1">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Operating State
          </div>
          <div className="text-lg sm:text-xl font-black text-emerald-700 mt-0.5 sm:mt-1">
            {isArchived ? 'ARCHIVED' : 'RUNNING'}
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5">Auto-detected</div>
        </div>
      </div>

      {/* TWO COLUMN MAIN CONTENT: SPECIFICATIONS & QR PASSPORT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        
        {/* LEFT 2 COLS: ENERGY STATS & TECHNICAL PROFILE */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Energy Consumption Estimates */}
          <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-3 mb-4 gap-2">
              <div>
                <h3 className="text-sm sm:text-base font-bold uppercase tracking-wider text-slate-900">
                  Energy Consumption &amp; Demand
                </h3>
                <div className="text-[11px] sm:text-xs text-slate-500 font-medium">
                  {energy_stats.calculation_method}
                </div>
              </div>
              <span className="self-start sm:self-auto text-xs bg-teal-50 text-teal-800 font-bold px-2 py-0.5 rounded border border-teal-200">
                Tariff: ₹7.50 / kWh
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-4 text-center">
              <div className="bg-slate-50 p-2.5 sm:p-3.5 rounded-xl border border-slate-200">
                <div className="text-[9px] sm:text-[10px] font-bold uppercase text-slate-500">Today</div>
                <div className="text-lg sm:text-2xl font-black text-slate-900 mt-1">
                  {energy_stats.energy_today_kwh}{' '}
                  <span className="text-[10px] sm:text-xs font-bold text-slate-500">kWh</span>
                </div>
                <div className="text-[11px] sm:text-xs font-bold text-emerald-700 mt-0.5" suppressHydrationWarning>
                  ₹{Math.round(energy_stats.energy_today_kwh * 7.5).toLocaleString()}
                </div>
              </div>

              <div className="bg-slate-50 p-2.5 sm:p-3.5 rounded-xl border border-slate-200">
                <div className="text-[9px] sm:text-[10px] font-bold uppercase text-slate-500">This Month</div>
                <div className="text-lg sm:text-2xl font-black text-slate-900 mt-1">
                  {energy_stats.energy_month_kwh}{' '}
                  <span className="text-[10px] sm:text-xs font-bold text-slate-500">kWh</span>
                </div>
                <div className="text-[11px] sm:text-xs font-bold text-slate-700 mt-0.5" suppressHydrationWarning>
                  ₹{Math.round(energy_stats.energy_month_kwh * 7.5).toLocaleString()}
                </div>
              </div>

              <div className="bg-slate-50 p-2.5 sm:p-3.5 rounded-xl border border-slate-200">
                <div className="text-[9px] sm:text-[10px] font-bold uppercase text-slate-500">This Year</div>
                <div className="text-lg sm:text-2xl font-black text-slate-900 mt-1">
                  {energy_stats.energy_year_kwh}{' '}
                  <span className="text-[10px] sm:text-xs font-bold text-slate-500">kWh</span>
                </div>
                <div className="text-[11px] sm:text-xs font-bold text-slate-700 mt-0.5" suppressHydrationWarning>
                  ₹{Math.round(energy_stats.energy_year_kwh * 7.5).toLocaleString()}
                </div>
              </div>

              <div className="bg-slate-50 p-2.5 sm:p-3.5 rounded-xl border border-slate-200">
                <div className="text-[9px] sm:text-[10px] font-bold uppercase text-slate-500">Peak Demand</div>
                <div className="text-lg sm:text-2xl font-black text-slate-900 mt-1">
                  {energy_stats.peak_demand_kw ? `${energy_stats.peak_demand_kw} kW` : '---'}
                </div>
                <div className="text-[9px] sm:text-[10px] text-slate-500 mt-0.5">
                  {energy_stats.peak_utilization_window}
                </div>
              </div>
            </div>
          </div>

          {/* AI Insights & Optimization Recommendations */}
          <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm space-y-3">
            <h3 className="text-sm sm:text-base font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2">
              Autopilot Insights &amp; Operating Envelope
            </h3>

            {ai_insights.length > 0 ? (
              ai_insights.map((ins: any, i: number) => (
                <div
                  key={i}
                  className={`p-3.5 rounded-xl border text-xs font-medium ${
                    ins.level === 'INFO'
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
                      : 'bg-indigo-50 border-indigo-200 text-indigo-950'
                  }`}
                >
                  <div className="font-bold flex items-center gap-1.5 uppercase tracking-wide">
                    <span>{ins.level === 'INFO' ? '🛡️' : '💡'}</span>
                    <span>{ins.title}</span>
                  </div>
                  <div className="mt-1 text-slate-700">{ins.message}</div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-500 italic p-2">
                No active anomaly alerts. Operating within normal electrical envelope.
              </div>
            )}
          </div>

          {/* Full Technical Profile Specifications */}
          <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm">
            <h3 className="text-sm sm:text-base font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-4">
              Technical Specifications &amp; Constraints
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 text-xs">
              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Equipment Type</span>
                <span className="font-bold text-slate-900">
                  {asset.equipment_type || 'Not configured'}
                </span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Manufacturer / Model</span>
                <span className="font-bold text-slate-900">
                  {asset.manufacturer_model || 'Not configured'}
                </span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Rated Capacity</span>
                <span className="font-bold text-slate-900">
                  {asset.rated_capacity_kw ? `${asset.rated_capacity_kw} kW` : 'Not configured'}
                </span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Rated Voltage</span>
                <span className="font-bold text-slate-900">
                  {asset.rated_voltage_v ? `${asset.rated_voltage_v} V` : 'Not configured'}
                </span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Phase Config</span>
                <span className="font-bold text-slate-900">{asset.phase_config || 'Not configured'}</span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">PCC Bus Association</span>
                <span className="font-bold text-slate-900">{asset.pcc_association || 'PCC-01'}</span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Operating Schedule</span>
                <span className="font-bold text-slate-900">{asset.operating_schedule || '24/7'}</span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Min Runtime / Off-time</span>
                <span className="font-bold text-slate-900">
                  {asset.min_runtime_minutes || 15}m run / {asset.min_offtime_minutes || 15}m off
                </span>
              </div>

              <div className="bg-slate-50 sm:bg-transparent p-2.5 sm:p-0 rounded-lg sm:rounded-none">
                <span className="text-slate-400 uppercase text-[10px] block font-bold">Restart Delay</span>
                <span className="font-bold text-slate-900">{asset.restart_delay_minutes || 5} mins</span>
              </div>
            </div>

            {/* Constraints & Maintenance Notes */}
            <div className="mt-4 pt-4 border-t border-slate-200 space-y-3 text-xs">
              <div>
                <span className="text-slate-500 uppercase text-[10px] font-bold block">Production Constraints</span>
                <p className="text-slate-800 font-medium mt-0.5 break-words">
                  {asset.production_constraints || 'Not configured'}
                </p>
              </div>

              <div>
                <span className="text-slate-500 uppercase text-[10px] font-bold block">Operator Notes</span>
                <p className="text-slate-800 font-medium mt-0.5 break-words">
                  {asset.operator_notes || 'Not configured'}
                </p>
              </div>

              <div>
                <span className="text-slate-500 uppercase text-[10px] font-bold block">Maintenance Notes</span>
                <p className="text-slate-800 font-medium mt-0.5 break-words">
                  {asset.maintenance_notes || 'Not configured'}
                </p>
              </div>
            </div>
          </div>

          {/* Recent Approved / Rejected Actions */}
          <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-2 mb-3 gap-1">
              <h3 className="text-sm sm:text-base font-bold uppercase tracking-wider text-slate-900">
                Recent Optimization Actions &amp; Audit Trail
              </h3>
              <Link
                href={`/assets/${asset.asset_id}/control`}
                className="text-xs text-teal-700 font-bold hover:underline"
              >
                Open Control Center &rarr;
              </Link>
            </div>

            {control_actions && control_actions.length > 0 ? (
              <div className="space-y-2 text-xs">
                {control_actions.slice(0, 3).map((act: any) => (
                  <div
                    key={act.action_id}
                    className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                  >
                    <div>
                      <div className="font-bold font-mono text-slate-900">{act.action_id}</div>
                      <div className="text-slate-600 font-medium mt-0.5 text-[11px] sm:text-xs">
                        {act.recommendation_reason || act.action_type}
                      </div>
                    </div>
                    <span
                      className={`self-start sm:self-auto px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider whitespace-nowrap ${
                        act.status === 'APPROVED'
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          : act.status === 'REJECTED'
                          ? 'bg-rose-100 text-rose-800 border border-rose-300'
                          : 'bg-amber-100 text-amber-800 border border-amber-300'
                      }`}
                    >
                      {act.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-slate-500 italic p-2">
                No recent control actions recorded for this asset.
              </div>
            )}
          </div>

        </div>

        {/* RIGHT COL: EMBEDDED QR CODE PASSPORT & ACTIONS */}
        <div className="space-y-4 sm:space-y-6">
          <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm flex flex-col items-center">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 text-center">
              Permanent QR Passport
            </div>

            <QrCodeDisplay
              url={effectiveQrUrl}
              assetId={asset.asset_id}
              assetName={asset.name}
              equipmentType={asset.equipment_type}
              pcc={asset.pcc_association}
              cellSize={6}
              showControls={true}
              showLabelBorder={true}
              instructionText="Scan for Energy Passport"
              isProduction={is_production_url}
            />

            <div className="mt-4 w-full pt-3 border-t border-slate-200 text-center">
              <button
                onClick={copyUrl}
                className="w-full bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs py-2.5 rounded-lg transition-all"
              >
                {copied ? '✓ Copied URL!' : '🔗 Copy Destination Link'}
              </button>
            </div>
          </div>

          {/* Quick Context Links */}
          <div className="bg-slate-50 border border-slate-300 rounded-xl p-4 text-xs font-bold space-y-2">
            <div className="text-[11px] text-slate-500 uppercase tracking-widest mb-1">
              Context Actions
            </div>
            <Link
              href={`/assets/${asset.asset_id}/history`}
              className="block p-2.5 rounded-lg bg-white border border-slate-200 hover:border-slate-400 text-slate-800 transition-all"
            >
              📊 Inspect 24h &amp; 7d Energy History
            </Link>
            <Link
              href={`/assets/${asset.asset_id}/control`}
              className="block p-2.5 rounded-lg bg-white border border-slate-200 hover:border-slate-400 text-slate-800 transition-all"
            >
              🛡️ Authorize Pending Curtailment
            </Link>
            <Link
              href={`/assets/qr-codes?selected=${asset.asset_id}`}
              className="block p-2.5 rounded-lg bg-white border border-slate-200 hover:border-slate-400 text-slate-800 transition-all"
            >
              🖨️ Open Label Print Center
            </Link>
            <Link
              href="/assets"
              className="block p-2.5 rounded-lg bg-white border border-slate-200 hover:border-slate-400 text-slate-800 transition-all"
            >
              &larr; Back to Asset Registry
            </Link>
          </div>
        </div>

      </div>

    </div>
  )
}
