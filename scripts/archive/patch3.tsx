function LiveMeterView() {
  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20">
      
      {/* 1. GLOBAL HEADER */}
      <div className="flex justify-between items-end border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black tracking-tighter text-slate-900 uppercase">Plant 01 — Live Meter</h1>
          <p className="text-xs font-bold tracking-widest text-slate-400 uppercase mt-1">L&T Energy Meter / Arduino UNO Q</p>
        </div>
        <div className="flex gap-4 text-xs font-bold tracking-widest">
           <div className="flex items-center gap-2 px-3 py-1 bg-amber-100 text-amber-800 rounded border border-amber-200 uppercase text-[9px]">WAITING FOR LIVE TELEMETRY</div>
        </div>
      </div>

      <div className="flex items-center justify-center h-[500px] border border-dashed border-slate-300 rounded-xl bg-slate-50">
         <div className="text-center space-y-4">
            <div className="text-6xl text-slate-300 mb-6">●</div>
            <h2 className="text-lg font-black uppercase tracking-widest text-slate-700">Live Hardware Disconnected</h2>
            <p className="text-sm text-slate-500 max-w-md mx-auto">The physical L&T Energy Meter and Arduino UNO Q gateway are currently offline. Live telemetry is unavailable.</p>
            
            <div className="flex justify-center gap-4 mt-8">
               <div className="px-6 py-4 bg-white border border-slate-200 rounded-lg shadow-sm text-left">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Arduino UNO Q</div>
                  <div className="text-amber-600 font-black text-sm">OFFLINE</div>
               </div>
               <div className="px-6 py-4 bg-white border border-slate-200 rounded-lg shadow-sm text-left">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">L&T Meter RS485</div>
                  <div className="text-amber-600 font-black text-sm">OFFLINE</div>
               </div>
            </div>
            
            <button className="mt-8 px-6 py-2 bg-slate-900 text-white rounded font-bold uppercase text-xs tracking-widest hover:bg-slate-800">
               Test Connection
            </button>
         </div>
      </div>

    </div>
  )
}
