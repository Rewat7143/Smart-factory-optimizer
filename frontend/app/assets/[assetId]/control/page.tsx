"use client"
import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { getApiBaseUrl } from '@/lib/config'

interface ControlAction {
  action_id: string
  asset_id: string
  action_type: string
  recommendation_reason: string
  current_demand_kw: number
  threshold_kw: number
  expected_impact_kw: number
  production_implications: string
  status: string
  operator_id?: string
  operator_notes?: string
  created_at: string
  decided_at?: string
  physical_verification_status: string
}

export default function AssetControlPage() {
  const params = useParams()
  const rawId = (params?.assetId as string) || ''
  const assetId = decodeURIComponent(rawId).trim().toUpperCase()

  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [operatorBadge, setOperatorBadge] = useState<string>('OP-1049')
  const [operatorNote, setOperatorNote] = useState<string>('')
  const [processingId, setProcessingId] = useState<string | null>(null)
  const [notification, setNotification] = useState<string | null>(null)

  const baseUrl = getApiBaseUrl()

  const fetchControlData = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${baseUrl}/assets/${assetId}/control`)
      if (!res.ok) throw new Error(`Asset control data not available (${res.status})`)
      const json = await res.json()
      setData(json)
      setError(null)
    } catch (e: any) {
      setError(e.message || 'Failed to fetch control state.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!assetId) return
    fetchControlData()
    const timer = setInterval(fetchControlData, 4000)
    return () => clearInterval(timer)
  }, [assetId])

  const handleDecision = async (actionId: string, decision: 'APPROVE' | 'REJECT') => {
    if (!operatorBadge.trim()) {
      alert('Operator Badge / ID is required to authorize or reject an intervention.')
      return
    }

    setProcessingId(actionId)
    try {
      const res = await fetch(`${baseUrl}/assets/${assetId}/control/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_id: actionId,
          decision: decision,
          operator_id: operatorBadge.trim(),
          operator_notes: operatorNote.trim() || undefined
        })
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `Server rejected decision (${res.status})`)
      }

      setNotification(`✓ Recommendation ${actionId} successfully ${decision}D. Audit log updated.`)
      setOperatorNote('')
      setTimeout(() => setNotification(null), 4000)
      await fetchControlData()
    } catch (e: any) {
      alert(`Action Failed: ${e.message}`)
    } finally {
      setProcessingId(null)
    }
  }

  if (loading && !data) {
    return (
      <div className="max-w-[1200px] mx-auto p-12 text-center text-slate-500 font-bold font-mono">
        Loading control &amp; approval interface for {assetId}...
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-[800px] mx-auto p-12 text-center font-mono space-y-4">
        <div className="text-3xl">⚠️</div>
        <h2 className="text-xl font-black text-slate-900 uppercase">
          Control Center Unavailable
        </h2>
        <p className="text-xs text-slate-500">{error || 'Asset not found.'}</p>
        <Link
          href={`/assets/${assetId}`}
          className="inline-block bg-slate-900 text-white font-bold text-xs px-4 py-2 rounded-xl uppercase"
        >
          &larr; Return to Asset Details
        </Link>
      </div>
    )
  }

  const {
    name,
    is_protected,
    load_classification,
    permitted_actions,
    current_demand_kw,
    contract_threshold_kw,
    pending_recommendations,
    audit_history,
    hardware_status,
    control_warning
  } = data

  const isProtectedOrMandatory = is_protected || load_classification === 'Mandatory'

  return (
    <div className="max-w-[1400px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-4 sm:top-6 right-4 sm:right-6 left-4 sm:left-auto max-w-md z-50 bg-emerald-700 text-white px-4 sm:px-5 py-3 rounded-xl shadow-xl flex items-center gap-3">
          <span className="text-base">✓</span>
          <span className="text-xs font-bold">{notification}</span>
        </div>
      )}

      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-slate-300 pb-4 gap-3 sm:gap-4">
        <div className="w-full md:w-auto">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5">
            <span className="bg-slate-900 text-white font-mono text-xs font-black px-2.5 py-0.5 rounded uppercase">
              {assetId}
            </span>
            <span
              className={`text-[10px] font-black px-2.5 py-0.5 rounded uppercase tracking-wider border ${
                isProtectedOrMandatory
                  ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                  : 'bg-indigo-100 text-indigo-900 border-indigo-300'
              }`}
            >
              {isProtectedOrMandatory ? 'Protected Load' : 'Flexible Load'}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 uppercase break-words">
            Asset Control &amp; Approvals
          </h1>
          <p className="text-[11px] sm:text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">
            Authorized Intervention Interface &bull; Two-Person Rule Compliant
          </p>
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Link
            href={`/assets/${assetId}`}
            className="w-full md:w-auto flex items-center justify-center text-center bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3.5 py-2.5 rounded-xl transition-all shadow-xs"
          >
            &larr; View Energy Passport
          </Link>
        </div>
      </div>

      {/* SAFETY & AUTHORIZATION BANNER */}
      <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-3.5 sm:p-4 text-xs font-bold text-amber-950 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <span className="text-xl shrink-0">🛡️</span>
          <div>
            <div className="uppercase tracking-wider font-black">
              Physical Safety &amp; Access Control Policy:
            </div>
            <p className="text-amber-900 font-medium mt-0.5 text-[11px] sm:text-xs">
              {control_warning} No relay signal is transmitted until explicitly approved by an authorized plant operator.
            </p>
          </div>
        </div>
        <div className="text-[10px] sm:text-[11px] font-mono bg-amber-100 px-3 py-1 rounded-lg border border-amber-300 whitespace-nowrap self-start md:self-auto">
          {hardware_status}
        </div>
      </div>

      {/* OPERATOR DEMAND CONTEXT RIBBON */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-4">
        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500 truncate">
            Current Factory Demand
          </div>
          <div className="text-xl sm:text-2xl lg:text-3xl font-black text-teal-700 mt-1">
            {current_demand_kw.toFixed(1)}{' '}
            <span className="text-[10px] sm:text-xs font-bold text-slate-500">kW</span>
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 font-medium mt-0.5 truncate">
            PCC Incomer Meter
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500 truncate">
            Contract CMD Limit
          </div>
          <div className="text-xl sm:text-2xl lg:text-3xl font-black text-rose-700 mt-1">
            {contract_threshold_kw.toFixed(1)}{' '}
            <span className="text-[10px] sm:text-xs font-bold text-slate-500">kW</span>
          </div>
          <div className="text-[10px] sm:text-xs text-rose-600 font-medium mt-0.5 truncate">
            Ceiling Threshold
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500 truncate">
            Protection Policy
          </div>
          <div className="text-base sm:text-xl lg:text-2xl font-black text-slate-900 mt-1 truncate">
            {isProtectedOrMandatory ? 'LOCKED' : 'FLEXIBLE'}
          </div>
          <div className="text-[10px] sm:text-xs text-slate-500 font-medium mt-0.5 truncate">
            {isProtectedOrMandatory ? 'Mandatory Base' : 'Curtailable'}
          </div>
        </div>

        <div className="bg-white border border-slate-300 rounded-xl p-3 sm:p-4 shadow-sm">
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500 truncate">
            Operator Badge Session
          </div>
          <div className="mt-1">
            <input
              type="text"
              value={operatorBadge}
              onChange={(e) => setOperatorBadge(e.target.value.toUpperCase())}
              placeholder="Operator Badge ID"
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2 sm:px-2.5 py-1 text-xs font-mono font-bold text-slate-900 outline-none focus:border-teal-600"
            />
          </div>
          <div className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5 truncate">Logged in audit trail</div>
        </div>
      </div>

      {/* PERMITTED ACTIONS MATRIX */}
      <div className="bg-white border border-slate-300 rounded-xl p-3.5 sm:p-4 shadow-sm">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
          Permitted Engineering Actions For This Asset
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {permitted_actions.map((act: string) => (
            <span
              key={act}
              className="bg-slate-100 border border-slate-300 text-slate-800 font-bold px-3 py-1 rounded-lg uppercase tracking-wider"
            >
              ✓ {act.replace('_', ' ')}
            </span>
          ))}
          {permitted_actions.length === 0 && (
            <span className="text-slate-400 italic">No automated actions permitted (Monitor Only).</span>
          )}
        </div>
      </div>

      {/* PENDING RECOMMENDATIONS SECTION */}
      <div className="bg-white border border-slate-300 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-base font-bold uppercase tracking-wider text-slate-900">
              Active Optimization Recommendations Awaiting Operator Approval
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              Review rationale and production constraints before executing intervention
            </p>
          </div>
          <span className="bg-amber-100 text-amber-900 border border-amber-300 text-xs font-black px-2.5 py-1 rounded-lg">
            {pending_recommendations.length} Pending
          </span>
        </div>

        {pending_recommendations.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <div className="text-2xl">✓</div>
            <div className="text-xs font-bold uppercase text-slate-700">
              No Pending Interventions
            </div>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Current factory demand is operating safely within contract limits. Autopilot will flag recommendations when peak shaving or ToD shifting is required.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {pending_recommendations.map((rec: ControlAction) => (
              <div
                key={rec.action_id}
                className="bg-slate-50 border-2 border-slate-200 rounded-xl p-5 space-y-4 transition-all hover:border-slate-300"
              >
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-200 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="bg-slate-900 text-white font-mono text-xs font-black px-2 py-0.5 rounded">
                      {rec.action_id}
                    </span>
                    <span className="text-xs font-black uppercase text-teal-800">
                      {rec.action_type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">
                    Created: {new Date(rec.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="md:col-span-2 space-y-2">
                    <div>
                      <span className="text-slate-400 uppercase text-[10px] font-bold block">
                        Optimization Rationale
                      </span>
                      <p className="text-slate-800 font-bold mt-0.5">
                        {rec.recommendation_reason}
                      </p>
                    </div>

                    <div>
                      <span className="text-slate-400 uppercase text-[10px] font-bold block">
                        Production Implications
                      </span>
                      <p className="text-slate-700 font-medium mt-0.5">
                        {rec.production_implications}
                      </p>
                    </div>
                  </div>

                  <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-2 text-center flex flex-col justify-center">
                    <div className="text-[10px] font-bold uppercase text-slate-500">
                      Expected Headroom Impact
                    </div>
                    <div className="text-2xl font-black text-emerald-700">
                      -{rec.expected_impact_kw.toFixed(1)}{' '}
                      <span className="text-xs font-bold text-slate-500">kW</span>
                    </div>
                    <div className="text-[10px] text-slate-400">Demand Relief</div>
                  </div>
                </div>

                {/* Operator Note & Action Buttons */}
                <div className="pt-3 border-t border-slate-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                  <div className="w-full sm:w-80">
                    <input
                      type="text"
                      placeholder="Optional operator authorization note..."
                      value={operatorNote}
                      onChange={(e) => setOperatorNote(e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 outline-none focus:border-teal-600"
                    />
                  </div>

                  <div className="grid grid-cols-2 sm:flex items-center gap-2 w-full sm:w-auto">
                    <button
                      onClick={() => handleDecision(rec.action_id, 'REJECT')}
                      disabled={processingId === rec.action_id}
                      className="min-h-[44px] bg-white border-2 border-rose-300 hover:bg-rose-50 text-rose-800 font-bold text-xs px-4 py-2 rounded-xl uppercase tracking-wider transition-all disabled:opacity-50 flex items-center justify-center text-center"
                    >
                      {processingId === rec.action_id ? 'Processing...' : '✕ Reject'}
                    </button>

                    <button
                      onClick={() => handleDecision(rec.action_id, 'APPROVE')}
                      disabled={processingId === rec.action_id || isProtectedOrMandatory}
                      className={`min-h-[44px] text-white font-bold text-xs px-5 py-2 rounded-xl uppercase tracking-wider transition-all shadow-sm flex items-center justify-center text-center ${
                        isProtectedOrMandatory
                          ? 'bg-slate-400 cursor-not-allowed'
                          : 'bg-teal-700 hover:bg-teal-800'
                      } disabled:opacity-50`}
                      title={
                        isProtectedOrMandatory
                          ? 'Mandatory / protected loads cannot be curtailed'
                          : 'Authorize control signal'
                      }
                    >
                      {processingId === rec.action_id
                        ? 'Authorizing...'
                        : isProtectedOrMandatory
                        ? '🛡️ Protected'
                        : '✓ Authorize'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AUDIT TRAIL HISTORY */}
      <div className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2">
          Immutable Control Audit Trail
        </h3>

        {audit_history.length === 0 ? (
          <div className="text-xs text-slate-400 italic p-4 text-center">
            No historical control events logged for this asset yet.
          </div>
        ) : (
          <>
            {/* MOBILE AUDIT CARDS (Visible only on mobile) */}
            <div className="md:hidden space-y-3">
              {audit_history.map((hist: ControlAction) => (
                <div
                  key={hist.action_id}
                  className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2.5 font-mono text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">
                      {hist.action_id}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-black uppercase border ${
                        hist.status === 'APPROVED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : 'bg-rose-100 text-rose-800 border-rose-300'
                      }`}
                    >
                      {hist.status}
                    </span>
                  </div>

                  <div className="text-slate-800 font-bold uppercase text-[11px]">
                    {hist.action_type.replace(/_/g, ' ')}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-600 pt-1 border-t border-slate-200">
                    <div>
                      <span className="text-slate-400 block uppercase">Operator</span>
                      <span className="font-bold text-slate-800">{hist.operator_id || 'Autopilot'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block uppercase">Verification</span>
                      <span className="font-bold text-slate-800">{hist.physical_verification_status}</span>
                    </div>
                  </div>

                  <div className="text-[10px] text-slate-500 pt-1" suppressHydrationWarning>
                    {hist.decided_at
                      ? new Date(hist.decided_at).toLocaleString()
                      : new Date(hist.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>

            {/* DESKTOP AUDIT TABLE (Visible on md+ screens) */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider">
                  <tr>
                    <th className="p-3">Action ID</th>
                    <th className="p-3">Intervention Type</th>
                    <th className="p-3">Authorized Operator</th>
                    <th className="p-3">Decision</th>
                    <th className="p-3">Timestamp</th>
                    <th className="p-3">Verification Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {audit_history.map((hist: ControlAction) => (
                    <tr key={hist.action_id} className="hover:bg-slate-50">
                      <td className="p-3 font-mono font-bold text-slate-900">
                        {hist.action_id}
                      </td>
                      <td className="p-3 font-medium uppercase text-slate-700">
                        {hist.action_type.replace(/_/g, ' ')}
                      </td>
                      <td className="p-3 font-mono text-slate-800 font-bold">
                        {hist.operator_id || 'Autopilot Engine'}
                      </td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                            hist.status === 'APPROVED'
                              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                              : 'bg-rose-100 text-rose-800 border-rose-300'
                          }`}
                        >
                          {hist.status}
                        </span>
                      </td>
                      <td className="p-3 text-slate-600" suppressHydrationWarning>
                        {hist.decided_at
                          ? new Date(hist.decided_at).toLocaleString()
                          : new Date(hist.created_at).toLocaleString()}
                      </td>
                      <td className="p-3 font-mono text-[11px] text-slate-600">
                        {hist.physical_verification_status}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

    </div>
  )
}
