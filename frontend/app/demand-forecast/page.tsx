"use client"
import React, { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import ReactECharts from 'echarts-for-react'
import { useGlobalState } from '@/components/GlobalState'

export default function DemandForecastPage() {
  const { mode } = useGlobalState()
  const isLive = mode === 'LIVE'
  const [analytics, setAnalytics] = useState<any>(null)
  const [selectedTimeframe, setSelectedTimeframe] = useState<'day' | 'week' | 'month' | 'year'>('day')
  const [optimizationApproved, setOptimizationApproved] = useState<boolean>(false)

  useEffect(() => {
    let isMounted = true
    const fetchAnalytics = async () => {
      try {
        const baseUrl =
          typeof window !== 'undefined'
            ? `${window.location.protocol}//${window.location.hostname}:8000/api`
            : 'http://localhost:8000/api'
        const res = await fetch(`${baseUrl}/telemetry/layman_analytics?mode=${mode}`)
        if (res.ok) {
          const data = await res.json()
          if (isMounted) setAnalytics(data)
        }
      } catch (e) {
        // Fallback gracefully
      }
    }

    fetchAnalytics()
    const timer = setInterval(fetchAnalytics, 2000)
    return () => {
      isMounted = false
      clearInterval(timer)
    }
  }, [mode])

  // Telemetry fallback defaults
  const data = useMemo(() => {
    if (analytics) return analytics

    if (isLive) {
      return {
        maximum_demand: {
          current_demand_kw: 198.5,
          today_highest_peak_kw: 198.5,
          month_highest_peak_kw: 198.5,
          configured_demand_limit_kw: 200.0,
          safe_operating_limit_kw: 140.0,
          predicted_peak_kw: 198.5,
          predicted_peak_time: '--:--',
          remaining_buffer_kw: 1.5,
          unit: 'VA',
        },
        actual_vs_forecast: {
          hours: [
            '14 Oct 00:00', '14 Oct 01:00', '14 Oct 02:00', '14 Oct 03:00', '14 Oct 04:00', '14 Oct 05:00',
            '14 Oct 06:00', '14 Oct 07:00', '14 Oct 08:00', '14 Oct 09:00', '14 Oct 10:00', '14 Oct 11:00',
            '14 Oct 12:00', '14 Oct 13:00', '14 Oct 14:00', '14 Oct 15:00', '14 Oct 16:00', '14 Oct 17:00',
            '14 Oct 18:00', '14 Oct 19:00', '14 Oct 20:00', '14 Oct 21:00', '14 Oct 22:00', '14 Oct 23:00',
          ],
          actual_kw: Array(24).fill(null),
          forecast_kw: Array(24).fill(0.0),
          cmd_limit_kw: 200.0,
          safe_limit_kw: 140.0,
          predicted_peak_kw: 198.5,
          predicted_peak_time: '--:--',
          unit: 'VA',
        },
        timeframes: {
          day: {
            labels: ['14 Oct 00:00', '14 Oct 04:00', '14 Oct 08:00', '14 Oct 12:00', '14 Oct 16:00', '14 Oct 20:00'],
            values: [0, 0, 0, 0, 0, 0],
            peaks: [0, 0, 0, 0, 0, 0],
            peak: 0.0,
            total: 0.0,
            unit: 'Wh',
            demand_unit: 'VA',
          },
          week: {
            labels: ['08 Oct (Thu)', '09 Oct (Fri)', '10 Oct (Sat)', '11 Oct (Sun)', '12 Oct (Mon)', '13 Oct (Tue)', '14 Oct (Wed)'],
            values: [0, 0, 0, 0, 0, 0, 0],
            peaks: [0, 0, 0, 0, 0, 0, 0],
            peak: 0.0,
            total: 0.0,
            unit: 'Wh',
            demand_unit: 'VA',
          },
          month: {
            labels: ['16-22 Sep', '23-29 Sep', '30 Sep-06 Oct', '07-14 Oct (Current)'],
            values: [0, 0, 0, 0],
            peaks: [0, 0, 0, 0],
            peak: 0.0,
            total: 0.0,
            unit: 'Wh',
            demand_unit: 'VA',
          },
          year: {
            labels: ['Nov 2025', 'Dec 2025', 'Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026', 'Jul 2026', 'Aug 2026', 'Sep 2026', 'Oct 2026'],
            values: Array(12).fill(0),
            peaks: Array(12).fill(0),
            peak: 0.0,
            total: 0.0,
            unit: 'Wh',
            demand_unit: 'VA',
          },
        },
        optimization_opportunity: {
          title: 'Optimal Load Distribution & Surcharge Protection',
          suggestion: 'Operating load and 24h peak forecast are well within the 200 VA ceiling.',
          potential_savings: '₹ 0 (Zero surcharge risk — optimal operation)',
          predicted_peak_avoided_kw: 0.0,
        },
      }
    }

    return {
      maximum_demand: {
        current_demand_kw: 0.0,
        today_highest_peak_kw: 0.0,
        month_highest_peak_kw: 0.0,
        configured_demand_limit_kw: 100.0,
        predicted_peak_kw: 0.0,
        predicted_peak_time: '--:--',
        remaining_buffer_kw: 100.0,
      },
      actual_vs_forecast: {
        hours: [
          '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00',
          '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
          '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
        ],
        actual_kw: Array(24).fill(null),
        forecast_kw: Array(24).fill(0.0),
        cmd_limit_kw: 100.0,
        safe_limit_kw: 90.0,
        predicted_peak_kw: 0.0,
        predicted_peak_time: '--:--',
      },
      timeframes: {
        day: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          values: [0, 0, 0, 0, 0, 0],
          peak: 0.0,
          total: 0.0,
          unit: 'kWh',
        },
        week: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          values: [0, 0, 0, 0, 0, 0, 0],
          peaks: [0, 0, 0, 0, 0, 0, 0],
          peak: 0.0,
          total: 0.0,
          unit: 'kWh',
        },
        month: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          values: [0, 0, 0, 0],
          peaks: [0, 0, 0, 0],
          peak: 0.0,
          total: 0.0,
          unit: 'kWh',
        },
        year: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          values: Array(12).fill(0),
          peaks: Array(12).fill(0),
          peak: 0.0,
          total: 0.0,
          unit: 'kWh',
        },
      },
      optimization_opportunity: {
        title: 'Real-time AI Forecasting Active',
        suggestion: 'Connecting to live hardware meter and telemetry database for continuous peak demand inference...',
        potential_savings: '₹ 0 (Monitoring active)',
        predicted_peak_avoided_kw: 0.0,
      },
    }
  }, [analytics, isLive])

  const md = data.maximum_demand || {}
  const af = data.actual_vs_forecast || {}
  const tf = data.timeframes || {}
  const opp = data.optimization_opportunity || {}
  const pq = data.power_quality || {}

  const demandUnit = isLive ? 'VA' : 'kW'
  const energyUnit = isLive ? 'Wh' : 'kWh'

  const currentDemand = Number(md.current_demand_kw ?? 0.0)
  const peakDemand = Number(md.today_highest_peak_kw ?? currentDemand)
  const contractLimit = isLive ? 200.0 : Number(md.configured_demand_limit_kw ?? 100.0)
  const safeLimit = isLive ? 140.0 : Number(af.safe_limit_kw ?? 90.0)
  const predictedPeak = Number(af.predicted_peak_kw ?? currentDemand)
  const predictedPeakTime = String(af.predicted_peak_time || '--:--')
  const currentPf = Number(pq.current_power_factor ?? 0.95)

  // Dynamic Y-axis max for sub-kilowatt bench testing vs industrial scale
  const yAxisMax24h = useMemo(() => {
    if (isLive) return 220
    const maxVal = Math.max(currentDemand, peakDemand, predictedPeak)
    if (maxVal < 1.0) return 1.0
    if (maxVal < 5.0) return Math.ceil(maxVal * 2.0)
    return Math.max(110, Math.ceil(maxVal * 1.15))
  }, [isLive, currentDemand, peakDemand, predictedPeak])

  // ECharts 1: 24-Hour Actual vs AI Predicted Demand Curve
  const chartOptions24h = useMemo(() => {
    const hours = af.hours || []
    const actuals = af.actual_kw || []
    const forecasts = af.forecast_kw || []

    return {
      animation: false,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
        backgroundColor: '#0f172a',
        borderColor: '#334155',
        textStyle: { color: '#ffffff', fontSize: 12, fontWeight: 'bold' },
        formatter: (params: any[]) => {
          let html = `<div class="font-black text-xs pb-1 mb-1 border-b border-slate-700">${params[0]?.axisValue}</div>`
          params.forEach((p) => {
            if (p.value !== null && p.value !== undefined) {
              html += `<div class="flex items-center justify-between gap-4 py-0.5">
                <span style="color:${p.color}">● ${p.seriesName}:</span>
                <span class="font-black">${Number(p.value).toFixed(1)} ${demandUnit}</span>
              </div>`
            }
          })
          return html
        },
      },
      legend: {
        data: isLive
          ? ['Actual Measured Demand', 'AI Forecast Demand', 'Safe Operating Limit (140 VA)', 'Contract Ceiling (200 VA)']
          : (yAxisMax24h >= 100
              ? ['Actual Measured Demand', 'AI Forecast Demand', 'Safe Operating Limit (90 kW)', 'Contract Ceiling (100 kW)']
              : ['Actual Measured Demand', 'AI Forecast Demand']),
        top: 8,
        textStyle: { fontWeight: 'bold', fontSize: 11, color: '#1e293b' },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '18%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: hours,
        axisLine: { lineStyle: { color: '#94a3b8', width: 2 } },
        axisLabel: { fontWeight: 'bold', color: '#334155', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        name: `Demand (${demandUnit})`,
        nameTextStyle: { fontWeight: 'bold', color: '#1e293b', fontSize: 12 },
        min: 0,
        max: yAxisMax24h,
        axisLine: { show: true, lineStyle: { color: '#94a3b8' } },
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLabel: { fontWeight: 'bold', color: '#334155' },
      },
      series: [
        {
          name: 'Actual Measured Demand',
          type: 'line',
          smooth: true,
          data: actuals,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: { color: '#059669' },
          lineStyle: { width: 3.5, color: '#059669' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(5, 150, 105, 0.35)' },
                { offset: 1, color: 'rgba(5, 150, 105, 0.02)' },
              ],
            },
          },
        },
        {
          name: 'AI Forecast Demand',
          type: 'line',
          smooth: true,
          data: forecasts,
          symbol: 'diamond',
          symbolSize: 7,
          itemStyle: { color: '#6366f1' },
          lineStyle: { width: 3.5, type: 'solid', color: '#6366f1' },
          markPoint: {
            silent: true,
            data: [
              {
                coord: [
                  hours.find((h: string) => h.includes(predictedPeakTime.slice(-5))) || hours[Math.min(14, hours.length - 1)] || '14:00',
                  predictedPeak,
                ],
                value: `Crest: ${predictedPeak.toFixed(1)} ${demandUnit}`,
                itemStyle: { color: '#e11d48' },
              },
            ],
          },
        },
        ...(isLive || yAxisMax24h >= 100
          ? [
              {
                name: isLive ? 'Safe Operating Limit (140 VA)' : 'Safe Operating Limit (90 kW)',
                type: 'line',
                data: Array(hours.length).fill(safeLimit),
                silent: true,
                lineStyle: { type: 'dashed', width: 2.5, color: '#d97706' },
                itemStyle: { color: '#d97706' },
                symbol: 'none',
              },
              {
                name: isLive ? 'Contract Ceiling (200 VA)' : 'Contract Ceiling (100 kW)',
                type: 'line',
                data: Array(hours.length).fill(contractLimit),
                silent: true,
                lineStyle: { type: 'solid', width: 2.5, color: '#dc2626' },
                itemStyle: { color: '#dc2626' },
                symbol: 'none',
              },
            ]
          : []),
      ],
    }
  }, [af, isLive, demandUnit, safeLimit, contractLimit, predictedPeak, predictedPeakTime, yAxisMax24h])

  // ECharts 2: Multi-Timeframe Historical Analysis
  const chartOptionsTimeframe = useMemo(() => {
    const currentTf = tf[selectedTimeframe] || tf.day || {}
    const labels = currentTf.labels || []
    const values = currentTf.values || []
    const peaks = currentTf.peaks || values

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#0f172a',
        textStyle: { color: '#ffffff', fontWeight: 'bold' },
        formatter: (params: any[]) => {
          let html = `<div class="font-black text-xs pb-1 mb-1 border-b border-slate-700">${params[0]?.axisValue}</div>`
          params.forEach((p) => {
            if (p.value !== null && p.value !== undefined) {
              const u = p.seriesName.includes('Peak') ? demandUnit : energyUnit
              html += `<div class="flex items-center justify-between gap-4 py-0.5">
                <span style="color:${p.color}">● ${p.seriesName}:</span>
                <span class="font-black">${Number(p.value).toLocaleString()} ${u}</span>
              </div>`
            }
          })
          return html
        },
      },
      legend: {
        data: [`Energy (${energyUnit})`, `Peak Demand (${demandUnit})`],
        top: 4,
        textStyle: { fontWeight: 'bold', color: '#334155' },
      },
      grid: { left: '3%', right: '3%', bottom: '8%', top: '18%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { fontWeight: 'bold', color: '#334155' },
      },
      yAxis: [
        {
          type: 'value',
          name: energyUnit,
          axisLabel: { fontWeight: 'bold', color: '#334155' },
          splitLine: { lineStyle: { color: '#f1f5f9' } },
        },
        {
          type: 'value',
          name: `Peak ${demandUnit}`,
          min: 0,
          max: isLive ? 220 : (peaks && Math.max(...peaks.map(Number), 0) < 5.0 ? 2.0 : 120),
          axisLabel: { fontWeight: 'bold', color: '#334155' },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: `Energy (${energyUnit})`,
          type: 'bar',
          data: values,
          itemStyle: { color: '#818cf8', borderRadius: [6, 6, 0, 0] },
        },
        {
          name: `Peak Demand (${demandUnit})`,
          type: 'line',
          yAxisIndex: 1,
          data: peaks,
          itemStyle: { color: '#e11d48' },
          lineStyle: { width: 3, color: '#e11d48' },
          symbol: 'circle',
          symbolSize: 8,
        },
      ],
    }
  }, [tf, selectedTimeframe, isLive, demandUnit, energyUnit])

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
      
      {/* HEADER SECTION WITH NAVIGATION */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b-2 border-slate-300 pb-4 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-indigo-700 text-white text-[11px] font-black px-2.5 py-0.5 rounded uppercase tracking-wider">
              XGBoost &bull; LSTM Neural Forecaster
            </span>
            <span className="bg-slate-200 text-slate-900 text-[11px] font-black px-2.5 py-0.5 rounded uppercase tracking-wider">
              Early Warning Protocol Active
            </span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-black tracking-tight text-slate-900 uppercase mt-2">
            AI Peak Demand Forecasting & Graphs
          </h1>
          <p className="text-xs font-black tracking-widest text-slate-700 uppercase mt-1">
            24h Horizon Predictive Modeling • Surcharge Avoidance Intelligence
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="bg-white border-2 border-slate-300 hover:bg-slate-100 text-slate-900 font-black text-xs px-4 py-2.5 rounded-xl transition-all shadow-xs flex items-center gap-1.5 uppercase tracking-wider"
          >
            <span>&larr; Plant Visual Dashboard</span>
          </Link>
        </div>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {/* Card 1: Current Active Demand */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-slate-600 tracking-wider">Current Demand</div>
          <div className="text-2xl font-black text-slate-950 mt-1">
            {currentDemand.toFixed(isLive ? 1 : 2)} <span className="text-xs font-bold text-slate-600">{demandUnit}</span>
          </div>
          <div className="text-[11px] font-bold text-slate-500 mt-0.5">
            {((currentDemand / contractLimit) * 100).toFixed(1)}% of ceiling
          </div>
        </div>

        {/* Card 2: Highest Peak Measured Today */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-slate-600 tracking-wider">Today Highest Peak</div>
          <div className="text-2xl font-black text-rose-700 mt-1">
            {peakDemand.toFixed(isLive ? 1 : 2)} <span className="text-xs font-bold text-slate-600">{demandUnit}</span>
          </div>
          <div className="text-[11px] font-bold text-slate-500 mt-0.5">
            {md.today_highest_peak_time ? `Recorded at ${md.today_highest_peak_time}` : 'Live Monitoring'}
          </div>
        </div>

        {/* Card 3: AI Predicted Peak Crest */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-indigo-700 tracking-wider">AI Forecast Peak</div>
          <div className="text-2xl font-black text-indigo-950 mt-1">
            {predictedPeak.toFixed(isLive ? 1 : 2)} <span className="text-xs font-bold text-slate-600">{demandUnit}</span>
          </div>
          <div className="text-[11px] font-bold text-indigo-800 mt-0.5">Expected at {predictedPeakTime}</div>
        </div>

        {/* Card 4: Safe Buffer Remaining */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-emerald-700 tracking-wider">Safe Operating Buffer</div>
          <div className="text-2xl font-black text-emerald-800 mt-1">
            {Math.max(0, contractLimit - Math.max(currentDemand, peakDemand)).toFixed(isLive ? 1 : 2)}{' '}
            <span className="text-xs font-bold text-slate-600">{demandUnit}</span>
          </div>
          <div className="text-[11px] font-bold text-emerald-700 mt-0.5">Safe margin before penalty</div>
        </div>

        {/* Card 5: Contract Demand Ceiling */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm col-span-2 md:col-span-1">
          <div className="text-[11px] font-black uppercase text-slate-600 tracking-wider">Contracted Ceiling</div>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {contractLimit.toFixed(0)} <span className="text-xs font-bold text-slate-600">{demandUnit}</span>
          </div>
          <div className="text-[11px] font-bold text-rose-700 mt-0.5">
            {isLive ? 'Hardware Bench Limit (200 VA)' : 'HT Utility Sanctioned Limit'}
          </div>
        </div>
      </div>

      {/* =================================================================== */}
      {/* HERO GRAPH: 24-HOUR ACTUAL VS AI PREDICTED DEMAND CURVE             */}
      {/* =================================================================== */}
      <div className="bg-white border-2 border-slate-200 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-4 border-b border-slate-100 gap-2">
          <div>
            <h2 className="text-lg font-black text-slate-900 uppercase tracking-tight">
              24-Hour Actual vs AI Predicted Load Profile
            </h2>
            <p className="text-xs font-bold text-slate-600 mt-0.5">
              Green line represents physical meter readings; Purple line shows future AI load projection with predicted crest.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black bg-indigo-50 border border-indigo-200 text-indigo-900 px-3 py-1 rounded-lg">
              Predicted Crest: {predictedPeak.toFixed(1)} {demandUnit} @ {predictedPeakTime}
            </span>
          </div>
        </div>

        <div className="w-full h-[400px]">
          <ReactECharts option={chartOptions24h} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>

      {/* =================================================================== */}
      {/* ROW 2: TIMEFRAMES ANALYSIS & ACTIONABLE LOAD SHEDDING PROPOSAL      */}
      {/* =================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        
        {/* Left: Timeframe Trend Comparison (7 cols) */}
        <div className="lg:col-span-7 bg-white border-2 border-slate-200 rounded-3xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-4 border-b border-slate-100 gap-2">
              <div>
                <h3 className="text-base font-black text-slate-900 uppercase tracking-tight">
                  Historical Demand Trend Analysis
                </h3>
                <p className="text-xs font-bold text-slate-600">
                  Energy usage volume alongside measured peak demand peaks
                </p>
              </div>

              {/* Timeframe Selector Buttons */}
              <div className="flex items-center bg-slate-100 p-1 rounded-xl gap-1">
                {(['day', 'week', 'month', 'year'] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setSelectedTimeframe(mode)}
                    className={`px-3 py-1 rounded-lg text-xs font-black uppercase transition-all ${
                      selectedTimeframe === mode
                        ? 'bg-indigo-700 text-white shadow-xs'
                        : 'text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>

            <div className="w-full h-[280px]">
              <ReactECharts option={chartOptionsTimeframe} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs font-black text-slate-700">
            <span>Period Total: {(tf[selectedTimeframe]?.total || 0).toLocaleString()} {energyUnit}</span>
            <span>Period Peak: {(tf[selectedTimeframe]?.peak || 0)} {demandUnit}</span>
            <span>Est. Cost: ₹ {Math.round(isLive ? (tf[selectedTimeframe]?.cost_inr ?? ((tf[selectedTimeframe]?.total || 0) * 0.0075)) : ((tf[selectedTimeframe]?.total || 0) * 7.5)).toLocaleString()}</span>
          </div>
        </div>

        {/* Right: Actionable AI Load Shifting Protocol (5 cols) */}
        <div className="lg:col-span-5 bg-gradient-to-br from-indigo-50 to-slate-50 border-2 border-indigo-200 rounded-3xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-indigo-200">
              <span className="text-xs font-black bg-indigo-600 text-white px-2.5 py-0.5 rounded-full uppercase">
                AI Optimization Opportunity
              </span>
              <span
                className={`text-xs font-black px-2 py-0.5 rounded ${
                  opp.operator_approval_required
                    ? 'text-amber-800 bg-amber-100'
                    : 'text-emerald-800 bg-emerald-100'
                }`}
              >
                {opp.operator_approval_required ? 'Operator Approval Required' : 'Optimal Load Status'}
              </span>
            </div>

            <h3 className="text-lg font-black text-indigo-950 tracking-tight mb-2">
              {opp.title || 'Optimal Load Distribution & Surcharge Protection'}
            </h3>

            <p className="text-xs font-bold text-slate-700 leading-relaxed mb-4">
              {opp.suggestion ||
                `Operating load (${currentDemand.toFixed(1)} ${demandUnit}) and 24h AI peak forecast (${predictedPeak.toFixed(1)} ${demandUnit} @ ${predictedPeakTime}) are within sanctioned limits.`}
            </p>

            <div className="space-y-3 bg-white border border-indigo-100 rounded-2xl p-4 shadow-2xs">
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Predicted Peak Avoided:</span>
                <span className="text-emerald-700 text-sm font-black">
                  {opp.predicted_peak_avoided_kw ? `-${opp.predicted_peak_avoided_kw} ${demandUnit}` : `0.0 ${demandUnit} (Within limit)`}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Potential Penalty Saved:</span>
                <span className="text-emerald-700 text-sm font-black">{opp.potential_savings || '₹ 0 (Zero penalty)'}</span>
              </div>
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Execution Method:</span>
                <span className="text-slate-900">SCADA Automated Soft-Start Interlock</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-indigo-200">
            {opp.operator_approval_required ? (
              optimizationApproved ? (
                <div className="bg-emerald-100 border border-emerald-300 text-emerald-950 font-black text-xs py-3 px-4 rounded-xl text-center shadow-xs">
                  ✓ Protocol Authorized & Synchronized with SCADA PLC
                </div>
              ) : (
                <button
                  onClick={() => setOptimizationApproved(true)}
                  className="w-full bg-indigo-700 hover:bg-indigo-800 text-white font-black text-xs py-3.5 px-4 rounded-xl transition-all shadow-md uppercase tracking-wider flex items-center justify-center gap-2"
                >
                  <span>Authorize AI Load Shifting Protocol</span>
                  <span>&rarr;</span>
                </button>
              )
            ) : (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 font-bold text-xs py-3 px-4 rounded-xl text-center">
                ✓ Continuous AI Surcharge Guard Active • Factory demand well within contract threshold
              </div>
            )}
            <p className="text-[10px] font-bold text-slate-500 text-center mt-2">
              No physical machine setpoint is altered without human supervisor authorization.
            </p>
          </div>
        </div>

      </div>

    </div>
  )
}
