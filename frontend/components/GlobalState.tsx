"use client"
import React, { createContext, useContext, useState, useEffect } from 'react';

type Mode = 'SIMULATION' | 'LIVE';

interface GlobalStateContextType {
  mode: Mode;
  setMode: (mode: Mode) => void;
}

const GlobalStateContext = createContext<GlobalStateContextType>({ mode: 'SIMULATION', setMode: () => {} });

export function GlobalStateProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<Mode>('LIVE');

  useEffect(() => {
    const savedMode = localStorage.getItem('FEA_MODE') as Mode;
    if (savedMode) {
      setMode(savedMode);
    } else {
      setMode('LIVE');
      try {
        localStorage.setItem('FEA_MODE', 'LIVE');
      } catch (e) {
        // ignore storage error
      }
    }
    
    // Intercept fetch to route all API calls through port 3000 proxy and pass global mode
    if (typeof window !== 'undefined' && !(window as any).__fea_fetch_patched) {
      (window as any).__fea_fetch_patched = true;
      const nativeFetch = window.fetch.bind(window);

      window.fetch = function(input: RequestInfo | URL, init?: RequestInit) {
        try {
          if (typeof input === 'string') {
            let resUrl = input;
            // Strip any hardcoded :8000/api so requests route through Next.js proxy on port 3000
            if (resUrl.includes(':8000/api')) {
              resUrl = resUrl.replace(/^https?:\/\/[^/]+:8000\/api/, '/api');
            }
            if (resUrl.startsWith('/api') || resUrl.includes('/api/')) {
              try {
                const currentMode = localStorage.getItem('FEA_MODE') || 'LIVE';
                const parsed = new URL(resUrl, window.location.origin);
                if (!parsed.searchParams.has('mode')) {
                  parsed.searchParams.set('mode', currentMode);
                }
                resUrl = parsed.pathname + parsed.search;
              } catch (e) {
                // fallback
              }
            }
            return nativeFetch(resUrl, init);
          }
        } catch (e) {
          // fallback
        }
        return nativeFetch(input, init);
      };
    }
  }, []);

  const handleSetMode = (newMode: Mode) => {
    setMode(newMode);
    try {
      localStorage.setItem('FEA_MODE', newMode);
    } catch (e) {
      // ignore
    }
  };

  return (
    <GlobalStateContext.Provider value={{ mode, setMode: handleSetMode }}>
      {children}
    </GlobalStateContext.Provider>
  );
}

export function useGlobalState() {
  return useContext(GlobalStateContext);
}
