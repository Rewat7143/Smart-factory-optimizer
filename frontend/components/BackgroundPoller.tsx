"use client"
import { useEffect } from 'react'
import { useCachePoller } from '@/hooks/useCachePoller'

export function BackgroundPoller() {
  // Mount this once in layout.tsx. It silently polls all core endpoints 24/7.
  // Then when the user clicks a tab, the page's useCachePoller hook instantly loads from cache!
  useCachePoller('/factory/state', 2000);
  useCachePoller('/maintenance/status', 5000);
  useCachePoller('/copilot/insights', 5000);
  useCachePoller('/energy/history', 10000);
  useCachePoller('/optimize', 10000);
  useCachePoller('/forecast/registry', 10000);
  
  return null;
}
