// Fill the metrics strip from assets/metrics.json (copied from data/samples/metrics.json by scripts/build_site.py).
// Set DASHBOARD_URL if the live dashboard is ever deployed somewhere reachable.
const DASHBOARD_URL = "";

if (DASHBOARD_URL) {
  const a = document.getElementById("dashLink");
  a.href = DASHBOARD_URL;
  a.textContent = "Open the live dashboard";
}

const metrics = window.CEREBRO_METRICS ? Promise.resolve(window.CEREBRO_METRICS) : fetch("assets/metrics.json").then((r) => r.json());
metrics
  .then((m) => {
    const h = m.headline;
    const b = h.real_fault_cases_breakdown;
    const set = (k, v) => document.querySelectorAll(`[data-m="${k}"]`).forEach((el) => (el.textContent = v));
    set("subsystems", h.subsystems_monitored);
    set("faults", h.real_fault_cases_flagged);
    set("faults_detail", `${b.ashrae_fault_runs_detected_and_diagnosed} chiller fault runs, ${b.nasa_cells_flagged_before_eol} battery cells before end-of-life, ${b.umn_upv_low_readings_flagged} low-UPV concrete readings, ${b.cu_bems_ac1_collapse_flagged} AC-unit output collapse`);
    set("rerank", `${h.rerank_ms_mean.toFixed(2)} ms`);
    set("diag", `${(100 * h.hvac_diagnosis_accuracy).toFixed(1)}%`);
    set("fa", `${(100 * h.hvac_false_alarm_rate).toFixed(1)}%`);
    set("rul", h.battery_rul_mae_cycles.toFixed(1));
  })
  .catch(() => {});
