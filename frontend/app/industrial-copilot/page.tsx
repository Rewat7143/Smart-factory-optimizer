"use client"
import React from 'react'
import { useCachePoller } from "@/hooks/useCachePoller"

export default function CopilotPage() {
  const data = useCachePoller('/copilot/insights', 5000);

  if (!data) return <div className="p-6 text-slate-800 font-bold">Loading Copilot...</div>

  const isOffline = data.status === 'OFFLINE';
  const insights = isOffline ? [] : (data.insights || []);

  return (
    <div className="p-6 font-mono space-y-6 flex flex-col h-full">
      <header className="mb-4">
        <h1 className="text-xl lg:text-2xl font-bold text-slate-800 uppercase tracking-tight">Industrial Copilot</h1>
        <p className="text-base font-bold tracking-widest text-slate-700 uppercase mt-1">Intelligent Operational Guidance</p>
      </header>
      
      {isOffline && (
        <div className="bg-red-600 text-white px-4 py-3 rounded-lg mb-4 flex items-center font-bold text-sm">
          <span className="w-2 h-2 rounded-full bg-white animate-pulse mr-3"></span>
          OFFLINE: Waiting for telemetry.
        </div>
      )}

      <div className="flex-1 bg-slate-100 border border-slate-300 rounded-xl shadow-inner p-6 overflow-y-auto space-y-4">
        {insights.length === 0 ? (
          <div className="text-slate-500 font-bold text-center mt-10 text-lg">
             {isOffline ? 'Hardware disconnected. Copilot offline.' : 'No urgent insights. System operating nominally.'}
          </div>
        ) : (
          insights.map((insight: any, idx: number) => {
             const isWarning = insight.type === 'WARNING' || insight.type === 'MAINTENANCE_ALERT';
             const isAction = insight.type === 'OPTIMIZATION_ACTION';
             
             let bg = 'bg-white border-slate-300';
             let text = 'text-slate-800';
             let badge = 'bg-slate-200 text-slate-800';
             
             if (isWarning) {
                bg = 'bg-red-50 border-red-300';
                text = 'text-red-900';
                badge = 'bg-red-600 text-white';
             } else if (isAction) {
                bg = 'bg-teal-50 border-teal-300';
                text = 'text-teal-900';
                badge = 'bg-teal-700 text-white';
             }

             return (
               <div key={idx} className={`border-2 rounded-xl shadow-md p-5 flex gap-4 ${bg}`}>
                 <div className="text-2xl mt-1">{isWarning ? '⚠️' : isAction ? '⚡' : '💡'}</div>
                 <div className="flex-1">
                   <div className={`inline-block px-2 py-1 rounded text-xs font-bold uppercase tracking-widest mb-2 ${badge}`}>
                      {insight.type.replace('_', ' ')}
                   </div>
                   <div className={`text-xl font-bold ${text}`}>
                      {insight.content}
                   </div>
                   {insight.confidence && (
                      <div className="mt-2 text-sm font-bold text-slate-500">
                         AI Confidence: {(insight.confidence * 100).toFixed(1)}%
                      </div>
                   )}
                 </div>
               </div>
             )
          })
        )}
      </div>
    </div>
)
}
