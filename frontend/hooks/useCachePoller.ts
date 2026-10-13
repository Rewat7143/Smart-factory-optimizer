import React, { useState, useEffect } from 'react'
import { getApiBaseUrl } from '@/lib/config'

// Global cache survives Next.js client-side navigation!
const globalCache = new Map<string, any>()
const API_URL = getApiBaseUrl()

export function useCachePoller(endpoint: string, intervalMs: number = 2000) {
  const [data, setData] = useState<any>(globalCache.get(endpoint) || null)

  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        const currentMode = typeof window !== 'undefined' ? localStorage.getItem('FEA_MODE') || 'LIVE' : 'LIVE';
        const base = typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000';
        const url = new URL(`${API_URL}${endpoint}`, base);
        url.searchParams.set('mode', currentMode);
        
        const res = await fetch(url.toString())
        if (res.ok) {
           const json = await res.json()
           globalCache.set(endpoint, json)
           if (isMounted) setData(json)
        }
      } catch (e) {
        // silently fail or retry
      }
    }

    // Always fetch immediately if we don't have it, or just to keep fresh
    fetchData()
    const int = setInterval(fetchData, intervalMs)
    
    return () => { isMounted = false; clearInterval(int) }
  }, [endpoint, intervalMs])

  return data
}
