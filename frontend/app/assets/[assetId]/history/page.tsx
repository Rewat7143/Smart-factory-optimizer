"use client"
import React, { useEffect, useState, useMemo } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import ReactECharts from 'echarts-for-react'
import { getApiBaseUrl } from '@/lib/config'

export default function AssetHistoryPage() {
  const params = useParams()
  const rawId = (params?.assetId as string) || ''
  const assetId = decodeURIComponent(rawId).trim().toUpperCase()

  const [historyData, setHistoryData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [preset, setPreset] = useState<string>('today')
  const [startTime, setStartTime] = useState<string>('')
  const [endTime, setEndTime] = useState<string>('')
  const [activeMetric, setActiveMetric] = useState<'power' | 'voltage_current' | 'pf_freq'>('power')

  // Pagination for raw records
  const [tablePage, setTablePage] = useState<number>(1)
  const pageSize = 15

  const baseUrl = getApiBaseUrl()

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const query = new URLSearchParams()
      query.append('preset', preset)
      if (preset === 'custom' && startTime && endTime) {
        query.append('start_time', startTime)
        query.append('end_time', endTime)
      }
      query.append('limit', '300')

      const res = await fetch(`${baseUrl}/assets/${assetId}/history?${query.toString()}`)
      if (!res.ok) throw new Error(`History unavailable (${res.status})`)
      const json = await res.json()
      setHistoryData(json)
      setError(null)
    } catch (e: any) {
      setError(e.message || 'Failed to fetch historical telemetry.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!assetId) return
    fetchHistory()
  }, [assetId, preset])

  // Handle CSV Export
  const handleExportCsv = () => {
    if (!historyData || !historyData.raw_records || historyData.raw_records.length === 0) {
      alert('No records available to export for this window.')
      return
    }

    const headers = ['Timestamp', 'Active Power (kW)', 'Voltage (V)', 'Current (A)', 'Power Factor', 'Frequency (Hz)']
    const rows = historyData.raw_records.map((r: any) => [
      r.timestamp,
      r.active_power_kw || '',
      r.voltage_v || '',
      r.current_a || '',
      r.power_factor || '',
      r.frequency_hz || ''
    ])

    const csvContent = [headers.join(','), ...rows.map((row: any[]) => row.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `History_${assetId}_${preset}_${new Date().toISOString().substring(0, 10)}.csv`
    link.click()
  }

  // ECharts Chart Configuration
  const chartOption = useMemo(() => {
    if (!historyData || !historyData.timeline || historyData.timeline.length === 0) {
      return {}
    }

    const times = historyData.timeline.map((t: string) => {
      try {
        const d = new Date(t)
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      } catch {
        return t
      }
    })

    if (activeMetric === 'power') {
      return {
        animation: false,
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'line' },
          backgroundColor: '#0F172A',
          borderColor: '#334155',
          textStyle: { color: '#F8FAFC', fontFamily: 'monospace' }
        },
        grid: { top: 30, right: 20, bottom: 40, left: 60 },
        xAxis: {
          type: 'category',
          data: times,
          axisLine: { lineStyle: { color: '#CBD5E1' } },
          axisLabel: { color: '#475569', fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: 'kW',
          axisLine: { lineStyle: { color: '#CBD5E1' } },
          axisLabel: { color: '#475569', fontSize: 10 },
          splitLine: { lineStyle: { color: '#F1F5F9' } }
        },
        series: [
          {
            name: 'PCC Active Power',
            type: 'line',
            data: historyData.power_kw,
            smooth: true,
            lineStyle: { width: 3, color: '#0F766E' },
            itemStyle: { color: '#0F766E' },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(15, 118, 110, 0.25)' },
                  { offset: 1, color: 'rgba(15, 118, 110, 0.0)' }
                ]
              }
            }
          }
        ]
      }
    }

    if (activeMetric === 'voltage_current') {
      return {
        animation: false,
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'line' },
          backgroundColor: '#0F172A',
          textStyle: { color: '#F8FAFC', fontFamily: 'monospace' }
        },
        grid: { top: 30, right: 60, bottom: 40, left: 60 },
        xAxis: {
          type: 'category',
          data: times,
          axisLabel: { color: '#475569', fontSize: 10 }
        },
        yAxis: [
          {
            type: 'value',
            name: 'Voltage (V)',
            min: 210,
            max: 250,
            axisLabel: { color: '#475569', fontSize: 10 }
          },
          {
            type: 'value',
            name: 'Current (A)',
            axisLabel: { color: '#475569', fontSize: 10 }
          }
        ],
        series: [
          {
            name: 'Voltage',
            type: 'line',
            data: historyData.voltage_v,
            lineStyle: { width: 2, color: '#4F46E5' },
            itemStyle: { color: '#4F46E5' }
          },
          {
            name: 'Current',
            type: 'line',
            yAxisIndex: 1,
            data: historyData.current_a,
            lineStyle: { width: 2, color: '#D97706' },
            itemStyle: { color: '#D97706' }
          }
        ]
      }
    }

    // Power Factor & Frequency
    return {
      animation: false,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
        backgroundColor: '#0F172A',
        textStyle: { color: '#F8FAFC', fontFamily: 'monospace' }
      },
      grid: { top: 30, right: 60, bottom: 40, left: 60 },
      xAxis: {
        type: 'category',
        data: times,
        axisLabel: { color: '#475569', fontSize: 10 }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Power Factor',
          min: 0.8,
          max: 1.0,
          axisLabel: { color: '#475569', fontSize: 10 }
        },
        {
          type: 'value',
          name: 'Frequency (Hz)',
          min: 49.5,
          max: 50.5,
          axisLabel: { color: '#475569', fontSize: 10 }
        }
      ],
      series: [
        {
          name: 'Power Factor',
          type: 'line',
          data: historyData.power_factor,
          lineStyle: { width: 2, color: '#059669' },
          itemStyle: { color: '#059669' }
        },
        {
          name: 'Grid Frequency',
          type: 'line',
          yAxisIndex: 1,
          data: historyData.frequency_hz,
          lineStyle: { width: 2, color: '#6366F1' },
          itemStyle: { color: '#6366F1' }
        }
      ]
    }
  }, [historyData, activeMetric])

  const rawRecords = historyData?.raw_records || []
  const paginatedRecords = rawRecords.slice((tablePage - 1) * pageSize, tablePage * pageSize)
  const totalTablePages = Math.ceil(rawRecords.length / pageSize) || 1

  return (
    <div className="max-w-[1400px] mx-auto space-y-4 sm:space-y-6 font-mono text-slate-800 pb-20 p-3 sm:p-4 md:p-6 w-full min-w-0">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-slate-300 pb-4 gap-3 sm:gap-4">
        <div className="w-full md:w-auto">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1">
            <span className="bg-slate-900 text-white font-mono text-xs font-black px-2.5 py-0.5 rounded uppercase">
              {assetId}
            </span>
            <span className="text-[11px] sm:text-xs font-bold text-slate-500 uppercase tracking-widest">
              Historical Telemetry Service
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-slate-900 uppercase break-words">
            Asset Energy History
          </h1>
          <p className="text-[11px] sm:text-xs font-semibold tracking-widest text-slate-500 uppercase mt-1">
            Auditable Database Records &bull; Point of Common Coupling Time Series
          </p>
        </div>

        <div className="grid grid-cols-2 sm:flex items-center gap-2 w-full md:w-auto">
          <button
            onClick={handleExportCsv}
            disabled={rawRecords.length === 0}
            className="flex items-center justify-center text-center bg-emerald-50 border border-emerald-300 hover:bg-emerald-100 text-emerald-950 font-bold text-xs px-3.5 py-2.5 rounded-xl transition-all shadow-xs gap-1.5 uppercase disabled:opacity-50 min-h-[44px]"
          >
            <span>📥</span>
            <span>Export CSV</span>
          </button>

          <Link
            href={`/assets/${assetId}`}
            className="flex items-center justify-center text-center bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs px-3.5 py-2.5 rounded-xl transition-all shadow-xs min-h-[44px]"
          >
            &larr; Energy Passport
          </Link>
        </div>
      </div>

      {/* FILTER & RANGE SELECTOR BAR */}
      <div className="bg-white border border-slate-300 rounded-xl p-3.5 sm:p-4 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        {/* Preset Range Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 max-w-full no-scrollbar w-full md:w-auto">
          {[
            { id: 'today', label: 'Today' },
            { id: '24h', label: 'Last 24h' },
            { id: '7d', label: '7 Days' },
            { id: 'custom', label: 'Custom' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setPreset(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all shrink-0 min-h-[38px] ${
                preset === tab.id
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Custom Date Pickers */}
        {preset === 'custom' && (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 text-xs font-bold w-full md:w-auto">
            <div className="flex-1">
              <input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-xs text-slate-900"
              />
            </div>
            <span className="hidden sm:inline text-center">to</span>
            <div className="flex-1">
              <input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-xs text-slate-900"
              />
            </div>
            <button
              onClick={fetchHistory}
              className="bg-teal-700 hover:bg-teal-800 text-white px-4 py-2 rounded-lg text-xs font-bold uppercase min-h-[38px]"
            >
              Apply
            </button>
          </div>
        )}

        {/* Metric Switcher */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg w-full md:w-auto overflow-x-auto justify-between sm:justify-start">
          <button
            onClick={() => setActiveMetric('power')}
            className={`flex-1 sm:flex-none px-2.5 py-1.5 rounded text-[11px] font-bold uppercase tracking-wider min-h-[36px] ${
              activeMetric === 'power' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-600'
            }`}
          >
            Active Power
          </button>
          <button
            onClick={() => setActiveMetric('voltage_current')}
            className={`flex-1 sm:flex-none px-2.5 py-1.5 rounded text-[11px] font-bold uppercase tracking-wider min-h-[36px] ${
              activeMetric === 'voltage_current' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-600'
            }`}
          >
            V / Current
          </button>
          <button
            onClick={() => setActiveMetric('pf_freq')}
            className={`flex-1 sm:flex-none px-2.5 py-1.5 rounded text-[11px] font-bold uppercase tracking-wider min-h-[36px] ${
              activeMetric === 'pf_freq' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-600'
            }`}
          >
            PF / Freq
          </button>
        </div>
      </div>

      {/* CHART CONTAINER */}
      <div className="bg-white border border-slate-300 rounded-xl p-3.5 sm:p-5 shadow-sm space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs font-bold text-slate-700 border-b border-slate-100 pb-2 gap-1">
          <div className="uppercase tracking-wider">
            {activeMetric === 'power' && '⚡ PCC Bus Active Power Profile (kW)'}
            {activeMetric === 'voltage_current' && '🔌 Voltage (V) & Total Current (A)'}
            {activeMetric === 'pf_freq' && '⚙️ Power Factor & Grid Frequency (Hz)'}
          </div>
          <div className="text-slate-400 font-mono text-[11px]">
            {historyData?.records_returned || 0} points plotted
          </div>
        </div>

        {loading ? (
          <div className="h-[280px] sm:h-[360px] flex items-center justify-center text-slate-400 font-bold text-xs">
            Querying SQLite telemetry database...
          </div>
        ) : historyData?.timeline?.length === 0 ? (
          <div className="h-[280px] sm:h-[360px] flex items-center justify-center text-slate-400 font-bold text-xs">
            No telemetry records found for this time window.
          </div>
        ) : (
          <ReactECharts
            option={chartOption}
            style={{ height: '340px', width: '100%' }}
          />
        )}
      </div>

      {/* FILTERED RECORDS TABLE & MOBILE CARDS */}
      <div className="bg-white border border-slate-300 rounded-xl shadow-sm overflow-hidden space-y-2">
        <div className="p-3.5 sm:p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Persistent Telemetry Record Sample ({rawRecords.length} records in range)
          </h3>
          <span className="text-[11px] text-slate-500 font-medium font-mono">
            Source: telemetry.db
          </span>
        </div>

        {rawRecords.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs font-bold">
            No records in range.
          </div>
        ) : (
          <>
            {/* MOBILE RECORD CARDS (Visible only on mobile) */}
            <div className="md:hidden divide-y divide-slate-100 p-2 space-y-2">
              {paginatedRecords.map((r: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-2 font-mono text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-slate-600 font-bold" suppressHydrationWarning>
                      {new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                    <span className="font-black text-teal-800 text-sm">
                      {(r.active_power_kw || 0).toFixed(1)} kW
                    </span>
                  </div>

                  <div className="grid grid-cols-4 gap-2 text-[10px] text-slate-600 pt-1.5 border-t border-slate-200">
                    <div>
                      <span className="text-slate-400 block">V</span>
                      <span className="font-bold text-slate-800">{(r.voltage_v || 230).toFixed(0)}V</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Curr</span>
                      <span className="font-bold text-slate-800">{(r.current_a || 0).toFixed(1)}A</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">PF</span>
                      <span className="font-bold text-slate-800">{(r.power_factor || 0.95).toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Freq</span>
                      <span className="font-bold text-slate-800">{(r.frequency_hz || 50).toFixed(1)}Hz</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* DESKTOP AUDIT TABLE (Visible on md+ screens) */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider">
                  <tr>
                    <th className="p-3">Timestamp</th>
                    <th className="p-3">Active Power (kW)</th>
                    <th className="p-3">Voltage (V)</th>
                    <th className="p-3">Current (A)</th>
                    <th className="p-3">Power Factor</th>
                    <th className="p-3">Frequency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {paginatedRecords.map((r: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-3 font-bold text-slate-700" suppressHydrationWarning>
                        {new Date(r.timestamp).toLocaleString()}
                      </td>
                      <td className="p-3 font-bold text-teal-800">
                        {(r.active_power_kw || 0).toFixed(1)} kW
                      </td>
                      <td className="p-3 text-slate-700">
                        {(r.voltage_v || 230).toFixed(1)} V
                      </td>
                      <td className="p-3 text-slate-700">
                        {(r.current_a || 0).toFixed(1)} A
                      </td>
                      <td className="p-3 text-slate-700">
                        {(r.power_factor || 0.95).toFixed(3)}
                      </td>
                      <td className="p-3 text-slate-700">
                        {(r.frequency_hz || 50).toFixed(2)} Hz
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {totalTablePages > 1 && (
          <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs font-bold text-slate-600">
            <div>
              Page {tablePage} of {totalTablePages}
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setTablePage((p) => Math.max(1, p - 1))}
                disabled={tablePage === 1}
                className="min-h-[38px] px-3 py-1.5 rounded-lg bg-white border border-slate-300 disabled:opacity-40"
              >
                &larr; Prev
              </button>
              <button
                onClick={() => setTablePage((p) => Math.min(totalTablePages, p + 1))}
                disabled={tablePage === totalTablePages}
                className="min-h-[38px] px-3 py-1.5 rounded-lg bg-white border border-slate-300 disabled:opacity-40"
              >
                Next &rarr;
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  )
}
