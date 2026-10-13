export default function LiveFactory({ pipeline, simulatedAction }: { pipeline: any, simulatedAction: boolean }) {
  const assets = pipeline.attribution || [];
  
  const getAsset = (name: string) => assets.find((a: any) => a.name.includes(name)) || { power: 0, status: 'OFF' };
  
  const compressor = getAsset('Compressor');
  const pump = getAsset('Pump');
  
  // Simulated action override
  const compStatus = simulatedAction ? 'OFF' : compressor.status;
  const compPower = simulatedAction ? 0 : compressor.power;

  return (
    <div className="h-full flex flex-col items-center justify-center font-mono">
       
       <div className="flex justify-center w-full mb-8">
          <div className="border-2 border-blue-500 rounded p-4 text-center bg-slate-50 shadow-[0_0_15px_rgba(59,130,246,0.5)]">
             <div className="text-base font-bold text-blue-300 font-bold uppercase mb-1">Grid / Main Meter</div>
             <div className="text-xl lg:text-2xl font-bold font-bold text-slate-800">{(simulatedAction ? pipeline.pipeline.current_demand - compressor.power : pipeline.pipeline.current_demand).toFixed(1)} kW</div>
          </div>
       </div>

       <div className="w-0.5 h-12 bg-teal-500 relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rounded-full animate-ping"></div>
       </div>

       <div className="w-3/4 h-0.5 bg-teal-500"></div>

       <div className="flex justify-between w-3/4 mt-8">
          {assets.map((asset: any, idx: number) => {
             const isFlex = !asset.protected;
             let p = asset.power;
             let s = 'RUNNING';
             if (simulatedAction && asset.name.includes('Compressor')) {
                 p = 0; s = 'OFF (DELAYED)';
             }
             if (p === 0 && !simulatedAction) s = 'IDLE';

             return (
               <div key={idx} className="flex flex-col items-center relative">
                  <div className="absolute -top-5 w-0.5 h-8 bg-teal-500"></div>
                  <div className={`border-2 rounded p-5 text-center w-32 ${isFlex ? 'border-amber-500/50 bg-amber-900/20' : 'border-slate-600 bg-slate-50'}`}>
                     <div className="text-lg font-bold font-bold text-slate-800 font-bold uppercase mb-1 truncate">{asset.name}</div>
                     <div className={`text-lg font-bold ${p > 0 ? 'text-slate-800' : 'text-slate-800'}`}>{p.toFixed(1)} kW</div>
                     <div className={`text-[8px] font-bold uppercase mt-2 ${p > 0 ? 'text-green-400' : 'text-slate-800'}`}>{s}</div>
                  </div>
               </div>
             )
          })}
       </div>
    </div>
  )
}
