import { useGlobalState } from './GlobalState'

// ... later in CommandCenter ...
  const { mode } = useGlobalState()

  if (mode === 'LIVE') {
     return <LiveMeterView />
  }

// ... the rest of the existing CommandCenter return logic ...
