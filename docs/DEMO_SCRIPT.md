# Demo Script: Factory Energy Autopilot

**Total Time:** 4m 30s
**Presenter:** Lead Architect

---

## 1. INTRO & PROBLEM (0:00 - 0:40)
**Action:** Open the `Overview` page (Command Center).
**Script:**
> "Welcome to Factory Energy Autopilot. 
> The manufacturing industry faces a critical problem: electricity costs and peak demand penalties are rising, but factories cannot simply switch off machines to save energy—doing so destroys production schedules.
> We built a platform that optimizes the energy *around* production. Production is our hard constraint; energy is our optimization variable."

## 2. LIVE FACTORY (0:40 - 1:20)
**Action:** Click `Run Presentation Demo` in the top right.
**Script:**
> "Right now, the factory is operating normally. We are hitting our 100% production target.
> The AI Forecaster in the center is constantly analyzing the live telemetry against our 30-day historical data.
> Notice the current demand is stable."

## 3. PEAK EVENT & FORECAST (1:20 - 2:05)
**Action:** Wait for the deterministic demo to trigger Peak Risk. The UI pulses RED.
**Script:**
> "Suddenly, a flexible load—the heavy compressor—starts up at the same time as our cooling pump. 
> Instantly, the XGBoost Forecasting model detects that in 15 minutes, we will exceed our Safe Target of 100 kW. We are entering High Peak Risk.
> Instead of blind alarms, the AI attributes the peak to the exact live contributors on the left: Production, Compressor, and Pump."

## 4. OPTIMIZATION & PROTECTION (2:05 - 2:50)
**Action:** Point to the AI Recommendation card on the right.
**Script:**
> "Here is where the intelligence happens. The OR-Tools constraint solver evaluates our options. 
> It looks at 'Option A: Stop the Production Motor.' But you can see it is **REJECTED** because it violates our hard 100% production constraint.
> Instead, it selects a safe counterfactual: Delay the compressor startup by 8 minutes. This achieves a 9.2 kW reduction without touching production."

## 5. WHAT-IF SIMULATION (2:50 - 3:20)
**Action:** Click `View What-If Analysis` to open the What-If Engine.
**Script:**
> "Before applying, the operator can see exactly why this was chosen. 
> Here in the Counterfactual Simulator, we compare the Baseline, the Optimized Schedule, and the Rejected option side-by-side. 
> You can clearly see how Peak Demand drops, Risk goes to LOW, and Production stays at 100%."

## 6. ANOMALY & ENERGY DNA (3:20 - 3:50)
**Action:** Navigate to `Opportunities` or wait for the Anomaly trigger.
**Script:**
> "Beyond peak management, the platform uses an Isolation Forest model trained on the machines' historical behaviour to detect hidden waste.
> If a compressor starts drawing 24% more power than its expected baseline, it generates an Opportunity ticket quantifying the exact ₹ cost impact. 
> We can drill down into the 'Asset DNA' to see its exact engineering profile calculated from historical telemetry."

## 7. SCALE & CLOSING (3:50 - 4:10)
**Action:** Navigate to `Business Impact`.
**Script:**
> "Finally, we translate engineering metrics into business value. 
> We explicitly separate Measured daily consumption from Simulated optimization potential and Projected annual ROI. 
> This is a production-grade intelligence layer ready to connect to real hardware meters. Thank you."
