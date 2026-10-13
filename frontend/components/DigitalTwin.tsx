"use client"
import React from 'react'
import { useCachePoller } from "@/hooks/useCachePoller"

export function DigitalTwin() {
  const factory = useCachePoller('/factory/state', 2000);

  if (!factory) return <div className="text-slate-800 text-lg font-bold">Loading Digital Twin...</div>;

  const categories = ['Production', 'Utility', 'HVAC', 'Storage', 'Auxiliary'];

  return (
    <div className="bg-white p-4 rounded-xl border-2 border-neutral-200">
      <div className="flex justify-between items-center mb-8">
        <h3 className="font-semibold text-slate-800">Factory Bus: Main Meter</h3>
        <div className="text-xl lg:text-2xl font-bold text-slate-800">
          {factory.live_status === 'OFFLINE' ? 'OFFLINE' : `${(factory.current_demand_kw || 0).toFixed(1)} kW`}
        </div>
      </div>
      
      {!factory.submetering_available && (
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-8">
          <p className="text-amber-800 text-sm font-semibold">
            Submetering Unavailable
          </p>
          <p className="text-amber-700 text-sm mt-1">
            Machine-level power telemetry is not available from the current data source. 
            Smart submeters (e.g., Modbus RS485 energy meters) must be installed on individual asset panels to view live power draw per machine.
          </p>
        </div>
      )}

      <div className="relative border-l-4 border-slate-300 ml-4 pl-8 space-y-10 py-4">
        {categories.map(category => {
          const catAssets = factory.assets?.filter((a: any) => a.category === category) || [];
          if (catAssets.length === 0) return null;
          
          return (
            <div key={category} className="relative">
              <div className="absolute -left-10 top-5 w-10 h-1 bg-slate-300"></div>
              <h4 className="text-base font-bold text-slate-800 uppercase tracking-widest mb-4">{category} Bus</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {catAssets.map((asset: any) => (
                  <AssetBlock key={asset.asset_id} asset={asset} submetering={factory.submetering_available} />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function AssetBlock({ asset, submetering }: { asset: any, submetering: boolean }) {
  const isRunning = asset.status === 'RUNNING' || asset.status === 'STARTING';
  const isFault = asset.status === 'FAULT';
  const isUnknown = asset.status === 'UNKNOWN';
  
  let statusColor = 'bg-slate-50 text-slate-800 border-slate-200';
  if (isRunning) statusColor = 'bg-green-50 text-green-700 border-green-200';
  if (isFault) statusColor = 'bg-red-50 text-red-700 border-red-200';
  if (isUnknown) statusColor = 'bg-neutral-100 text-neutral-500 border-neutral-200 opacity-70';

  return (
    <div className={`p-4 rounded-lg border-2 flex flex-col justify-between hover:shadow-md transition-shadow ${statusColor}`}>
      <div className="flex justify-between items-start mb-2">
        <div className="font-medium text-lg font-bold">{asset.name}</div>
        <div className={`text-xs font-bold uppercase px-2 py-1 rounded ${isRunning ? 'bg-green-200 text-green-800' : isUnknown ? 'bg-neutral-200 text-neutral-600' : 'bg-slate-200 text-slate-800'}`}>
          {asset.status}
        </div>
      </div>
      
      <div className="mt-4 flex justify-between items-end">
        <div>
          <div className="text-xs font-bold opacity-70 mb-1">CURRENT POWER</div>
          <div className="font-bold">
            {submetering && asset.power_kw !== null && asset.power_kw !== undefined ? `${asset.power_kw.toFixed(1)} kW` : 'No Sensor'}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs font-bold opacity-70 mb-1">CRITICALITY</div>
          <div className="font-semibold text-sm">{asset.criticality}</div>
        </div>
      </div>
    </div>
  )
}
