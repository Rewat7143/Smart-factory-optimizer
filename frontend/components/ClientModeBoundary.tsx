"use client"
import React from 'react'
import { useGlobalState } from './GlobalState'
import { LiveMeterPlaceholder } from './LiveMeterPlaceholder'

export function ClientModeBoundary({ children, title }: { children: React.ReactNode, title?: string }) {
  const { mode } = useGlobalState()

  if (mode === 'LIVE') {
    return <LiveMeterPlaceholder title={title} />
  }

  return <>{children}</>
}
