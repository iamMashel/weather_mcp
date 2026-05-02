<template>
  <div class="app">
    <header class="header">
      <h1>Weather MCP</h1>
      <p class="subtitle">Powered by National Weather Service</p>
    </header>

    <main class="main">
      <!-- Forecast Section -->
      <section class="section">
        <h2 class="section-title">Forecast</h2>
        <div class="input-row">
          <input v-model="lat" placeholder="Latitude (e.g. 37.7749)" type="number" step="any" />
          <input v-model="lon" placeholder="Longitude (e.g. -122.4194)" type="number" step="any" />
          <button class="btn" :disabled="forecastLoading" @click="fetchForecast">
            {{ forecastLoading ? "Loading..." : "Get Forecast" }}
          </button>
        </div>

        <p v-if="forecastError" class="error">{{ forecastError }}</p>

        <div v-if="forecastPeriods.length" class="periods">
          <div v-for="(p, i) in forecastPeriods" :key="i" class="period-card">
            <div class="period-header">
              <span class="period-name">{{ p.name }}</span>
              <span class="period-temp">{{ formatTemperature(p) }}</span>
            </div>
            <div class="period-meta">
              <span class="badge wind">{{ formatWind(p) }}</span>
              <span v-if="p.shortForecast" class="badge">{{ p.shortForecast }}</span>
            </div>
            <p class="period-detail">{{ p.detailedForecast }}</p>
          </div>
        </div>
      </section>

      <!-- Alerts Section -->
      <section class="section">
        <h2 class="section-title">Active Alerts</h2>
        <div class="input-row">
          <input v-model="state" placeholder="State code (e.g. TX)" maxlength="2" style="text-transform:uppercase" />
          <button class="btn" :disabled="alertsLoading" @click="fetchAlerts">
            {{ alertsLoading ? "Loading..." : "Get Alerts" }}
          </button>
        </div>

        <p v-if="alertsError" class="error">{{ alertsError }}</p>
        <p v-if="noAlerts" class="no-alerts">No active alerts for {{ state.toUpperCase() }}.</p>

        <div v-if="alertItems.length" class="alerts">
          <div v-for="(a, i) in alertItems" :key="i" class="alert-card" :class="severityClass(a.severity)">
            <div class="alert-header">
              <span class="alert-event">{{ a.event }}</span>
              <span class="severity-badge">{{ a.severity }}</span>
            </div>
            <p class="alert-area">{{ a.area }}</p>
            <details class="alert-details">
              <summary>Description</summary>
              <p class="alert-body">{{ a.description }}</p>
            </details>
            <details v-if="a.instructions" class="alert-details">
              <summary>Instructions</summary>
              <p class="alert-body">{{ a.instructions }}</p>
            </details>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue"

const lat = ref("")
const lon = ref("")
const state = ref("")

const forecastLoading = ref(false)
const forecastError = ref("")
const forecastPeriods = ref([])

const alertsLoading = ref(false)
const alertsError = ref("")
const alertItems = ref([])
const noAlerts = ref(false)

const config = useRuntimeConfig()
const API = config.public.apiBase

function formatTemperature(period) {
  if (period.temperature === null || period.temperature === undefined) return "N/A"
  return `${period.temperature}°${period.temperatureUnit}`
}

function formatWind(period) {
  return [period.windSpeed, period.windDirection].filter(Boolean).join(" ") || "Wind unavailable"
}

function severityClass(severity) {
  const s = severity?.toLowerCase()
  if (s === "extreme") return "sev-extreme"
  if (s === "severe") return "sev-severe"
  if (s === "moderate") return "sev-moderate"
  return "sev-minor"
}

const fetchForecast = async () => {
  forecastError.value = ""
  forecastPeriods.value = []

  if (!lat.value || !lon.value) {
    forecastError.value = "Enter a latitude and longitude."
    return
  }

  forecastLoading.value = true
  try {
    const res = await fetch(`${API}/forecast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ latitude: Number(lat.value), longitude: Number(lon.value) }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail ?? "Request failed")
    forecastPeriods.value = data.data ?? []
  } catch (e) {
    forecastError.value = e.message || "Failed to fetch forecast"
  } finally {
    forecastLoading.value = false
  }
}

const fetchAlerts = async () => {
  alertsError.value = ""
  alertItems.value = []
  noAlerts.value = false

  if (!/^[a-zA-Z]{2}$/.test(state.value.trim())) {
    alertsError.value = "Enter a two-letter US state code."
    return
  }

  alertsLoading.value = true
  try {
    const res = await fetch(`${API}/alerts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state: state.value.toUpperCase() }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail ?? "Request failed")
    alertItems.value = data.data ?? []
    noAlerts.value = alertItems.value.length === 0
  } catch (e) {
    alertsError.value = e.message || "Failed to fetch alerts"
  } finally {
    alertsLoading.value = false
  }
}
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; }

.app {
  min-height: 100vh;
  background: #f0f4f8;
  font-family: system-ui, sans-serif;
  color: #1a202c;
}

.header {
  background: #1a365d;
  color: white;
  padding: 2rem 1.5rem;
  text-align: center;
}
.header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
.subtitle { margin: 0.25rem 0 0; opacity: 0.7; font-size: 0.9rem; }

.main {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.section-title {
  margin: 0 0 1.25rem;
  font-size: 1.15rem;
  font-weight: 600;
  color: #2d3748;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.6rem;
}

.input-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
}

input {
  flex: 1;
  min-width: 140px;
  padding: 0.6rem 0.8rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.15s;
}
input:focus { border-color: #3182ce; }

.btn {
  padding: 0.6rem 1.2rem;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.btn:hover:not(:disabled) { background: #2c5282; }
.btn:disabled { opacity: 0.55; cursor: default; }

.error { color: #c53030; font-size: 0.9rem; margin: 0.5rem 0; }
.no-alerts { color: #718096; font-size: 0.9rem; }

/* Forecast periods */
.periods {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.period-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.period-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
}
.period-name { font-weight: 600; font-size: 0.95rem; }
.period-temp { font-size: 1.1rem; font-weight: 700; color: #2b6cb0; white-space: nowrap; }

.period-meta { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.badge { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: #ebf8ff; color: #2b6cb0; }

.period-detail {
  margin: 0;
  font-size: 0.85rem;
  color: #4a5568;
  line-height: 1.5;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* Alerts */
.alerts { display: flex; flex-direction: column; gap: 1rem; }

.alert-card {
  border-left: 4px solid #a0aec0;
  border-radius: 6px;
  padding: 1rem 1rem 0.75rem;
  background: #f7fafc;
}
.sev-extreme { border-left-color: #742a2a; background: #fff5f5; }
.sev-severe  { border-left-color: #c53030; background: #fff5f5; }
.sev-moderate { border-left-color: #dd6b20; background: #fffaf0; }
.sev-minor   { border-left-color: #3182ce; background: #ebf8ff; }

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}
.alert-event { font-weight: 700; font-size: 0.95rem; }
.severity-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #e2e8f0;
  color: #2d3748;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.sev-severe  .severity-badge,
.sev-extreme .severity-badge { background: #fed7d7; color: #9b2c2c; }
.sev-moderate .severity-badge { background: #feebc8; color: #7b341e; }

.alert-area { margin: 0 0 0.6rem; font-size: 0.85rem; color: #718096; }

.alert-details {
  margin-top: 0.4rem;
  font-size: 0.85rem;
}
.alert-details summary {
  cursor: pointer;
  font-weight: 600;
  color: #4a5568;
  padding: 0.3rem 0;
  user-select: none;
}
.alert-body {
  margin: 0.5rem 0 0.25rem;
  color: #4a5568;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}
</style>
