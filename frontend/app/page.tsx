"use client"
import CommandCenter from "@/components/CommandCenter"
import LiveTelemetryDashboard from "@/components/LiveTelemetryDashboard"
import { useGlobalState } from "@/components/GlobalState"

export default function Home() {
  const { mode } = useGlobalState();
  if (mode === 'LIVE') {
     return <LiveTelemetryDashboard />
  }
  return <CommandCenter />
}
