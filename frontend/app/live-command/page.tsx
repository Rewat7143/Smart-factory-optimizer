"use client"
import React, { useEffect, useState, useRef } from 'react'
import { useCachePoller } from "@/hooks/useCachePoller"

export default function LiveCommandPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [audioUnlocked, setAudioUnlocked] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio('/alarm.mp3'); // Assuming some asset exists or browser default beep
    // We can also synthesize a beep
  }, []);

  const fetchEvents = async () => {
    try {
      const apiUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))
      const res = await fetch(`${apiUrl}/control/events`);
      if (res.ok) {
        const json = await res.json();
        setEvents(json.events || []);
        
        // Play audio if there's an unacknowledged awaiting_approval event
        const activeAlarm = json.events.some((e: any) => e.status === 'AWAITING_APPROVAL' && !e.acknowledged);
        if (activeAlarm && audioUnlocked && audioRef.current) {
          audioRef.current.play().catch(() => console.log('Audio play prevented'));
        }
      }
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, [audioUnlocked]);

  const unlockAudio = () => {
    setAudioUnlocked(true);
    if (audioRef.current) {
      audioRef.current.volume = 0;
      audioRef.current.play().then(() => {
        audioRef.current!.pause();
        audioRef.current!.volume = 1;
      }).catch(() => {});
    }
  };

  const handleAction = async (eventId: string, action: string, assetId: string) => {
    try {
      const apiUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))
      await fetch(`${apiUrl}/control/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId, action, asset_id: assetId || "UNKNOWN" })
      });
      fetchEvents();
    } catch (e) {
      alert("Failed to submit command");
    }
  }

  const acknowledge = async (eventId: string) => {
    try {
      const apiUrl = (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'))
      await fetch(`${apiUrl}/control/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId })
      });
      if (audioRef.current) audioRef.current.pause();
      fetchEvents();
    } catch (e) {
      alert("Failed to acknowledge");
    }
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 font-mono text-slate-800 pb-20 p-6">
      
      {/* HEADER */}
      <div className="flex justify-between items-end border-b border-slate-300 pb-4">
        <div>
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-slate-800 uppercase">Live Command Center</h1>
          <p className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-2">Operator Control & Peak Event Management</p>
        </div>
        {!audioUnlocked ? (
          <button onClick={unlockAudio} className="bg-amber-100 text-amber-800 px-4 py-2 rounded font-bold text-sm hover:bg-amber-200 uppercase tracking-widest animate-pulse border-2 border-amber-300">
            Enable Audible Alarms
          </button>
        ) : (
          <div className="text-emerald-700 font-bold text-sm tracking-widest border-2 border-emerald-200 bg-emerald-50 px-4 py-2 rounded">
            AUDIO ENABLED
          </div>
        )}
      </div>

      <div className="bg-white border-2 border-slate-200 rounded-xl p-6 shadow-sm min-h-[400px]">
         <div className="text-sm font-bold uppercase tracking-widest text-slate-800 mb-6 border-b border-slate-100 pb-2">Active Events & Recommendations</div>
         
         {events.length === 0 ? (
           <div className="flex flex-col items-center justify-center h-64 text-slate-400 font-bold tracking-widest">
              NO ACTIVE PEAK EVENTS
           </div>
         ) : (
           <div className="space-y-6">
             {events.map((evt) => (
               <div key={evt.event_id} className={`border-2 rounded-xl p-6 flex flex-col md:flex-row gap-6 items-center ${evt.severity === 'CRITICAL' ? 'border-red-300 bg-red-50' : 'border-amber-300 bg-amber-50'}`}>
                 <div className="flex-1">
                   <div className="flex items-center gap-3 mb-2">
                     <span className={`text-xs font-bold uppercase tracking-widest px-2 py-1 rounded text-white ${evt.severity === 'CRITICAL' ? 'bg-red-600' : 'bg-amber-600'}`}>
                       {evt.type.replace('_', ' ')}
                     </span>
                     <span className="text-sm font-bold text-slate-500">{new Date(evt.created_at).toLocaleTimeString()}</span>
                     <span className="text-xs font-bold uppercase tracking-widest text-slate-500">ID: {evt.event_id}</span>
                   </div>
                   <div className="text-lg font-bold text-slate-800 mb-4">{evt.message}</div>
                   
                   {evt.proposed_action ? (
                     <div className="bg-white border border-slate-200 p-4 rounded-lg">
                       <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-1">AI Recommendation</div>
                       <div className="font-semibold text-slate-800">{evt.proposed_action}</div>
                       <div className="text-sm font-bold text-teal-700 mt-2">Predicted Impact: {evt.impact_kw.toFixed(1)} kW reduction</div>
                     </div>
                   ) : (
                     <div className="bg-white border border-slate-200 p-4 rounded-lg text-slate-500 italic text-sm font-bold">
                       No safe optimization actions available. Production constraints prohibit load shedding.
                     </div>
                   )}
                 </div>
                 
                 <div className="flex flex-col gap-3 min-w-[200px]">
                   <div className="text-xs font-bold uppercase tracking-widest text-slate-500 text-center mb-1">Operator Action</div>
                   
                   {evt.status === 'AWAITING_APPROVAL' ? (
                     <>
                       {evt.proposed_action && (
                         <button onClick={() => handleAction(evt.event_id, 'APPROVE', evt.asset_id)} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-lg uppercase tracking-widest shadow-md">
                           APPROVE
                         </button>
                       )}
                       <button onClick={() => handleAction(evt.event_id, 'REJECT', evt.asset_id)} className="w-full bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold py-3 rounded-lg uppercase tracking-widest">
                         REJECT
                       </button>
                       {!evt.acknowledged && (
                         <button onClick={() => acknowledge(evt.event_id)} className="w-full bg-transparent text-slate-500 hover:text-slate-700 font-bold py-2 rounded-lg text-sm uppercase tracking-widest underline">
                           ACKNOWLEDGE ALARM
                         </button>
                       )}
                     </>
                   ) : (
                     <div className="text-center p-4 bg-white rounded-lg border-2 border-slate-200">
                       <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Command Status</div>
                       <div className={`font-bold uppercase tracking-widest ${evt.status === 'SENT' ? 'text-teal-600' : evt.status === 'REJECTED' ? 'text-slate-600' : 'text-red-600'}`}>
                         {evt.status}
                       </div>
                       {evt.status === 'SENT' && (
                         <div className="text-xs text-slate-500 mt-2 mt-2">Awaiting hardware feedback...</div>
                       )}
                     </div>
                   )}
                 </div>
               </div>
             ))}
           </div>
         )}
      </div>
    </div>
  )
}
