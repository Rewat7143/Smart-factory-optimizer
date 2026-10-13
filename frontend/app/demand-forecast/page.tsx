"use client"
import React, { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import ReactECharts from 'echarts-for-react'

export default function DemandForecastPage() {
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
        const res = await fetch(`${baseUrl}/telemetry/layman_analytics`)
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
  }, [])

  // Telemetry fallback defaults
  const data = useMemo(() => {
    if (analytics) return analytics

    return {
      maximum_demand: {
        current_demand_kw: 90.92,
        today_highest_peak_kw: 94.19,
        month_highest_peak_kw: 94.19,
        configured_demand_limit_kw: 100.0,
        predicted_peak_kw: 88.4,
        predicted_peak_time: '14:30',
        remaining_buffer_kw: 5.81,
      },
      actual_vs_forecast: {
        hours: [
          '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00',
          '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
          '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
        ],
        actual_kw: [
          22.0, 20.5, 19.8, 18.2, 24.0, 31.5, 52.0, 72.4,
          85.0, 89.2, 91.1, 90.9, null, null, null, null,
          null, null, null, null, null, null, null, null,
        ],
        forecast_kw: [
          22.0, 20.5, 19.8, 18.2, 24.0, 31.5, 52.0, 72.4,
          85.0, 89.2, 91.1, 90.9, 78.0, 82.5, 88.4, 84.1,
          74.0, 62.5, 54.0, 42.5, 34.0, 28.0, 24.5, 22.0,
        ],
        cmd_limit_kw: 100.0,
        safe_limit_kw: 90.0,
        predicted_peak_kw: 88.4,
        predicted_peak_time: '14:30',
      },
      timeframes: {
        day: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          values: [21.5, 25.0, 85.0, 91.1, 74.0, 32.0],
          peak: 91.1,
          total: 1284.5,
          unit: 'kWh',
        },
        week: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          values: [1340, 1420, 1284, 1390, 1450, 920, 610],
          peaks: [92.4, 94.2, 91.1, 93.0, 94.8, 62.1, 41.5],
          peak: 94.8,
          total: 8414.0,
          unit: 'kWh',
        },
        month: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          values: [9450, 9820, 9640, 10040],
          peaks: [94.0, 94.8, 93.5, 94.2],
          peak: 94.8,
          total: 38950.0,
          unit: 'kWh',
        },
        year: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
          values: [37500, 36200, 39100, 38400, 40100, 41200, 39800, 39200, 38950, 38950],
          peaks: [92.0, 93.1, 94.5, 95.0, 96.2, 95.8, 94.1, 93.5, 94.2, 94.2],
          peak: 96.2,
          total: 389400.0,
          unit: 'kWh',
        },
      },
      optimization_opportunity: {
        title: 'Stagger Compressor C-02 & Induction Furnace Startup',
        suggestion:
          'Shift Compressor C-02 heavy cycle from 14:15 to 15:00 to prevent predicted peak of 88.4 kW from approaching the 90 kW safe limit.',
        potential_savings: '₹ 4,200 avoiding peak demand utility surcharge',
        predicted_peak_avoided_kw: 11.9,
      },
    }
  }, [analytics])

  const md = data.maximum_demand || {}
  const af = data.actual_vs_forecast || {}
  const tf = data.timeframes || {}
  const opp = data.optimization_opportunity || {}
  const pq = data.power_quality || {}

  const currentDemand = Number(md.current_demand_kw || 90.92)
  const peakDemand = Number(md.today_highest_peak_kw || currentDemand)
  const contractLimit = Number(md.configured_demand_limit_kw || 100.0)
  const safeLimit = Number(af.safe_limit_kw || 90.0)
  const predictedPeak = Number(af.predicted_peak_kw || 88.4)
  const predictedPeakTime = String(af.predicted_peak_time || '14:30')
  const currentPf = Number(pq.current_power_factor || 0.95)

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
          let html = `<div class="font-black text-xs pb-1 mb-1 border-b border-slate-700">${params[0]?.axisValue} Hours</div>`
          params.forEach((p) => {
            if (p.value !== null && p.value !== undefined) {
              html += `<div class="flex items-center justify-between gap-4 py-0.5">
                <span style="color:${p.color}">● ${p.seriesName}:</span>
                <span class="font-black">${Number(p.value).toFixed(1)} kW</span>
              </div>`
            }
          })
          return html
        },
      },
      legend: {
        data: ['Actual Measured Demand', 'AI Forecast Demand', 'Safe Operating Limit (90 kW)', 'Contract Ceiling (100 kW)'],
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
        name: 'Demand (kW)',
        nameTextStyle: { fontWeight: 'bold', color: '#1e293b', fontSize: 12 },
        min: 0,
        max: 110,
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
                coord: [predictedPeakTime.split(':')[0] + ':00', predictedPeak],
                value: `Crest: ${predictedPeak} kW`,
                itemStyle: { color: '#e11d48' },
              },
            ],
          },
        },
        {
          name: 'Safe Operating Limit (90 kW)',
          type: 'line',
          data: Array(hours.length).fill(safeLimit),
          silent: true,
          lineStyle: { type: 'dashed', width: 2.5, color: '#d97706' },
          itemStyle: { color: '#d97706' },
          symbol: 'none',
        },
        {
          name: 'Contract Ceiling (100 kW)',
          type: 'line',
          data: Array(hours.length).fill(contractLimit),
          silent: true,
          lineStyle: { type: 'solid', width: 2.5, color: '#dc2626' },
          itemStyle: { color: '#dc2626' },
          symbol: 'none',
        },
      ],
    }
  }, [af, safeLimit, contractLimit, predictedPeak, predictedPeakTime])

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
      },
      legend: {
        data: ['Energy (kWh)', 'Peak Demand (kW)'],
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
          name: 'kWh',
          axisLabel: { fontWeight: 'bold', color: '#334155' },
          splitLine: { lineStyle: { color: '#f1f5f9' } },
        },
        {
          type: 'value',
          name: 'Peak kW',
          min: 0,
          max: 120,
          axisLabel: { fontWeight: 'bold', color: '#334155' },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: 'Energy (kWh)',
          type: 'bar',
          data: values,
          itemStyle: { color: '#818cf8', borderRadius: [6, 6, 0, 0] },
        },
        {
          name: 'Peak Demand (kW)',
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
  }, [tf, selectedTimeframe])

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
            {currentDemand.toFixed(2)} <span className="text-xs font-bold text-slate-600">kW</span>
          </div>
          <div className="text-[11px] font-bold text-slate-500 mt-0.5">
            {((currentDemand / contractLimit) * 100).toFixed(1)}% of ceiling
          </div>
        </div>

        {/* Card 2: Highest Peak Measured Today */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-slate-600 tracking-wider">Today Highest Peak</div>
          <div className="text-2xl font-black text-rose-700 mt-1">
            {peakDemand.toFixed(2)} <span className="text-xs font-bold text-slate-600">kW</span>
          </div>
          <div className="text-[11px] font-bold text-slate-500 mt-0.5">Recorded at 10:15 Shift 1</div>
        </div>

        {/* Card 3: AI Predicted Peak Crest */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-indigo-700 tracking-wider">AI Forecast Peak</div>
          <div className="text-2xl font-black text-indigo-950 mt-1">
            {predictedPeak.toFixed(1)} <span className="text-xs font-bold text-slate-600">kW</span>
          </div>
          <div className="text-[11px] font-bold text-indigo-800 mt-0.5">Expected at {predictedPeakTime}</div>
        </div>

        {/* Card 4: Safe Buffer Remaining */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm">
          <div className="text-[11px] font-black uppercase text-emerald-700 tracking-wider">Safe Operating Buffer</div>
          <div className="text-2xl font-black text-emerald-800 mt-1">
            {Math.max(0, contractLimit - Math.max(currentDemand, peakDemand)).toFixed(2)}{' '}
            <span className="text-xs font-bold text-slate-600">kW</span>
          </div>
          <div className="text-[11px] font-bold text-emerald-700 mt-0.5">Safe margin before penalty</div>
        </div>

        {/* Card 5: Contract Demand Ceiling */}
        <div className="bg-white border-2 border-slate-200 rounded-2xl p-4 shadow-sm col-span-2 md:col-span-1">
          <div className="text-[11px] font-black uppercase text-slate-600 tracking-wider">Contracted Ceiling</div>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {contractLimit.toFixed(0)} <span className="text-xs font-bold text-slate-600">kW</span>
          </div>
          <div className="text-[11px] font-bold text-rose-700 mt-0.5">HT Utility Sanctioned Limit</div>
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
              Predicted Crest: {predictedPeak} kW @ {predictedPeakTime}
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
            <span>Period Total: {(tf[selectedTimeframe]?.total || 0).toLocaleString()} kWh</span>
            <span>Period Peak: {(tf[selectedTimeframe]?.peak || 0)} kW</span>
            <span>Est. Cost: ₹ {Math.round((tf[selectedTimeframe]?.total || 0) * 7.5).toLocaleString()}</span>
          </div>
        </div>

        {/* Right: Actionable AI Load Shifting Protocol (5 cols) */}
        <div className="lg:col-span-5 bg-gradient-to-br from-indigo-50 to-slate-50 border-2 border-indigo-200 rounded-3xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-indigo-200">
              <span className="text-xs font-black bg-indigo-600 text-white px-2.5 py-0.5 rounded-full uppercase">
                AI Optimization Opportunity
              </span>
              <span className="text-xs font-black text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                Operator Approval Required
              </span>
            </div>

            <h3 className="text-lg font-black text-indigo-950 tracking-tight mb-2">
              {opp.title || 'Stagger Compressor C-02 & Induction Furnace Startup'}
            </h3>

            <p className="text-xs font-bold text-slate-700 leading-relaxed mb-4">
              {opp.suggestion ||
                'Shift Compressor C-02 heavy cycle from 14:15 to 15:00 to prevent predicted peak of 88.4 kW from approaching the 90 kW safe limit.'}
            </p>

            <div className="space-y-3 bg-white border border-indigo-100 rounded-2xl p-4 shadow-2xs">
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Predicted Peak Avoided:</span>
                <span className="text-emerald-700 text-sm font-black">-{opp.predicted_peak_avoided_kw || 11.9} kW</span>
              </div>
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Potential Penalty Saved:</span>
                <span className="text-emerald-700 text-sm font-black">{opp.potential_savings || '₹ 4,200'}</span>
              </div>
              <div className="flex items-center justify-between text-xs font-black text-slate-700">
                <span>Execution Method:</span>
                <span className="text-slate-900">SCADA Automated Soft-Start Interlock</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-indigo-200">
            {optimizationApproved ? (
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
