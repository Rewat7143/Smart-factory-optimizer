"use client"
import React, { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'

export default function HistoryExplorerPage() {
  const [startTime, setStartTime] = useState<string>('')
  const [endTime, setEndTime] = useState<string>('')
  const [source, setSource] = useState<string>('')
  
  const [records, setRecords] = useState<any[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(false)
  
  const [measurement, setMeasurement] = useState<string>('active_power_kw')
  const [forecastHorizon, setForecastHorizon] = useState<string>('15m')
  const [forecastResult, setForecastResult] = useState<any>(null)

  // Initialize dates to last 3 days
  useEffect(() => {
     const end = new Date()
     const start = new Date(end.getTime() - 72 * 60 * 60 * 1000)
     setEndTime(end.toISOString().substring(0, 16))
     setStartTime(start.toISOString().substring(0, 16))
  }, [])

  const loadData = async () => {
     if (!startTime || !endTime) return
     setIsLoading(true)
     setForecastResult(null)
     
     // Construct proper UTC timestamps
     const startUtc = new Date(startTime).toISOString()
     const endUtc = new Date(endTime).toISOString()
     
     let url = `${typeof window !== 'undefined' ? window.location.protocol + '//' + window.location.hostname + ':8000/api' : 'http://localhost:8000/api'}/telemetry/history_explorer?start_time=${startUtc}&end_time=${endUtc}&limit=5000`
     if (source) url += `&source=${source}`
     
     try {
        const res = await fetch(url)
        const data = await res.json()
        setRecords(data.records || [])
        setTotalCount(data.total_count || 0)
        
        // After loading history, if source is explicitly HISTORICAL_TEST or something, we can run a forecast!
        if (data.records && data.records.length > 100) {
           await runForecast(data.records)
        }
     } catch (e) {
        console.error(e)
     } finally {
        setIsLoading(false)
     }
  }
  
  const runForecast = async (histRecords: any[]) => {
      try {
         // Call a backend endpoint to run forecast on this specific history slice
         const res = await fetch(`${typeof window !== 'undefined' ? window.location.protocol + '//' + window.location.hostname + ':8000/api' : 'http://localhost:8000/api'}/forecast/custom`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ history: histRecords })
         })
         const data = await res.json()
         if (data.forecast) {
            setForecastResult(data.forecast)
         }
      } catch (e) {
         console.error("Forecast failed on custom history", e)
      }
  }

  const handleExport = () => {
      const headers = "timestamp,source,watts_total,watts_r,watts_y,watts_b,pf_avg,pf_r,pf_y,pf_b,va_total,va_r,va_y,va_b,v_ll_avg,v_ry,v_yb,v_br,v_ln_avg,v_r,v_y,v_b,current_total,current_r,current_y,current_b,frequency,energy_wh,energy_vah,load_hours";
      const rows = records.map(r => [
          r.timestamp,
          r.data_source,
          r.watts_total ?? ((r.active_power_kw || 0) * 1000),
          r.watts_r ?? '',
          r.watts_y ?? '',
          r.watts_b ?? '',
          r.pf_avg ?? r.power_factor ?? '',
          r.pf_r ?? '',
          r.pf_y ?? '',
          r.pf_b ?? '',
          r.va_total ?? '',
          r.va_r ?? '',
          r.va_y ?? '',
          r.va_b ?? '',
          r.v_ll_avg ?? '',
          r.v_ry ?? '',
          r.v_yb ?? '',
          r.v_br ?? '',
          r.v_ln_avg ?? r.voltage_v ?? '',
          r.v_r ?? '',
          r.v_y ?? '',
          r.v_b ?? '',
          r.current_total ?? r.current_a ?? '',
          r.current_r ?? '',
          r.current_y ?? '',
          r.current_b ?? '',
          r.frequency ?? r.frequency_hz ?? '',
          r.energy_wh ?? ((r.energy_kwh || 0) * 1000),
          r.energy_vah ?? '',
          r.load_hours ?? ''
      ].join(","));
      const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows.join("\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "telemetry_27params_history.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  }

  const resetFilters = () => {
     const end = new Date()
     const start = new Date(end.getTime() - 72 * 60 * 60 * 1000)
     setEndTime(end.toISOString().substring(0, 16))
     setStartTime(start.toISOString().substring(0, 16))
     setSource('')
     setRecords([])
     setTotalCount(0)
     setForecastResult(null)
  }

  const timestamps = records.map(r => r.timestamp)
  let values = []
  if (measurement === 'active_power_kw') values = records.map(r => r.active_power_kw ?? (r.watts_total ? r.watts_total / 1000 : 0))
  else if (measurement === 'watts_total') values = records.map(r => r.watts_total ?? ((r.active_power_kw || 0) * 1000))
  else if (measurement === 'watts_r') values = records.map(r => r.watts_r ?? 0)
  else if (measurement === 'watts_y') values = records.map(r => r.watts_y ?? 0)
  else if (measurement === 'watts_b') values = records.map(r => r.watts_b ?? 0)
  else if (measurement === 'va_total') values = records.map(r => r.va_total ?? 0)
  else if (measurement === 'voltage_v') values = records.map(r => r.voltage_v ?? r.v_ln_avg ?? 0)
  else if (measurement === 'v_r') values = records.map(r => r.v_r ?? 0)
  else if (measurement === 'v_y') values = records.map(r => r.v_y ?? 0)
  else if (measurement === 'v_b') values = records.map(r => r.v_b ?? 0)
  else if (measurement === 'v_ll_avg') values = records.map(r => r.v_ll_avg ?? 0)
  else if (measurement === 'current_a') values = records.map(r => r.current_a ?? r.current_total ?? 0)
  else if (measurement === 'current_r') values = records.map(r => r.current_r ?? 0)
  else if (measurement === 'current_y') values = records.map(r => r.current_y ?? 0)
  else if (measurement === 'current_b') values = records.map(r => r.current_b ?? 0)
  else if (measurement === 'power_factor') values = records.map(r => r.power_factor ?? r.pf_avg ?? 0)
  else if (measurement === 'frequency') values = records.map(r => r.frequency ?? r.frequency_hz ?? 50)
  else if (measurement === 'energy_wh') values = records.map(r => r.energy_wh ?? ((r.energy_kwh || 0) * 1000))
  else if (measurement === 'load_hours') values = records.map(r => r.load_hours ?? 1420)
  
  const yName = measurement.includes('power') || measurement.includes('watts') ? 'Power' : measurement.includes('volt') || measurement.startsWith('v_') ? 'Voltage (V)' : measurement.includes('current') ? 'Current (A)' : measurement.includes('va') ? 'Apparent Power (VA)' : measurement.includes('freq') ? 'Hz' : measurement.includes('energy') ? 'Wh' : 'Value'
  
  const forecastPoint = forecastResult ? forecastResult.predicted_kw : null
  const forecastTime = forecastResult ? forecastResult.timestamp : null
  
  const chartTimestamps = [...timestamps]
  const chartValues = [...values]
  const forecastSeries = Array(timestamps.length).fill(null)
  
  if (forecastPoint !== null && measurement === 'active_power_kw') {
      chartTimestamps.push(forecastTime)
      chartValues.push(null) // no historical value for future
      forecastSeries.push(forecastPoint)
      forecastSeries[forecastSeries.length - 2] = values[values.length - 1] // link it
  }

  const chartOption = {
    animation: false,
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'line' }
    },
    legend: { data: ['History', 'Forecast'], bottom: 0, textStyle: { fontWeight: 'bold' } },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, bottom: 40, height: 20 }
    ],
    xAxis: { 
      type: 'category', 
      data: chartTimestamps, 
      axisLabel: { 
        formatter: (val: string) => val ? (val.includes('T') ? val.split('T')[1].substring(0,5) : String(val).substring(0,10)) : ''
      }
    },
    yAxis: { 
      type: 'value', 
      name: yName,
      scale: true
    },
    series: [
      { 
        name: 'History', 
        type: 'line', 
        data: chartValues, 
        smooth: true, 
        showSymbol: false, 
        lineStyle: { color: '#0f766e', width: 2 }
      },
      {
        name: 'Forecast',
        type: 'line',
        data: forecastSeries,
        smooth: true,
        showSymbol: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#9333ea', width: 3, type: 'dashed' },
        itemStyle: { color: '#9333ea' }
      }
    ],
    grid: { left: '5%', right: '5%', bottom: '20%', top: '10%', containLabel: true }
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
        <header className="mb-6">
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Historical Explorer</h1>
          <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2 border-b border-slate-300 pb-4">Query, Analyze, and Forecast Test Histories</p>
        </header>

        {/* FILTERS */}
        <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm space-y-4">
           <div className="flex flex-wrap gap-6 items-end">
              <div>
                 <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Start Time (Local)</div>
                 <input type="datetime-local" value={startTime} onChange={e => setStartTime(e.target.value)} className="border-2 border-slate-200 rounded px-3 py-1.5 text-sm font-bold outline-none" />
              </div>
              <div>
                 <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">End Time (Local)</div>
                 <input type="datetime-local" value={endTime} onChange={e => setEndTime(e.target.value)} className="border-2 border-slate-200 rounded px-3 py-1.5 text-sm font-bold outline-none" />
              </div>
              <div>
                 <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Source</div>
                 <select value={source} onChange={e => setSource(e.target.value)} className="border-2 border-slate-200 rounded px-3 py-1.5 text-sm font-bold outline-none">
                    <option value="">ALL SOURCES</option>
                    <option value="HISTORICAL_TEST">HISTORICAL_TEST</option>
                    <option value="SIMULATED_RASPI">SIMULATED_RASPI</option>
                    <option value="SIMULATOR">SIMULATOR</option>
                    <option value="RASPBERRY_PI">RASPBERRY_PI</option>
                 </select>
              </div>
              <div>
                 <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Measurement</div>
                 <select value={measurement} onChange={e => setMeasurement(e.target.value)} className="border-2 border-slate-200 rounded px-3 py-1.5 text-sm font-bold outline-none bg-slate-50">
                    <optgroup label="Active Power">
                       <option value="active_power_kw">Watts Total (kW)</option>
                       <option value="watts_total">Watts Total (W)</option>
                       <option value="watts_r">Watts Phase R (W)</option>
                       <option value="watts_y">Watts Phase Y (W)</option>
                       <option value="watts_b">Watts Phase B (W)</option>
                    </optgroup>
                    <optgroup label="Apparent Power">
                       <option value="va_total">VA Total (VA)</option>
                    </optgroup>
                    <optgroup label="Voltage">
                       <option value="voltage_v">Voltage LN Avg (V)</option>
                       <option value="v_r">Voltage Phase R (V)</option>
                       <option value="v_y">Voltage Phase Y (V)</option>
                       <option value="v_b">Voltage Phase B (V)</option>
                       <option value="v_ll_avg">Voltage LL Avg (V)</option>
                    </optgroup>
                    <optgroup label="Current">
                       <option value="current_a">Current Total (A)</option>
                       <option value="current_r">Current Phase R (A)</option>
                       <option value="current_y">Current Phase Y (A)</option>
                       <option value="current_b">Current Phase B (A)</option>
                    </optgroup>
                    <optgroup label="Power Factor & Frequency">
                       <option value="power_factor">Power Factor Avg</option>
                       <option value="frequency">Frequency (Hz)</option>
                    </optgroup>
                    <optgroup label="Energy & Counters">
                       <option value="energy_wh">Energy (Wh)</option>
                       <option value="load_hours">Load Hours (hrs)</option>
                    </optgroup>
                 </select>
              </div>
              
              <div className="flex gap-2">
                 <button onClick={loadData} className="bg-teal-700 text-white font-bold tracking-widest text-xs px-6 py-2.5 rounded shadow hover:bg-teal-800 transition">
                    APPLY FILTERS
                 </button>
                 <button onClick={resetFilters} className="bg-slate-200 text-slate-700 font-bold tracking-widest text-xs px-6 py-2.5 rounded shadow hover:bg-slate-300 transition">
                    RESET
                 </button>
                 <button onClick={handleExport} disabled={records.length === 0} className="bg-indigo-600 disabled:opacity-50 text-white font-bold tracking-widest text-xs px-6 py-2.5 rounded shadow hover:bg-indigo-700 transition">
                    EXPORT CSV
                 </button>
              </div>
           </div>
        </div>

        {/* METRICS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
           <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
              <div className="text-xs font-semibold uppercase text-slate-500 tracking-widest mb-1">Records Loaded</div>
              <div className="text-2xl font-bold tracking-tight text-slate-800">{records.length} / {totalCount}</div>
           </div>
           <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
              <div className="text-xs font-semibold uppercase text-slate-500 tracking-widest mb-1">Forecast Status</div>
              <div className={`text-xl font-bold tracking-tight ${forecastResult ? 'text-purple-700' : 'text-slate-400'}`}>
                 {isLoading ? 'ANALYZING...' : forecastResult ? 'COMPUTED' : 'UNAVAILABLE'}
              </div>
           </div>
           <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
              <div className="text-xs font-semibold uppercase text-slate-500 tracking-widest mb-1">Predicted Peak</div>
              <div className={`text-2xl font-bold tracking-tight ${forecastResult ? 'text-purple-700' : 'text-slate-400'}`}>
                 {forecastResult ? `${forecastResult.predicted_kw.toFixed(1)} kW` : 'N/A'}
              </div>
           </div>
           <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
              <div className="text-xs font-semibold uppercase text-slate-500 tracking-widest mb-1">Model Compatibility</div>
              <div className={`text-lg font-bold tracking-tight uppercase ${records.length >= 1440 ? 'text-teal-700' : 'text-amber-600'}`}>
                 {records.length >= 1440 ? 'SATISFIED (24H+)' : 'INSUFFICIENT'}
              </div>
           </div>
        </div>

        {/* CHART */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm min-h-[500px]">
           {isLoading ? (
              <div className="flex items-center justify-center h-[450px] font-bold text-slate-400 tracking-widest uppercase">Fetching Historical Data...</div>
           ) : records.length === 0 ? (
              <div className="flex items-center justify-center h-[450px] font-bold text-slate-400 tracking-widest uppercase">No Records Found for the Selected Period</div>
           ) : (
              <ReactECharts option={chartOption} style={{ height: '500px', width: '100%' }} />
           )}
        </div>

    </div>
  )
}
