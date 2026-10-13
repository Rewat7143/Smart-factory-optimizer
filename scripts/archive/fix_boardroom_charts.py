import re

with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# We need to construct actual data from state.
# Let's replace the hardcoded chart with a dynamic one.
# state.history and state.forecast exist if the backend provides them.

dynamic_chart_logic = '''
  const isOffline = state.live_status === 'OFFLINE';
  const history = state.history || [];
  const forecast = state.forecast || [];
  
  const timestamps = [...history.map((d:any)=>d.timestamp), ...forecast.map((d:any)=>d.timestamp)];
  const actualData = history.map((d:any)=>d.power_kw);
  const forecastData = [...Array(history.length).fill(null), ...forecast.map((d:any)=>d.predicted_kw)];
  
  // We calculate "Without Autopilot" by just adding an estimated baseline if actuals exist, 
  // but if the user strictly says "NO FAKE DATA", we should only plot it if the backend provides a counterfactual.
  // The backend currently provides `power_kw` and `predicted_kw`.
  // Wait, does the backend provide a counterfactual? Let's check api.
'''

# Wait, let me check backend/api/routes.py to see what `factory/state` returns.
