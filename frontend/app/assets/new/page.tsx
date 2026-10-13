"use client"
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getApiBaseUrl } from '@/lib/config'

export default function CreateAssetPage() {
  const router = useRouter()
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  // Form Fields
  const [assetId, setAssetId] = useState<string>('')
  const [name, setName] = useState<string>('')
  const [equipmentType, setEquipmentType] = useState<string>('')
  const [manufacturerModel, setManufacturerModel] = useState<string>('')
  const [location, setLocation] = useState<string>('')
  const [ratedCapacityKw, setRatedCapacityKw] = useState<string>('')
  const [ratedVoltageV, setRatedVoltageV] = useState<string>('415')
  const [phaseConfig, setPhaseConfig] = useState<string>('3-Phase 415V')
  const [pccAssociation, setPccAssociation] = useState<string>('PCC-01')
  const [meterAssociation, setMeterAssociation] = useState<string>('RPi-METER-01')
  const [loadClassification, setLoadClassification] = useState<string>('Flexible')
  const [priorityOrder, setPriorityOrder] = useState<number>(2)
  const [isProtected, setIsProtected] = useState<boolean>(false)

  // Permitted actions
  const [permittedActions, setPermittedActions] = useState<string[]>([
    'monitor_only',
    'delay_startup'
  ])

  // Operational Constraints
  const [minRuntime, setMinRuntime] = useState<number>(15)
  const [minOfftime, setMinOfftime] = useState<number>(15)
  const [restartDelay, setRestartDelay] = useState<number>(5)
  const [operatingSchedule, setOperatingSchedule] = useState<string>('24/7 Continuous')
  const [productionConstraints, setProductionConstraints] = useState<string>('')
  const [operatorNotes, setOperatorNotes] = useState<string>('')
  const [maintenanceNotes, setMaintenanceNotes] = useState<string>('')

  const baseUrl = getApiBaseUrl()

  const handleActionToggle = (actionKey: string) => {
    if (permittedActions.includes(actionKey)) {
      setPermittedActions(permittedActions.filter((a) => a !== actionKey))
    } else {
      setPermittedActions([...permittedActions, actionKey])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)

    // Validation
    if (!name.trim()) {
      setValidationError('Asset name is required.')
      return
    }

    const isMandatoryOrProtected = isProtected || loadClassification === 'Mandatory'
    if (isMandatoryOrProtected && permittedActions.includes('authorized_switch_off')) {
      setValidationError(
        'Safety Constraint Violation: Mandatory and Protected loads cannot permit authorized switch-off/shedding. Remove switch-off permission or change classification.'
      )
      return
    }

    setSubmitting(true)

    try {
      const payload = {
        asset_id: assetId.trim() || undefined,
        name: name.trim(),
        equipment_type: equipmentType.trim() || 'Not configured',
        manufacturer_model: manufacturerModel.trim() || 'Not configured',
        location: location.trim() || 'Not configured',
        rated_capacity_kw: ratedCapacityKw ? parseFloat(ratedCapacityKw) : undefined,
        rated_voltage_v: ratedVoltageV ? parseFloat(ratedVoltageV) : undefined,
        phase_config: phaseConfig,
        pcc_association: pccAssociation,
        meter_association: meterAssociation,
        load_classification: loadClassification,
        priority_order: priorityOrder,
        is_protected: isMandatoryOrProtected,
        permitted_actions: permittedActions.length > 0 ? permittedActions : ['monitor_only'],
        min_runtime_minutes: minRuntime,
        min_offtime_minutes: minOfftime,
        restart_delay_minutes: restartDelay,
        operating_schedule: operatingSchedule || '24/7 Continuous',
        production_constraints: productionConstraints.trim() || 'Not configured',
        operator_notes: operatorNotes.trim() || 'Not configured',
        maintenance_notes: maintenanceNotes.trim() || 'Not configured'
      }

      const res = await fetch(`${baseUrl}/assets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `Server responded with ${res.status}`)
      }

      const json = await res.json()
      const createdId = json.asset?.asset_id || assetId
      router.push(`/assets/${createdId}`)
    } catch (e: any) {
      setValidationError(e.message || 'Failed to create asset.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-[1000px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-300 pb-4 gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-800 uppercase">
            Register New Asset
          </h1>
          <p className="text-[11px] sm:text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">
            Create permanent load profile and assign QR Passport
          </p>
        </div>
        <Link
          href="/assets"
          className="w-full sm:w-auto text-center bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3.5 py-2.5 rounded-xl transition-all min-h-[40px] flex items-center justify-center"
        >
          &larr; Back to Registry
        </Link>
      </div>

      {/* Validation Banner */}
      {validationError && (
        <div className="bg-rose-50 border-2 border-rose-300 rounded-xl p-4 text-xs font-bold text-rose-800 flex items-start gap-2">
          <span>🚨</span>
          <span>{validationError}</span>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white border border-slate-300 rounded-xl p-4 sm:p-6 shadow-sm space-y-6 text-xs font-bold">
        
        {/* Section 1: Identity */}
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-4">
            1. Identity &amp; Physical Specifications
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-700 mb-1">
                Asset ID (Immutable)
                <span className="text-[10px] text-slate-400 font-normal ml-1">
                  (Leave blank for auto-generated LOAD-XXX)
                </span>
              </label>
              <input
                type="text"
                value={assetId}
                onChange={(e) => setAssetId(e.target.value.toUpperCase())}
                placeholder="e.g. LOAD-004, PUMP-002"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-mono text-slate-900 outline-none focus:border-teal-600"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">
                Asset Display Name <span className="text-rose-600">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Cooling Tower Fan 01"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none focus:border-teal-600"
                required
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Equipment Type</label>
              <input
                type="text"
                value={equipmentType}
                onChange={(e) => setEquipmentType(e.target.value)}
                placeholder="e.g. Centrifugal Fan, Screw Compressor"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Manufacturer &amp; Model</label>
              <input
                type="text"
                value={manufacturerModel}
                onChange={(e) => setManufacturerModel(e.target.value)}
                placeholder="e.g. Siemens 1LE1001"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Plant Location / Area</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Utility Building - Mezzanine"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Rated Capacity (kW)</label>
              <input
                type="number"
                step="0.1"
                value={ratedCapacityKw}
                onChange={(e) => setRatedCapacityKw(e.target.value)}
                placeholder="e.g. 15.0 (leave blank if unknown)"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Electrical & Grid Connection */}
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-4">
            2. Electrical &amp; Grid Connection
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-700 mb-1">Rated Voltage (V)</label>
              <input
                type="number"
                value={ratedVoltageV}
                onChange={(e) => setRatedVoltageV(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Phase Configuration</label>
              <select
                value={phaseConfig}
                onChange={(e) => setPhaseConfig(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              >
                <option value="3-Phase 415V">3-Phase 415V</option>
                <option value="1-Phase 230V">1-Phase 230V</option>
                <option value="Not configured">Not configured</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Point of Common Coupling (PCC)</label>
              <select
                value={pccAssociation}
                onChange={(e) => setPccAssociation(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              >
                <option value="PCC-01">PCC-01 (Main Incomer Bus)</option>
                <option value="PCC-02">PCC-02 (Feeder Sub-Bus B)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: Optimization & Safety Classification */}
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-4">
            3. Optimization Classification &amp; Safety Rules
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-700 mb-1">Load Classification</label>
              <select
                value={loadClassification}
                onChange={(e) => {
                  const val = e.target.value
                  setLoadClassification(val)
                  if (val === 'Mandatory') setIsProtected(true)
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              >
                <option value="Mandatory">Mandatory (Base production / critical)</option>
                <option value="Flexible">Flexible (Can modulate or delay)</option>
                <option value="Opportunistic">Opportunistic (Buffer / deferrable)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Priority Order</label>
              <select
                value={priorityOrder}
                onChange={(e) => setPriorityOrder(parseInt(e.target.value))}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              >
                <option value={1}>1 - Highest Priority (Protected)</option>
                <option value={2}>2 - Secondary Shedding Candidate</option>
                <option value={3}>3 - First Shedding Candidate</option>
                <option value={4}>4 - Auxiliary Deferrable</option>
              </select>
            </div>

            <div className="flex flex-col justify-end pb-2">
              <label className="flex items-center gap-2 cursor-pointer bg-slate-50 p-2.5 rounded-lg border border-slate-300">
                <input
                  type="checkbox"
                  checked={isProtected || loadClassification === 'Mandatory'}
                  onChange={(e) => setIsProtected(e.target.checked)}
                  disabled={loadClassification === 'Mandatory'}
                  className="rounded text-teal-600"
                />
                <span className="text-xs font-bold text-slate-900">
                  Protect from Peak Shedding
                </span>
              </label>
            </div>
          </div>

          {/* Permitted Actions Checkboxes */}
          <div className="mt-4 bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
            <label className="block text-slate-700 font-bold mb-1">
              Permitted Optimization Actions
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={permittedActions.includes('monitor_only')}
                  onChange={() => handleActionToggle('monitor_only')}
                  className="rounded text-teal-600"
                />
                <span>Monitor Only</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={permittedActions.includes('delay_startup')}
                  onChange={() => handleActionToggle('delay_startup')}
                  className="rounded text-teal-600"
                />
                <span>Delay Startup</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={permittedActions.includes('modulate_setpoint')}
                  onChange={() => handleActionToggle('modulate_setpoint')}
                  className="rounded text-teal-600"
                />
                <span>Modulate Setpoint</span>
              </label>

              <label
                className={`flex items-center gap-2 cursor-pointer ${
                  isProtected || loadClassification === 'Mandatory'
                    ? 'opacity-40 cursor-not-allowed'
                    : ''
                }`}
                title={
                  isProtected || loadClassification === 'Mandatory'
                    ? 'Protected loads cannot be switched off'
                    : ''
                }
              >
                <input
                  type="checkbox"
                  checked={permittedActions.includes('authorized_switch_off')}
                  disabled={isProtected || loadClassification === 'Mandatory'}
                  onChange={() => handleActionToggle('authorized_switch_off')}
                  className="rounded text-rose-600"
                />
                <span className="text-rose-900">Authorized Switch-Off</span>
              </label>
            </div>
          </div>
        </div>

        {/* Section 4: Operational Constraints & Notes */}
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 border-b border-slate-200 pb-2 mb-4">
            4. Operational Constraints &amp; Notes
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-slate-700 mb-1">Min Runtime (mins)</label>
              <input
                type="number"
                value={minRuntime}
                onChange={(e) => setMinRuntime(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Min Off-Time (mins)</label>
              <input
                type="number"
                value={minOfftime}
                onChange={(e) => setMinOfftime(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Restart Delay (mins)</label>
              <input
                type="number"
                value={restartDelay}
                onChange={(e) => setRestartDelay(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-slate-700 mb-1">Operating Schedule</label>
              <input
                type="text"
                value={operatingSchedule}
                onChange={(e) => setOperatingSchedule(e.target.value)}
                placeholder="e.g. 24/7 Continuous or Two Shifts (06:00 - 22:00)"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Production Constraints</label>
              <textarea
                rows={2}
                value={productionConstraints}
                onChange={(e) => setProductionConstraints(e.target.value)}
                placeholder="e.g. Line dependency, temperature buffer limitations, unloader max idle time"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1">Maintenance &amp; Service Notes</label>
              <textarea
                rows={2}
                value={maintenanceNotes}
                onChange={(e) => setMaintenanceNotes(e.target.value)}
                placeholder="e.g. Greasing interval, inspection history, insulation test records"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="pt-4 border-t border-slate-200 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-end gap-2.5 sm:gap-3">
          <Link
            href="/assets"
            className="min-h-[44px] flex items-center justify-center text-center px-4 py-2.5 rounded-xl text-xs font-bold uppercase text-slate-600 hover:bg-slate-100 border border-slate-200 sm:border-transparent"
          >
            Cancel
          </Link>

          <button
            type="submit"
            disabled={submitting}
            className="min-h-[44px] flex items-center justify-center text-center bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs px-6 py-2.5 rounded-xl uppercase tracking-wider transition-all shadow-sm disabled:opacity-50"
          >
            {submitting ? 'Creating Profile...' : '✓ Register & Generate QR'}
          </button>
        </div>
      </form>

    </div>
  )
}
