"use client"
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useGlobalState } from './GlobalState';
import { getApiBaseUrl } from '@/lib/config';

export default function GlobalHeader() {
  const { mode, setMode } = useGlobalState();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  // Close mobile drawer on route navigation
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const execLinks = [
    { name: 'Boardroom', href: '/' },
    { name: 'Verified Ledger', href: '/verified-ledger' },
    { name: 'Scale Impact', href: '/scale-simulator' }
  ];

  const assetLinks = [
    { name: 'Asset Registry', href: '/assets' },
    { name: 'QR Generator & Print', href: '/assets/qr-codes' }
  ];

  const opsLinks = [
    { name: 'AI Demand Forecast', href: '/demand-forecast' },
    { name: 'Digital Twin (Eng)', href: '/live-factory' },
    { name: 'Energy Loss Map', href: '/energy-economics' },
    { name: 'Intelligence (Eng)', href: '/forecast' },
    { name: 'Optimization (Eng)', href: '/optimization-lab' },
    { name: 'Predictive Maint.', href: '/predictive-maintenance' },
    { name: 'Industrial Copilot', href: '/industrial-copilot' }
  ];

  const engLinks = [
    { name: 'Historical Data Explorer', href: '/history-explorer' },
    { name: 'Hardware Telemetry', href: '/telemetry' },
    { name: 'System Hardware', href: '/hardware' },
    { name: 'Industry Connection', href: '/industry-test' }
  ];

  const renderMobileNavLink = (item: { name: string; href: string }) => {
    const isActive = pathname === item.href;
    return (
      <Link
        key={item.href}
        href={item.href}
        onClick={() => setMobileMenuOpen(false)}
        className={`block px-3 py-2 rounded-lg text-sm font-bold uppercase tracking-wider transition-colors ${
          isActive
            ? 'bg-teal-700 text-white shadow-xs'
            : 'text-slate-800 hover:bg-slate-100'
        }`}
      >
        {item.name}
      </Link>
    );
  };

  return (
    <>
      <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-3 sm:px-6 shrink-0 shadow-sm z-30 sticky top-0 w-full">
        {/* Left Side: Hamburger (Mobile) + Title / Mode */}
        <div className="flex items-center space-x-2 sm:space-x-4 min-w-0">
          {/* Mobile Hamburger Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-800 hover:bg-slate-100 focus:outline-none flex items-center justify-center"
            aria-label="Toggle navigation drawer"
          >
            {mobileMenuOpen ? (
              <span className="text-xl font-black leading-none">✕</span>
            ) : (
              <span className="text-xl leading-none">☰</span>
            )}
          </button>

          {/* Mobile Branding (Visible only on mobile) */}
          <Link href="/assets" className="md:hidden flex flex-col min-w-0 mr-1">
            <span className="text-xs font-black uppercase tracking-tight text-slate-900 truncate">
              Autopilot
            </span>
            <span className="text-[9px] font-bold text-teal-700 uppercase -mt-0.5">
              Passport
            </span>
          </Link>

          {/* Mode Indicator: Locked to LIVE METER STREAM on Asset / QR pages */}
          {pathname?.startsWith('/assets') ? (
            <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-950 shadow-xs font-mono">
              <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-emerald-600 animate-pulse shrink-0" />
              <div className="flex flex-col min-w-0">
                <span className="text-[10px] sm:text-xs font-black uppercase tracking-wider leading-tight text-emerald-950 truncate">
                  LIVE METER STREAM
                </span>
                <span className="text-[8px] sm:text-[9px] font-bold text-emerald-700 tracking-wider uppercase -mt-0.5 truncate hidden xs:inline sm:inline">
                  Modbus RTU Hardware
                </span>
              </div>
            </div>
          ) : (
            /* Mode Switch on other pages */
            <div className="flex flex-col border border-slate-300 rounded overflow-hidden bg-slate-100 shadow-inner">
              <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-slate-200 px-1.5 sm:px-2 py-0.5 border-b border-slate-300 truncate">
                <span className="hidden sm:inline">Operating </span>Mode
              </div>
              <div className="flex">
                <button
                  onClick={() => setMode('SIMULATION')}
                  className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-widest transition-all ${
                    mode === 'SIMULATION'
                      ? 'bg-white text-slate-800 shadow-sm border-r border-slate-200'
                      : 'text-slate-500 hover:text-slate-800 border-r border-slate-200 opacity-70'
                  }`}
                >
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full border border-slate-400 flex items-center justify-center">
                    <div
                      className={`w-1 h-1 rounded-full ${
                        mode === 'SIMULATION' ? 'bg-teal-600' : 'bg-transparent'
                      }`}
                    />
                  </div>
                  <span>SIM</span>
                  <span className="hidden md:inline">ULATION</span>
                </button>
                <button
                  onClick={() => setMode('LIVE')}
                  className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-widest transition-all ${
                    mode === 'LIVE'
                      ? 'bg-white text-slate-800 shadow-sm'
                      : 'text-slate-500 hover:text-slate-800 opacity-70'
                  }`}
                >
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full border border-slate-400 flex items-center justify-center">
                    <div
                      className={`w-1 h-1 rounded-full ${
                        mode === 'LIVE' ? 'bg-red-600 animate-pulse' : 'bg-transparent'
                      }`}
                    />
                  </div>
                  <span>LIVE</span>
                  <span className="hidden md:inline"> FACTORY</span>
                </button>
              </div>
            </div>
          )}

          {/* System Telemetry Status (Responsive) */}
          <div className="hidden sm:block min-w-0">
            <SystemStatus mode={mode} />
          </div>
        </div>

        {/* Right Side: Operator Avatar & Label */}
        <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
          <span className="hidden lg:inline text-xs font-bold text-slate-700 uppercase tracking-wider">
            Plant Operator
          </span>
          <div
            className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center text-xs font-black shadow-xs font-mono"
            title="Logged in as Plant Operator"
          >
            OP
          </div>
        </div>
      </header>

      {/* MOBILE NAVIGATION DRAWER (Slide-over overlay on mobile devices) */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          {/* Backdrop Blur */}
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />

          {/* Drawer Content */}
          <div className="relative w-4/5 max-w-xs bg-white h-full shadow-2xl flex flex-col z-50 overflow-y-auto">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <div className="text-base font-black text-slate-900 uppercase">
                  Factory Energy
                </div>
                <div className="text-xs font-black text-teal-700 uppercase tracking-widest">
                  Autopilot
                </div>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="w-8 h-8 rounded-lg bg-white border border-slate-300 flex items-center justify-center text-slate-800 font-bold"
                aria-label="Close navigation"
              >
                ✕
              </button>
            </div>

            <nav className="flex-1 p-4 space-y-6">
              <div>
                <div className="text-[11px] font-black uppercase tracking-widest text-teal-800 border-b border-slate-200 pb-1 mb-2">
                  Asset Management
                </div>
                <div className="space-y-1">{assetLinks.map(renderMobileNavLink)}</div>
              </div>

              <div>
                <div className="text-[11px] font-black uppercase tracking-widest text-slate-500 border-b border-slate-200 pb-1 mb-2">
                  Executive View
                </div>
                <div className="space-y-1">{execLinks.map(renderMobileNavLink)}</div>
              </div>

              <div>
                <div className="text-[11px] font-black uppercase tracking-widest text-slate-500 border-b border-slate-200 pb-1 mb-2">
                  Operations View
                </div>
                <div className="space-y-1">{opsLinks.map(renderMobileNavLink)}</div>
              </div>

              <div>
                <div className="text-[11px] font-black uppercase tracking-widest text-slate-500 border-b border-slate-200 pb-1 mb-2">
                  Engineering / Hardware
                </div>
                <div className="space-y-1">{engLinks.map(renderMobileNavLink)}</div>
              </div>
            </nav>

            <div className="p-4 border-t border-slate-200 bg-slate-50 text-[10px] text-slate-500 font-mono">
              <div>Mobile Field Interface • v2.0</div>
              <div>Point of Common Coupling Live Bus</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function SystemStatus({ mode }: { mode: string }) {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    if (mode === 'SIMULATION') return;

    const fetchStatus = async () => {
      try {
        const apiBase = getApiBaseUrl();
        const res = await fetch(`${apiBase}/telemetry/source-status`);
        if (res.ok) {
          const data = await res.json();
          setStatus(data);
        }
      } catch (e) {
        console.error('Failed to fetch source status', e);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [mode]);

  if (mode === 'SIMULATION') {
    return (
      <div className="flex flex-col">
        <div className="flex items-center space-x-1.5 text-xs font-bold">
          <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
          <span className="text-slate-800 font-bold tracking-wider uppercase">SIMULATION</span>
        </div>
        <span className="text-[9px] text-slate-400 uppercase tracking-widest hidden md:inline">
          Software Loop
        </span>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center space-x-1.5 text-xs font-bold">
        <div className="w-2 h-2 rounded-full bg-slate-300" />
        <span className="text-slate-400 font-bold uppercase tracking-wider">CONNECTING</span>
      </div>
    );
  }

  const isLive =
    status.active_source === 'RASPBERRY_PI' || status.active_source === 'SIMULATED_RASPI';

  return (
    <div className="flex flex-col">
      <div className="flex items-center space-x-1.5 text-xs font-bold">
        <div
          className={`w-2 h-2 rounded-full ${
            isLive ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
          }`}
        />
        <span className="text-slate-800 font-bold tracking-wider uppercase">
          {isLive ? 'LIVE HARDWARE' : 'FALLBACK'}
        </span>
      </div>
      <span className="text-[9px] text-slate-400 uppercase tracking-widest hidden md:inline">
        Fresh • {status.data_age_seconds ?? 0.3}s
      </span>
    </div>
  );
}
