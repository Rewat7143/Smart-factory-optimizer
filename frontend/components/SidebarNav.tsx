"use client"
import React from 'react'
import Link from 'next/link'
import { useGlobalState } from './GlobalState'
import { usePathname } from 'next/navigation'

export function SidebarNav() {
  const { mode } = useGlobalState()
  const pathname = usePathname()

  const execLinks = [
    { name: 'Boardroom', href: '/' },
    { name: 'Verified Ledger', href: '/verified-ledger' },
    { name: 'Scale Impact', href: '/scale-simulator' }
  ]

  const assetLinks = [
    { name: 'Asset Registry', href: '/assets' },
    { name: 'QR Generator & Print', href: '/assets/qr-codes' }
  ]

  const opsLinks = [
    { name: 'AI Demand Forecast', href: '/demand-forecast' },
    { name: 'Digital Twin (Eng)', href: '/live-factory' },
    { name: 'Energy Loss Map', href: '/energy-economics' },
    { name: 'Intelligence (Eng)', href: '/forecast' },
    { name: 'Optimization (Eng)', href: '/optimization-lab' },
    { name: 'Predictive Maint.', href: '/predictive-maintenance' },
    { name: 'Industrial Copilot', href: '/industrial-copilot' }
  ]

  const renderLink = (item: any) => {
     const isActive = pathname === item.href;
     return (
       <Link 
          key={item.name} 
          href={item.href} 
          className={`block px-4 py-3 rounded text-base font-bold tracking-wide uppercase transition-colors ${
             isActive 
               ? 'bg-teal-700 text-white shadow-sm' 
               : 'text-slate-800 hover:bg-slate-200'
          }`}
       >
         {item.name}
       </Link>
     )
  }

  return (
    <aside className="w-72 flex-shrink-0 bg-slate-50 border-r border-slate-200 hidden md:flex flex-col shadow-inner">
      <div className="p-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight uppercase">Factory Energy<br/><span className="text-teal-700">Autopilot</span></h1>
        <div className="mt-2 text-sm font-bold text-slate-800 uppercase tracking-widest">{mode === 'LIVE' ? 'Hardware Telemetry' : 'Closed-Loop Intelligence'}</div>
      </div>
      <nav className="flex-1 py-6 overflow-y-auto">
        <div className="px-3 space-y-2 mb-8">
           <div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4 px-3 border-b-2 border-slate-200 pb-2">Executive View</div>
           {execLinks.map(renderLink)}
        </div>

        <div className="px-3 space-y-2 mb-8">
           <div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4 px-3 border-b-2 border-slate-200 pb-2">Asset Management</div>
           {assetLinks.map(renderLink)}
        </div>
        
        <div className="px-3 space-y-2 mb-8">
           <div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4 px-3 border-b-2 border-slate-200 pb-2">Operations View</div>
           {opsLinks.map(renderLink)}
        </div>
      </nav>
      
      <div className="p-4 border-t border-slate-200">
         <div className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-2 px-2">Engineering / Config</div>
         <Link href="/history-explorer" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 ${pathname === "/history-explorer" ? "text-slate-800" : "text-slate-500"}`}>Historical Data Explorer</Link>
         <Link href="/telemetry" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 ${pathname === "/telemetry" ? "text-slate-800" : "text-slate-500"}`}>Hardware Telemetry</Link>
         <Link href="/hardware" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 ${pathname === '/hardware' ? 'text-slate-800' : 'text-slate-500'}`}>System Hardware</Link>
         <Link href="/industry-test" className={`block px-2 py-2 rounded text-sm font-bold hover:text-slate-800 ${pathname === '/industry-test' ? 'text-slate-800' : 'text-slate-500'}`}>Industry Connection</Link>
      </div>
    </aside>
  )
}
