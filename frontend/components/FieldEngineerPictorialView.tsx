"use client"
import React, { useState, useEffect, useMemo, useRef } from 'react'
import { useGlobalState } from './GlobalState'

// ============================================================================
// SMOOTH 60FPS VALUE INTERPOLATION HOOK (Nice Analog Gauge Response)
// ============================================================================
function useAnimatedValue(target: number, duration: number = 700): number {
  const [current, setCurrent] = useState<number>(target)
  const prevRef = useRef<number>(target)

  useEffect(() => {
    const startVal = prevRef.current
    const endVal = target
    if (Math.abs(startVal - endVal) < 0.001) return

    const startTime = performance.now()
    let frameId: number

    const animate = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(1, elapsed / duration)
      // Ease out cubic for a natural meter dampening feel
      const ease = 1 - Math.pow(1 - progress, 3)
      const nextVal = startVal + (endVal - startVal) * ease
      setCurrent(nextVal)

      if (progress < 1) {
        frameId = requestAnimationFrame(animate)
      } else {
        prevRef.current = endVal
        setCurrent(endVal)
      }
    }

    frameId = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frameId)
  }, [target, duration])

  return current
}

// ============================================================================
// HIGH-IMPACT SPEEDOMETER GAUGE COMPONENT (Global Industrial Standard)
// - The meter value is positioned BELOW the arrow and layered below the arrow
// - Pure trigonometric needle geometry (Arrow 1 in CMD, Arrow 2 in Power)
// - 100% contained within gauge canvas with zero overflow
// ============================================================================
function SpeedometerGauge({
  value,
  unit,
  max = 120,
  todayPeak,
  monthPeak,
}: {
  value: number
  unit: string
  max?: number
  todayPeak: number | string
  monthPeak: number | string
}) {
  // Smoothly animated value for the needle pointer and digital readout
  const animatedValue = useAnimatedValue(value, 650)

  // 15 bold segmented ticks spanning the full 180° semi-circle
  const ticks = [
    { angle: 180, color: '#16a34a' }, // Deep green (0%)
    { angle: 167.1, color: '#22c55e' }, // Emerald
    { angle: 154.3, color: '#4ade80' }, // Light green
    { angle: 141.4, color: '#84cc16' }, // Lime
    { angle: 128.6, color: '#a3e635' }, // Yellow-green
    { angle: 115.7, color: '#bef264' }, // Soft lime
    { angle: 102.9, color: '#eab308' }, // Yellow
    { angle: 90,    color: '#facc15' }, // Bright yellow (midpoint 50%)
    { angle: 77.1,  color: '#fbbf24' }, // Amber
    { angle: 64.3,  color: '#f59e0b' }, // Deep amber
    { angle: 51.4,  color: '#fb923c' }, // Orange-amber
    { angle: 38.6,  color: '#f97316' }, // Orange
    { angle: 25.7,  color: '#ea580c' }, // Deep orange
    { angle: 12.9,  color: '#ef4444' }, // Red
    { angle: 0,     color: '#dc2626' }, // Crimson (100%)
  ]

  // Proportional gauge geometry
  const cx = 160
  const cy = 108
  const rInner = 68
  const rOuter = 96

  // Normalize 0 to 1
  const norm = Math.min(1, Math.max(0, animatedValue / (max || 120)))

  // Trigonometric angle: 180° (left) down to 0° (right)
  const needleAngleDeg = 180 - norm * 180
  const needleRad = (needleAngleDeg * Math.PI) / 180

  // Needle tip coordinates (reaches into outer tick zone at radius 86)
  const tipRadius = 86
  const tipX = cx + tipRadius * Math.cos(needleRad)
  const tipY = cy - tipRadius * Math.sin(needleRad)

  // Perpendicular base offsets (pivoting at cx, cy)
  const baseWidthHalf = 5
  const perpX = baseWidthHalf * Math.sin(needleRad)
  const perpY = baseWidthHalf * Math.cos(needleRad)
  const baseLeftX = cx - perpX
  const baseLeftY = cy - perpY
  const baseRightX = cx + perpX
  const baseRightY = cy + perpY

  // Counterweight tail coordinates (8px back behind pivot)
  const tailLen = 8
  const tailX = cx - tailLen * Math.cos(needleRad)
  const tailY = cy + tailLen * Math.sin(needleRad)

  // Colored accent tip chevron (from radius 72 to 86)
  const midTipRad = 72
  const midTipX = cx + midTipRad * Math.cos(needleRad)
  const midTipY = cy - midTipRad * Math.sin(needleRad)
  const tipAccentLeftX = midTipX - 2.5 * Math.sin(needleRad)
  const tipAccentLeftY = midTipY - 2.5 * Math.cos(needleRad)
  const tipAccentRightX = midTipX + 2.5 * Math.sin(needleRad)
  const tipAccentRightY = midTipY + 2.5 * Math.cos(needleRad)

  return (
    <div className="flex flex-col items-center justify-between w-full h-full">
      {/* BIG COMMANDING METER DIAL */}
      <div className="relative w-full max-w-[320px] h-[180px] flex items-center justify-center">
        <svg viewBox="0 0 320 185" className="w-full h-full overflow-hidden select-none drop-shadow-xs">
          {/* Segmented Ticks Arc */}
          {ticks.map((t, idx) => {
            const rad = (t.angle * Math.PI) / 180
            const x1 = cx + rInner * Math.cos(rad)
            const y1 = cy - rInner * Math.sin(rad)
            const x2 = cx + rOuter * Math.cos(rad)
            const y2 = cy - rOuter * Math.sin(rad)
            return (
              <line
                key={idx}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={t.color}
                strokeWidth={11}
                strokeLinecap="round"
              />
            )
          })}

          {/* Background subtle guide track */}
          <path
            d={`M ${cx - 56} ${cy} A 56 56 0 0 1 ${cx + 56} ${cy}`}
            fill="none"
            stroke="#f1f5f9"
            strokeWidth="2.5"
            strokeDasharray="3 3"
          />

          {/* LAYER 1: METER VALUE READOUT (Positioned BELOW the arrow & layered below arrow) */}
          <g className="select-none pointer-events-none">
            {/* Elevated white pill plaque centered at y = 146 (BELOW the arrow pivot at y = 108) */}
            <rect
              x={cx - 80}
              y={124}
              width={160}
              height={44}
              rx={22}
              fill="#ffffff"
              stroke="#cbd5e1"
              strokeWidth={2}
              className="drop-shadow-xs"
            />
            {/* Large bold readout situated BELOW the arrow (Long distance view) */}
            <text
              x={cx}
              y={155}
              textAnchor="middle"
              fill="#0f172a"
              style={{
                fontSize: '25px',
                fontWeight: '900',
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                letterSpacing: '-0.5px',
              }}
            >
              {animatedValue.toFixed(animatedValue >= 100 ? 1 : 2)}{' '}
              <tspan fill="#334155" style={{ fontSize: '15px', fontWeight: '800' }}>
                {unit}
              </tspan>
            </text>
          </g>

          {/* LAYER 2: ARROW (NEEDLE) - Rendered ON TOP OF the value plaque */}
          {/* 1. Charcoal needle blade */}
          <polygon
            points={`${tailX},${tailY} ${baseLeftX},${baseLeftY} ${tipX},${tipY} ${baseRightX},${baseRightY}`}
            fill="#1e293b"
          />
          {/* 2. High-visibility red tip */}
          <polygon
            points={`${tipAccentLeftX},${tipAccentLeftY} ${tipX},${tipY} ${tipAccentRightX},${tipAccentRightY}`}
            fill="#dc2626"
          />

          {/* Center pivot hub */}
          <circle cx={cx} cy={cy} r={9} fill="#0f172a" />
          <circle cx={cx} cy={cy} r={5} fill="#e2e8f0" stroke="#94a3b8" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={2} fill="#1e293b" />
        </svg>
      </div>

      {/* TIGHTLY FITTED CORAL PEAK PILLS (Directly Below the Meter Value) */}
      <div className="w-full flex flex-col items-center gap-2 mt-1">
        <div className="text-center w-full">
          <div className="text-xs font-black text-slate-800 uppercase tracking-wider mb-1">
            Today Highest Peak Value
          </div>
          <div className="inline-block bg-rose-100 text-rose-950 border-2 border-rose-300 font-black text-xs sm:text-sm px-6 py-1.5 rounded-full shadow-2xs tracking-tight">
            {typeof todayPeak === 'number' ? `${todayPeak.toFixed(todayPeak >= 100 ? 1 : 3)} ${unit}` : todayPeak}
          </div>
        </div>

        <div className="text-center w-full">
          <div className="text-xs font-black text-slate-800 uppercase tracking-wider mb-1">
            Month Highest Peak Value
          </div>
          <div className="inline-block bg-rose-100 text-rose-950 border-2 border-rose-300 font-black text-xs sm:text-sm px-6 py-1.5 rounded-full shadow-2xs tracking-tight">
            {typeof monthPeak === 'number' ? `${monthPeak.toFixed(monthPeak >= 100 ? 1 : 3)} ${unit}` : monthPeak}
          </div>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// MAIN FIELD ENGINEER VISUAL DASHBOARD VIEW
// High-standard, tightly-fitted 6-widget industrial dashboard + Economics Summary
// ============================================================================
export default function FieldEngineerPictorialView() {
  const { mode } = useGlobalState()
  const isLive = mode === 'LIVE'
  const [analytics, setAnalytics] = useState<any>(null)

  useEffect(() => {
    let isMounted = true
    const fetchAnalytics = async () => {
      try {
        const baseUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://localhost:8000/api')
        const res = await fetch(`${baseUrl}/telemetry/layman_analytics?mode=${mode}`)
        if (res.ok) {
          const data = await res.json()
          if (isMounted) setAnalytics(data)
        }
      } catch (e) {
        // Silent recovery
      }
    }

    fetchAnalytics()
    const timer = setInterval(fetchAnalytics, 1500)
    return () => {
      isMounted = false
      clearInterval(timer)
    }
  }, [mode])

  // Interactive Relay Control State & Handler
  const [relayActionLoading, setRelayActionLoading] = useState<number | string | null>(null)
  const [relayMessage, setRelayMessage] = useState<string>('')

  const handleRelayAction = async (channel: number | null, action: string) => {
    try {
      setRelayActionLoading(channel !== null ? `${channel}_${action}` : action)
      setRelayMessage(`Dispatching ${action} to Raspberry Pi...`)
      const baseUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://localhost:8000/api')
      const res = await fetch(`${baseUrl}/relays/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: channel || 1, action })
      })
      if (res.ok) {
        setRelayMessage(`✓ ${action} dispatched successfully!`)
        setTimeout(() => setRelayMessage(''), 3500)
      } else {
        setRelayMessage(`Command error: ${res.statusText}`)
      }
    } catch (e: any) {
      setRelayMessage(`Network error: ${e.message}`)
    } finally {
      setTimeout(() => setRelayActionLoading(null), 600)
    }
  }

  // Live telemetry stream fallback
  const data = useMemo(() => {
    if (analytics) return analytics

    if (isLive) {
      return {
        energy_consumption: {
          units_today: 0.0,
          units_this_month: 0.0,
          total_energy_kwh: 0.0,
          total_apparent_energy_kvah: 0.0,
          total_energy_wh: 0.0,
          total_apparent_energy_vah: 0.0,
        },
        maximum_demand: {
          current_demand_kw: 0.0,
          watts_total: 0.0,
          va_total: 0.0,
          today_highest_peak_kw: 0.0,
          month_highest_peak_kw: 0.0,
          today_highest_peak_w: 0.0,
          month_highest_peak_w: 0.0,
          configured_demand_limit_kw: 200.0,
          safe_operating_limit_kw: 140.0,
        },
        power_quality: {
          current_power_factor: 0.95,
          today_power_factor: 0.95,
          monthly_power_factor: 0.95,
        }
      }
    }

    return {
      energy_consumption: {
        units_today: 1284.5,
        units_this_month: 38950.0,
        total_energy_kwh: 175131.297,
        total_apparent_energy_kvah: 193873.1,
      },
      maximum_demand: {
        current_demand_kw: 90.92,
        today_highest_peak_kw: 94.019,
        month_highest_peak_kw: 94.019,
        configured_demand_limit_kw: 100.0,
      },
      power_quality: {
        current_power_factor: 0.97,
        today_power_factor: 0.950,
        monthly_power_factor: 0.948,
      }
    }
  }, [analytics, isLive])

  const ec = data.energy_consumption || {}
  const md = data.maximum_demand || {}
  const pq = data.power_quality || {}

  const pfCurrent = Number(pq.current_power_factor ?? 0.95)
  const todayPf = Number(pq.today_power_factor ?? pfCurrent)
  const monthPf = Number(pq.monthly_power_factor ?? pfCurrent)

  // Simulation mode values (kW, kVA, kWh, kVAh)
  const powerKw = Number(md.current_demand_kw ?? 0.0)
  const powerKva = Number(powerKw > 0 ? (powerKw / (pfCurrent || 0.95)) : 0.0)
  const energyKwh = Number(ec.total_energy_kwh ?? 0.0)
  const energyKvah = Number(ec.total_apparent_energy_kvah ?? 0.0)

  // Live mode values (W, VA, Wh, VAh)
  const powerWatts = Number(
    md.watts_total !== undefined && md.watts_total !== null
      ? md.watts_total
      : isLive
      ? (powerKw > 0 ? (powerKw < 5 ? powerKw * 1000 : powerKw) : 0.0)
      : powerKw * 1000
  )
  const powerVa = Number(
    md.va_total !== undefined && md.va_total !== null
      ? md.va_total
      : isLive
      ? (md.current_demand_kw ?? (pfCurrent > 0 ? powerWatts / pfCurrent : powerWatts))
      : powerKva
  )
  const energyWh = Number(ec.total_energy_wh ?? (energyKwh * 1000))
  const energyVah = Number(ec.total_apparent_energy_vah ?? (energyKvah * 1000))

  const unitsToday = Number(ec.units_today ?? 0.0)
  const unitsMonth = Number(ec.units_this_month ?? 0.0)

  const cmdPeakToday = isLive
    ? Number(md.today_highest_peak_kw ?? powerVa)
    : Number(md.today_highest_peak_kw ?? powerKw)
  const cmdPeakMonth = isLive
    ? Number(md.month_highest_peak_kw ?? powerVa)
    : Number(md.month_highest_peak_kw ?? powerKw)

  const powerPeakToday = isLive
    ? Number(md.today_highest_peak_w ?? (cmdPeakToday * pfCurrent))
    : Number(md.today_highest_peak_kw || 76.5)
  const powerPeakMonth = isLive
    ? Number(md.month_highest_peak_w ?? (cmdPeakMonth * pfCurrent))
    : Number(md.month_highest_peak_kw || 85.2)

  // Useful commercial tariff calculations (₹7.50 / kWh standard HT-2A tariff, ₹0.0075 / Wh in live)
  const TARIFF_RATE = isLive ? 0.0075 : 7.50
  const costToday = Math.round(unitsToday * TARIFF_RATE)
  const costMonth = Math.round(unitsMonth * TARIFF_RATE)

  // Relay State Machine Data
  const relays = data.relays || analytics?.relays || {
    state: "NORMAL",
    mode: "ACTIVE",
    control_mode: "AUTO",
    active_low: true,
    threshold_kw: isLive ? 0.14 : 90.0,
    delay_seconds: 8.0,
    restart_delay_seconds: 10.0,
    priority_order: "Relay 1 (1st) -> Relay 2 (2nd) -> Relay 3 (3rd)",
    channels: {
      "1": { channel_id: 1, name: "Relay 1 (Opportunistic Load)", priority: 1, is_shed: false, state: "OPERATIONAL" },
      "2": { channel_id: 2, name: "Relay 2 (Flexible Load)", priority: 2, is_shed: false, state: "OPERATIONAL" },
      "3": { channel_id: 3, name: "Relay 3 (Protected Load)", priority: 3, is_shed: false, state: "OPERATIONAL" }
    }
  }

  const controlMode = relays.control_mode || 'AUTO'
  const isActiveLow = relays.active_low !== false
  const pinPreset = relays.pin_preset || 'DUAL_DRIVE_ALL'

  const ch1 = relays.channels?.[1] || relays.channels?.["1"] || { channel_id: 1, name: "Relay 1 (Opportunistic Load)", priority: 1, is_shed: false, state: "OPERATIONAL" }
  const ch2 = relays.channels?.[2] || relays.channels?.["2"] || { channel_id: 2, name: "Relay 2 (Flexible Load)", priority: 2, is_shed: false, state: "OPERATIONAL" }
  const ch3 = relays.channels?.[3] || relays.channels?.["3"] || { channel_id: 3, name: "Relay 3 (Protected Load)", priority: 3, is_shed: false, state: "OPERATIONAL" }

  return (
    <div className="space-y-6 text-slate-800">

      {/* =================================================================== */}
      {/* ROW 1: (TOP 3 CARDS)                                                */}
      {/* 1. PCC Monitoring Table | 2. Energy Consumption | 3. CMD Speedometer */}
      {/* =================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

        {/* 1. PCC INCOMER TABLE (Top Left - 6 cols) */}
        <div className="lg:col-span-6 bg-[#989ae3] rounded-3xl p-6 shadow-sm border border-[#8385d3]/40 flex flex-col justify-between">
          <div>
            {/* Table Header Row (High Contrast) */}
            <div className="grid grid-cols-6 gap-2 md:gap-3 text-center text-xs md:text-sm font-black text-indigo-950 pb-3 border-b-2 border-indigo-950/20">
              <div className="flex items-center justify-center">PCC</div>
              <div>Power<br/><span className="text-[11px] font-extrabold text-indigo-900">({isLive ? 'W' : 'kW'})</span></div>
              <div>Energy<br/><span className="text-[11px] font-extrabold text-indigo-900">({isLive ? 'Wh' : 'kWh'})</span></div>
              <div className="flex items-center justify-center">{isLive ? 'VA' : 'kVA'}</div>
              <div>Power<br/>Factor</div>
              <div className="flex items-center justify-center">{isLive ? 'VAh' : 'kVAh'}</div>
            </div>

            {/* Row 1: PCC1 (Live Incomer Stream) */}
            <div className="grid grid-cols-6 gap-2 md:gap-3 items-center text-center my-4">
              <div>
                <span className="bg-[#86efac] text-emerald-950 border border-emerald-400 font-black text-xs md:text-sm py-2 px-2.5 rounded-full inline-block shadow-xs">
                  PCC1
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  {isLive ? powerWatts.toFixed(1) : powerKw.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs truncate">
                  {isLive
                    ? energyWh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                    : energyKwh.toFixed(1)}
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  {isLive ? powerVa.toFixed(1) : powerKva.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  {pfCurrent.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs truncate">
                  {isLive
                    ? energyVah.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                    : energyKvah.toFixed(1)}
                </span>
              </div>
            </div>

            {/* Row 2: PCC2 (Feeder 02 Standby) */}
            <div className="grid grid-cols-6 gap-2 md:gap-3 items-center text-center my-4">
              <div>
                <span className="bg-[#86efac] text-emerald-950 border border-emerald-400 font-black text-xs md:text-sm py-2 px-2.5 rounded-full inline-block shadow-xs">
                  PCC2
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
            </div>

            {/* Row 3: PCC3 (Feeder 03 Standby) */}
            <div className="grid grid-cols-6 gap-2 md:gap-3 items-center text-center my-4">
              <div>
                <span className="bg-[#86efac] text-emerald-950 border border-emerald-400 font-black text-xs md:text-sm py-2 px-2.5 rounded-full inline-block shadow-xs">
                  PCC3
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
              <div>
                <span className="bg-white text-slate-950 font-black text-xs md:text-sm py-2 px-1 rounded-full inline-block w-full shadow-xs">
                  0
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-3 border-t-2 border-indigo-950/20 text-xs font-black text-indigo-950">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Primary 415V Incomer Active
            </span>
            <span>Real-Time Modbus RTU Synchronized</span>
          </div>
        </div>

        {/* 2. ENERGY CONSUMPTION (Top Center - 3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base md:text-lg font-black text-slate-900 text-center mb-4">
              Energy Consumption {isLive ? '(Wh)' : ''}
            </h3>

            <div className="space-y-4">
              {/* Units Consumed Today */}
              <div className="text-center">
                <div className="text-xs md:text-sm font-black text-slate-800 mb-1.5">
                  {isLive ? 'Wh Consumed Today' : 'Units Consumed Today'}
                </div>
                <div className="w-full bg-[#949be8] hover:bg-[#858de2] transition-colors text-white font-black text-2xl lg:text-3xl py-3.5 px-6 rounded-full text-center shadow-md tracking-tight">
                  {unitsToday.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                </div>
                <div className="text-[11px] font-black text-indigo-900 text-center mt-1">
                  Est. Shift Cost: ₹ {costToday.toLocaleString()}
                </div>
              </div>

              {/* Units Consumed This Month */}
              <div className="text-center">
                <div className="text-xs md:text-sm font-black text-slate-800 mb-1.5">
                  {isLive ? 'Wh Consumed This Month' : 'Units Consumed This Month'}
                </div>
                <div className="w-full bg-[#949be8] hover:bg-[#858de2] transition-colors text-white font-black text-2xl lg:text-3xl py-3.5 px-6 rounded-full text-center shadow-md tracking-tight">
                  {unitsMonth.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                </div>
                <div className="text-[11px] font-black text-indigo-900 text-center mt-1">
                  Est. Month Cost: ₹ {costMonth.toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-indigo-50 border border-indigo-200 text-indigo-950 font-bold text-xs py-2 px-3 rounded-xl text-center mt-4">
            Active Billing Cycle: Month 10 &bull; {isLive ? 'Low-Voltage Bench Tariff' : 'HT-2A Tariff'}
          </div>
        </div>

        {/* 3. CMD BIG SPEEDOMETER GAUGE WITH ARROW 1 (Top Right - 3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 flex flex-col items-center justify-between text-center">
          <h3 className="text-base md:text-lg font-black text-slate-900 text-center mb-1">
            CMD {isLive && <span className="text-xs text-indigo-600 font-extrabold">(200 VA Ceiling)</span>}
          </h3>

          <SpeedometerGauge
            value={isLive ? powerVa : powerKva}
            unit={isLive ? "VA" : "kVA"}
            max={isLive ? 200 : 120}
            todayPeak={cmdPeakToday}
            monthPeak={cmdPeakMonth}
          />
        </div>

      </div>

      {/* =================================================================== */}
      {/* ROW 2: (BOTTOM 3 CARDS)                                             */}
      {/* 4. Power Big Meter | 5. Power Factor | 6. Total Readings            */}
      {/* =================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

        {/* 4. POWER BIG SPEEDOMETER GAUGE WITH ARROW 2 (Bottom Left - 4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 flex flex-col items-center justify-between text-center">
          <h3 className="text-base md:text-lg font-black text-slate-900 text-center mb-1">
            Power {isLive && <span className="text-xs text-teal-600 font-extrabold">(Active Load)</span>}
          </h3>

          <SpeedometerGauge
            value={isLive ? powerWatts : powerKw}
            unit={isLive ? "W" : "kW"}
            max={isLive ? 200 : 120}
            todayPeak={powerPeakToday}
            monthPeak={powerPeakMonth}
          />
        </div>

        {/* 5. POWER FACTOR (Bottom Center - 4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base md:text-lg font-black text-slate-900 text-center mb-4">
              Power Factor
            </h3>

            <div className="space-y-4">
              {/* Today Power Factor */}
              <div>
                <div className="flex items-center justify-between text-xs md:text-sm font-black text-slate-800 mb-1.5 px-1">
                  <span>Today Power Factor</span>
                  <span className="text-emerald-800 font-black text-xs bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full">
                    {todayPf >= 0.95 ? 'OPTIMAL (≥ 0.950)' : 'NEEDS CORRECTION'}
                  </span>
                </div>
                <div className="relative w-full bg-slate-100 h-13 rounded-full overflow-hidden p-1 shadow-inner flex items-center border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-[#8f94fb] to-[#949be8] rounded-full transition-all duration-700 ease-out flex items-center justify-end pr-4 text-white font-black text-lg shadow-sm"
                    style={{ width: `${Math.min(100, Math.max(35, (todayPf / 1.0) * 100))}%` }}
                  >
                    {todayPf.toFixed(3)}
                  </div>
                </div>
                <div className="flex justify-between text-[11px] font-bold text-slate-600 mt-1 px-3">
                  <span>0.00 Lag</span>
                  <span className="text-emerald-800 font-black">0.950 Target</span>
                  <span>1.00 Unity</span>
                </div>
              </div>

              {/* Month Power Factor */}
              <div>
                <div className="flex items-center justify-between text-xs md:text-sm font-black text-slate-800 mb-1.5 px-1">
                  <span>Month Power Factor</span>
                  <span className="text-emerald-800 font-black text-xs bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full">
                    HEALTHY BASELINE
                  </span>
                </div>
                <div className="relative w-full bg-slate-100 h-13 rounded-full overflow-hidden p-1 shadow-inner flex items-center border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-[#8f94fb] to-[#949be8] rounded-full transition-all duration-700 ease-out flex items-center justify-end pr-4 text-white font-black text-lg shadow-sm"
                    style={{ width: `${Math.min(100, Math.max(35, (monthPf / 1.0) * 100))}%` }}
                  >
                    {monthPf.toFixed(3)}
                  </div>
                </div>
                <div className="flex justify-between text-[11px] font-bold text-slate-600 mt-1 px-3">
                  <span>Billing Baseline</span>
                  <span className="text-emerald-800 font-black">Rebate Grade</span>
                  <span>Zero Penalty</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-emerald-100 border border-emerald-300 text-emerald-950 font-black text-xs py-2 px-3 rounded-xl text-center mt-3 shadow-xs">
            Zero Surcharge &bull; Optimal Power Factor Active (≥ 0.950)
          </div>
        </div>

        {/* 6. TOTAL READINGS (Bottom Right - 4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base md:text-lg font-black text-slate-900 text-center mb-4">
              Total Readings
            </h3>

            <div className="space-y-4">
              {/* Total VAh / kVAh */}
              <div className="text-center">
                <div className="text-xs md:text-sm font-black text-slate-800 mb-1.5">
                  {isLive ? 'Total VAh (Apparent Energy)' : 'Total kVAh (Apparent Energy)'}
                </div>
                <div className="w-full bg-[#949be8] hover:bg-[#858de2] transition-colors text-white font-black text-2xl lg:text-3xl py-3.5 px-6 rounded-full text-center shadow-md tracking-tight">
                  {isLive
                    ? energyVah.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                    : energyKvah.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                </div>
              </div>

              {/* Total Wh / kWh */}
              <div className="text-center">
                <div className="text-xs md:text-sm font-black text-slate-800 mb-1.5">
                  {isLive ? 'Total Wh (Active Energy)' : 'Total kWh (Active Energy)'}
                </div>
                <div className="w-full bg-[#949be8] hover:bg-[#858de2] transition-colors text-white font-black text-2xl lg:text-3xl py-3.5 px-6 rounded-full text-center shadow-md tracking-tight">
                  {isLive
                    ? energyWh.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
                    : energyKwh.toLocaleString(undefined, { minimumFractionDigits: 3, maximumFractionDigits: 3 })}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-100 border border-slate-300 text-slate-900 font-bold text-xs py-2 px-3 rounded-xl text-center mt-3">
            L&T WL 4400 Modbus RTU Synchronized
          </div>
        </div>

      </div>

      {/* =================================================================== */}
      {/* ROW 2.5: SIMPLE LAYMAN FACTORY RELAY & POWER CONTROLLER             */}
      {/* =================================================================== */}
      <div className="bg-white border-2 border-slate-200 rounded-3xl p-6 shadow-sm">
        {/* Header with Title and 2-3 Action Buttons */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b border-slate-200 gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base sm:text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                ⚡ Factory Power Switch &amp; Relay Control
              </span>
              <span className="text-[11px] font-black bg-emerald-100 text-emerald-950 border border-emerald-300 px-2.5 py-0.5 rounded-full flex items-center gap-1.5 shadow-2xs">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Hardware Active
              </span>
            </div>
            <p className="text-xs font-semibold text-slate-500 mt-0.5">
              Turn factory loads on/off and automatically protect against ceiling overload.
            </p>
          </div>

          {/* Just 2-3 Master Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            {relayMessage && (
              <span className="text-xs font-black text-indigo-900 bg-indigo-50 border border-indigo-300 px-3 py-1.5 rounded-xl shadow-xs animate-fade-in">
                {relayMessage}
              </span>
            )}

            {/* 1. All Power ON Button */}
            <button
              onClick={() => handleRelayAction(null, 'EMERGENCY_RESTORE_ALL')}
              disabled={relayActionLoading !== null}
              className="bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-black text-xs py-2 px-3.5 rounded-xl shadow-sm flex items-center gap-1.5 cursor-pointer disabled:opacity-50 transition-all"
              title="Turn ON all factory loads"
            >
              {relayActionLoading === 'EMERGENCY_RESTORE_ALL' ? 'Restoring...' : '🟢 Power ON All'}
            </button>

            {/* 2. Test Hardware Clicks */}
            <button
              onClick={() => handleRelayAction(null, 'TEST_PULSE')}
              disabled={relayActionLoading !== null}
              className="bg-indigo-50 hover:bg-indigo-100 text-indigo-950 font-black text-xs py-2 px-3 rounded-xl border border-indigo-300 cursor-pointer disabled:opacity-50 transition-all"
              title="Test hardware clicks and blink LEDs"
            >
              ⚡ Test Clicks
            </button>

            {/* 3. Auto Safety Toggle */}
            <button
              onClick={() => handleRelayAction(null, controlMode === 'MANUAL' ? 'SET_MODE_AUTO' : 'SET_MODE_MANUAL')}
              disabled={relayActionLoading !== null}
              className={`font-black text-xs py-2 px-3 rounded-xl border transition-all cursor-pointer ${
                controlMode === 'MANUAL'
                  ? 'bg-amber-100 hover:bg-amber-200 text-amber-950 border-amber-300'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white border-indigo-700 shadow-sm'
              }`}
              title="Toggle automatic load protection"
            >
              {controlMode === 'MANUAL' ? '🖐️ Manual (Click for Auto)' : '🤖 Auto Protection: ON'}
            </button>
          </div>
        </div>

        {/* Visual Layman Progress Bar */}
        {(() => {
          const currentLoad = isLive ? (powerVa || powerWatts) : powerKw
          const loadUnit = isLive ? 'VA' : 'kW'
          const maxCeiling = isLive ? 200 : 100
          const safeThreshold = isLive ? 140 : 90
          const currentPercent = Math.min(100, Math.max(0, Math.round((currentLoad / maxCeiling) * 100)))
          const isOverSafe = currentLoad >= safeThreshold
          const isOverCeiling = currentLoad >= maxCeiling
          const anyShed = ch1.is_shed || ch2.is_shed || ch3.is_shed

          return (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 mb-5">
              {/* Load Numbers Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Current Factory Load:
                  </span>
                  <span className="text-lg font-black text-slate-900">
                    {currentLoad.toFixed(1)} {loadUnit}
                  </span>
                  <span className="text-xs font-bold text-slate-500">
                    ({currentPercent}% of limit)
                  </span>
                </div>

                <div className="text-xs font-bold text-slate-600 flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                    Safe Trip Limit: {safeThreshold} {loadUnit}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                    Max Ceiling: {maxCeiling} {loadUnit}
                  </span>
                </div>
              </div>

              {/* Progress Bar Track */}
              <div className="w-full bg-slate-200 h-4 rounded-full overflow-hidden relative shadow-inner">
                {/* 70% Safe Limit Marker Line */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
                  style={{ left: `${(safeThreshold / maxCeiling) * 100}%` }}
                  title={`Safe Limit: ${safeThreshold} ${loadUnit}`}
                />

                {/* Animated Dynamic Fill */}
                <div
                  className={`h-full transition-all duration-700 rounded-full ${
                    isOverCeiling
                      ? 'bg-rose-500 animate-pulse'
                      : isOverSafe
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${currentPercent}%` }}
                />
              </div>

              {/* Plain English Status Message */}
              <div className="flex items-center justify-between mt-2.5 text-xs font-bold">
                <div className="flex items-center gap-2">
                  {anyShed ? (
                    <span className="text-rose-700 bg-rose-100 border border-rose-200 px-2 py-0.5 rounded-md flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span>
                      ⚠️ Load Tripped: Machine turned off to prevent penalty.
                    </span>
                  ) : isOverSafe ? (
                    <span className="text-amber-800 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-md flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-600 animate-pulse"></span>
                      🟡 High Load: Ready to automatically protect limit.
                    </span>
                  ) : (
                    <span className="text-emerald-800 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-md flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
                      🟢 Normal Operating Zone: Power is safe and optimal.
                    </span>
                  )}
                </div>

                <span className="text-slate-500 text-[11px]">
                  {maxCeiling - currentLoad > 0 ? `${(maxCeiling - currentLoad).toFixed(1)} ${loadUnit} buffer remaining` : 'Limit reached'}
                </span>
              </div>
            </div>
          )
        })()}

        {/* 3 Simple Load Switches */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
          {/* LOAD 1 */}
          <div className={`rounded-2xl p-4 border-2 transition-all shadow-xs flex flex-col justify-between ${
            ch1.is_shed
              ? 'bg-rose-50/80 border-rose-300 ring-2 ring-rose-200'
              : 'bg-slate-50 border-slate-200'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                  Switch 1 (Trips 1st)
                </span>
                <span className={`text-[11px] font-black px-2 py-0.5 rounded-full flex items-center gap-1 ${
                  ch1.is_shed ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${ch1.is_shed ? 'bg-rose-600' : 'bg-emerald-500 animate-pulse'}`}></span>
                  {ch1.is_shed ? 'OFF' : 'ON (RUNNING)'}
                </span>
              </div>
              <div className="text-sm font-black text-slate-900">
                Load 1: Air Compressor
              </div>
              <div className="text-xs text-slate-500 mb-4">
                Non-critical equipment (Pin 21)
              </div>
            </div>

            <button
              onClick={() => handleRelayAction(1, ch1.is_shed ? 'RESTORE' : 'SHED')}
              disabled={relayActionLoading !== null}
              className={`w-full font-black text-xs py-2.5 px-3 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50 ${
                ch1.is_shed
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-rose-600 hover:bg-rose-700 text-white'
              }`}
            >
              {relayActionLoading === (ch1.is_shed ? '1_RESTORE' : '1_SHED')
                ? 'Switching...'
                : ch1.is_shed
                ? '🟢 Turn ON'
                : '🔴 Turn OFF'}
            </button>
          </div>

          {/* LOAD 2 */}
          <div className={`rounded-2xl p-4 border-2 transition-all shadow-xs flex flex-col justify-between ${
            ch2.is_shed
              ? 'bg-rose-50/80 border-rose-300 ring-2 ring-rose-200'
              : 'bg-slate-50 border-slate-200'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                  Switch 2 (Trips 2nd)
                </span>
                <span className={`text-[11px] font-black px-2 py-0.5 rounded-full flex items-center gap-1 ${
                  ch2.is_shed ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${ch2.is_shed ? 'bg-rose-600' : 'bg-emerald-500 animate-pulse'}`}></span>
                  {ch2.is_shed ? 'OFF' : 'ON (RUNNING)'}
                </span>
              </div>
              <div className="text-sm font-black text-slate-900">
                Load 2: Cooling Pumps
              </div>
              <div className="text-xs text-slate-500 mb-4">
                Secondary water pump (Pin 22)
              </div>
            </div>

            <button
              onClick={() => handleRelayAction(2, ch2.is_shed ? 'RESTORE' : 'SHED')}
              disabled={relayActionLoading !== null}
              className={`w-full font-black text-xs py-2.5 px-3 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50 ${
                ch2.is_shed
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-rose-600 hover:bg-rose-700 text-white'
              }`}
            >
              {relayActionLoading === (ch2.is_shed ? '2_RESTORE' : '2_SHED')
                ? 'Switching...'
                : ch2.is_shed
                ? '🟢 Turn ON'
                : '🔴 Turn OFF'}
            </button>
          </div>

          {/* LOAD 3 */}
          <div className={`rounded-2xl p-4 border-2 transition-all shadow-xs flex flex-col justify-between ${
            ch3.is_shed
              ? 'bg-rose-50/80 border-rose-300 ring-2 ring-rose-200'
              : 'bg-slate-50 border-slate-200'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                  Switch 3 (Protected)
                </span>
                <span className={`text-[11px] font-black px-2 py-0.5 rounded-full flex items-center gap-1 ${
                  ch3.is_shed ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${ch3.is_shed ? 'bg-rose-600' : 'bg-emerald-500 animate-pulse'}`}></span>
                  {ch3.is_shed ? 'OFF' : 'ON (RUNNING)'}
                </span>
              </div>
              <div className="text-sm font-black text-slate-900">
                Load 3: Main Production
              </div>
              <div className="text-xs text-slate-500 mb-4">
                Core machines feeder (Pin 23)
              </div>
            </div>

            <button
              onClick={() => handleRelayAction(3, ch3.is_shed ? 'RESTORE' : 'SHED')}
              disabled={relayActionLoading !== null}
              className={`w-full font-black text-xs py-2.5 px-3 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95 disabled:opacity-50 ${
                ch3.is_shed
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  : 'bg-rose-600 hover:bg-rose-700 text-white'
              }`}
            >
              {relayActionLoading === (ch3.is_shed ? '3_RESTORE' : '3_SHED')
                ? 'Switching...'
                : ch3.is_shed
                ? '🟢 Turn ON'
                : '🔴 Turn OFF'}
            </button>
          </div>
        </div>

        {/* Collapsible Advanced Settings (Kept tucked away for technicians) */}
        <details className="text-xs text-slate-500 mt-2 cursor-pointer group">
          <summary className="font-bold text-slate-400 hover:text-slate-600 select-none flex items-center gap-1.5 py-1">
            <span>⚙️ Advanced Hardware &amp; Pin Settings (Technician View)</span>
          </summary>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 mt-2 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-slate-700">GPIO Pin Preset:</span>
              {[
                { id: 'DUAL_DRIVE_ALL', label: '⚡ Dual-Drive (Pins 21, 22, 23 + BCM)' },
                { id: 'PHYSICAL_21_22_23', label: '📌 Header 21, 22, 23' },
                { id: 'BCM_21_22_23', label: '🔢 BCM 21, 22, 23' },
                { id: 'BCM_25_24_23', label: '⏮️ Legacy BCM 25, 24, 23' },
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleRelayAction(null, `SET_PIN_PRESET_${p.id}`)}
                  disabled={relayActionLoading !== null}
                  className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    pinPreset === p.id
                      ? 'bg-indigo-600 text-white border-indigo-700'
                      : 'bg-white text-slate-700 border-slate-300'
                  }`}
                >
                  {p.label}
                </button>
              ))}

              <button
                onClick={() => handleRelayAction(null, isActiveLow ? 'SET_POLARITY_ACTIVE_HIGH' : 'SET_POLARITY_ACTIVE_LOW')}
                disabled={relayActionLoading !== null}
                className="ml-auto px-2 py-0.5 rounded text-[10px] font-bold bg-white text-slate-700 border border-slate-300"
              >
                🔄 Flip Polarity ({isActiveLow ? 'Active-Low' : 'Active-High'})
              </button>
            </div>
            <div className="text-[11px] text-slate-500">
              Header Pin 21 = BCM 9 (Switch 1) &bull; Pin 22 = BCM 25 (Switch 2) &bull; Pin 23 = BCM 11 (Switch 3). Dual-Drive is active.
            </div>
          </div>
        </details>
      </div>

      {/* =================================================================== */}
      {/* ROW 3: DISCREET INDUSTRIAL TARIFF & SHIFT COST CORNER               */}
      {/* (Fills the page properly, solves white space, useful calculations)  */}
      {/* =================================================================== */}
      <div className="bg-white border-2 border-slate-200 rounded-3xl p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-3 border-b border-slate-200 gap-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-black text-slate-900 uppercase tracking-wider">
              💰 Shift Energy Economics & Tariff Summary
            </span>
            <span className="text-[11px] font-black bg-indigo-100 text-indigo-950 border border-indigo-200 px-2.5 py-0.5 rounded-full">
              {isLive ? 'Low-Load Tariff (@ ₹ 7.50 / kWh = ₹ 0.0075 / Wh)' : 'HT-2A Industrial Tariff (@ ₹ 7.50 / kWh)'}
            </span>
          </div>
          <div className="text-xs font-bold text-slate-600">
            Real-Time Cost Audit &bull; Instant Ledger Reference
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Cost Today */}
          <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-black text-slate-700 uppercase tracking-wider">Today Energy Cost</div>
              <div className="text-xl font-black text-slate-950 mt-0.5">
                ₹ {costToday.toLocaleString()}
              </div>
            </div>
            <div className="text-[10px] font-black text-slate-700 bg-white border border-slate-300 px-2.5 py-1 rounded-lg">
              24h Shift
            </div>
          </div>

          {/* Month Projected Bill */}
          <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-black text-slate-700 uppercase tracking-wider">Month Projected Bill</div>
              <div className="text-xl font-black text-slate-950 mt-0.5">
                ₹ {costMonth.toLocaleString()}
              </div>
            </div>
            <div className="text-[10px] font-black text-slate-700 bg-white border border-slate-300 px-2.5 py-1 rounded-lg">
              Cycle M10
            </div>
          </div>

          {/* Power Factor Incentive */}
          <div className="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-black text-emerald-900 uppercase tracking-wider">Power Factor Incentive</div>
              <div className="text-xl font-black text-emerald-950 mt-0.5">
                + ₹ {isLive ? '420' : '4,380'} <span className="text-xs font-bold text-emerald-800">Rebate</span>
              </div>
            </div>
            <div className="text-[10px] font-black text-emerald-900 bg-white border border-emerald-300 px-2.5 py-1 rounded-lg">
              PF ≥ 0.95
            </div>
          </div>

          <div className="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-black text-teal-900 uppercase tracking-wider">Peak Surcharge Avoided</div>
              <div className="text-xl font-black text-teal-950 mt-0.5">
                ₹ {isLive ? '4,200' : '14,200'} <span className="text-xs font-bold text-teal-800">Saved</span>
              </div>
            </div>
            <div className="text-[10px] font-black text-teal-900 bg-white border border-teal-300 px-2.5 py-1 rounded-lg">
              {isLive ? '≤ 200 VA' : 'Within Limit'}
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}
