"use client"
import React, { useState, useEffect } from 'react'

export default function SystemHardwarePage() {
  const [testMode, setTestMode] = useState(false);
  const [currentTime, setCurrentTime] = useState("--:--:--");
  useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString());
    const interval = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(interval);
  }, []);


  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm">
        <h1 className="text-xl lg:text-2xl font-bold font-bold text-slate-800 tracking-tight">System & Hardware Architecture</h1>
        <p className="text-lg font-bold text-slate-800 mt-1">Industrial Edge Deployment & Telemetry Ingestion</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* HARDWARE INTEGRATION PANEL */}
        <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm">
           <div className="flex justify-between items-center mb-6">
             <h3 className="font-semibold text-slate-800 uppercase tracking-wider text-base font-bold">Edge Hardware Integration</h3>
             <span className="px-2 py-0.5 rounded text-base font-bold font-bold bg-green-100 text-green-700">ONLINE</span>
           </div>
           
           <div className="space-y-6">
             {/* UNO Q */}
             <div className="border-2 border-slate-200 rounded-lg p-4 bg-slate-50 relative overflow-hidden">
               <div className="absolute right-0 top-0 h-full w-1 bg-green-500"></div>
               <div className="flex justify-between items-start mb-2">
                 <div>
                   <div className="font-bold text-slate-800 text-lg font-bold">Arduino UNO Q</div>
                   <div className="text-base font-bold text-slate-800">Edge Industrial Gateway</div>
                 </div>
                 <div className="text-base font-bold font-bold uppercase text-green-600 bg-green-100 px-2 py-1 rounded">Connected</div>
               </div>
               <div className="grid grid-cols-2 gap-4 mt-4 text-base font-bold">
                 <div>
                   <div className="text-slate-800 uppercase font-bold text-lg font-bold font-bold mb-1">Status</div>
                   <div className="font-mono text-slate-700">HEARTBEAT_OK</div>
                 </div>
                 <div>
                   <div className="text-slate-800 uppercase font-bold text-lg font-bold font-bold mb-1">Firmware</div>
                   <div className="font-mono text-slate-700">v2.1.4_EDGE_AI</div>
                 </div>
               </div>
             </div>

             {/* ENERGY METER */}
             <div className="border-2 border-slate-200 rounded-lg p-4 bg-slate-50 relative overflow-hidden">
               <div className="absolute right-0 top-0 h-full w-1 bg-teal-500"></div>
               <div className="flex justify-between items-start mb-2">
                 <div>
                   <div className="font-bold text-slate-800 text-lg font-bold">Factory Main Incomer</div>
                   <div className="text-base font-bold text-slate-800">Multifunction Energy Meter</div>
                 </div>
                 <div className="text-base font-bold font-bold uppercase text-teal-700 bg-blue-100 px-2 py-1 rounded">Simulated</div>
               </div>
               <div className="grid grid-cols-2 gap-4 mt-4 text-base font-bold">
                 <div>
                   <div className="text-slate-800 uppercase font-bold text-lg font-bold font-bold mb-1">Protocol</div>
                   <div className="font-mono text-slate-700">MODBUS RTU / RS-485</div>
                 </div>
                 <div>
                   <div className="text-slate-800 uppercase font-bold text-lg font-bold font-bold mb-1">Last Reading</div>
                   <div className="font-mono text-slate-700">{currentTime} IST</div>
                 </div>
               </div>
             </div>
           </div>
        </div>

        {/* DATA QUALITY ENGINE */}
        <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm flex flex-col">
           <h3 className="font-semibold text-slate-800 uppercase tracking-wider text-base font-bold mb-6">Data Quality Engine</h3>
           
           <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-green-50 border-2 border-green-200 p-4 rounded-lg">
                 <div className="text-base font-bold uppercase font-bold text-green-700 tracking-wider mb-1">Completeness</div>
                 <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-green-800">99.8%</div>
              </div>
              <div className="bg-slate-50 border-2 border-slate-200 p-4 rounded-lg">
                 <div className="text-base font-bold uppercase font-bold text-slate-800 tracking-wider mb-1">Latency</div>
                 <div className="text-xl lg:text-xl lg:text-2xl font-bold font-bold text-slate-800">42<span className="text-lg font-bold font-medium text-slate-800 ml-1">ms</span></div>
              </div>
           </div>

           <div className="space-y-4 flex-1">
              <div className="flex justify-between items-center text-base font-bold border-b border-slate-100 pb-2">
                 <span className="text-slate-800 font-medium">Timestamp Integrity</span>
                 <span className="font-mono text-green-600 font-bold">PASS</span>
              </div>
              <div className="flex justify-between items-center text-base font-bold border-b border-slate-100 pb-2">
                 <span className="text-slate-800 font-medium">Missing Values Handling</span>
                 <span className="font-mono text-slate-700">Linear Interpolation</span>
              </div>
              <div className="flex justify-between items-center text-base font-bold border-b border-slate-100 pb-2">
                 <span className="text-slate-800 font-medium">Outlier Rejection Rate</span>
                 <span className="font-mono text-slate-700">0.02%</span>
              </div>
              <div className="flex justify-between items-center text-base font-bold border-b border-slate-100 pb-2">
                 <span className="text-slate-800 font-medium">Telemetry Source</span>
                 <span className="font-mono text-teal-700 font-bold">SimulatorDataSource</span>
              </div>
           </div>
        </div>
      </div>

      {/* INDUSTRY TEST MODE */}
      <div className="bg-white p-4 rounded-xl border-2 border-neutral-200 shadow-sm">
         <div className="flex justify-between items-center mb-6">
           <div>
             <h3 className="font-semibold text-slate-800 uppercase tracking-wider text-base font-bold">Industry Test Mode</h3>
             <p className="text-base font-bold text-slate-800 mt-1">Calibration and validation environment for live factory deployment.</p>
           </div>
           <button 
              onClick={() => setTestMode(!testMode)}
              className={`px-4 py-2 rounded text-base font-bold font-bold uppercase transition-colors ${testMode ? 'bg-red-600 text-white text-slate-800 hover:bg-red-700' : 'bg-slate-50 text-slate-800 hover:bg-slate-700'}`}
           >
             {testMode ? 'Terminate Hardware Test' : 'Initialize Hardware Test'}
           </button>
         </div>

         {testMode ? (
           <div className="bg-white rounded-lg p-4 text-slate-700 font-mono text-base font-bold space-y-2 h-64 overflow-y-auto">
             <div className="text-green-400">[SYSTEM] Initializing industrial hardware bridge...</div>
             <div className="text-green-400">[UNO Q] Establishing serial connection on /dev/ttyUSB0... OK</div>
             <div className="text-green-400">[MODBUS] Probing Modbus RTU Address 0x01... OK</div>
             <div>[TELEMETRY] Register 30001 (Voltage): 415.2 V</div>
             <div>[TELEMETRY] Register 30007 (Current): 120.4 A</div>
             <div>[TELEMETRY] Register 30013 (Active Power): 86.5 kW</div>
             <div className="text-teal-500">[PIPELINE] Data aligned and injected into Data Quality Engine.</div>
             <div className="text-yellow-400">[AI] Forecasting engine synchronized to live datastream.</div>
             <div className="text-teal-500">[SYSTEM] Live hardware baseline capture in progress...</div>
             <div className="animate-pulse text-slate-800 mt-4">Waiting for continuous telemetry...</div>
           </div>
         ) : (
           <div className="bg-slate-50 rounded-lg border-2 border-slate-200 p-5 flex flex-col items-center justify-center text-center">
              <svg className="w-12 h-12 text-slate-700 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              <h4 className="font-bold text-slate-700 mb-2">Hardware Test Inactive</h4>
              <p className="text-lg font-bold text-slate-800 max-w-md">Activate test mode to connect directly to the Arduino UNO Q and begin capturing live Modbus telemetry for AI model calibration.</p>
           </div>
         )}
      </div>
    </div>
  )
}
