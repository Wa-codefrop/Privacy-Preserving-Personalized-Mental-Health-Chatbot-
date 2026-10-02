import { useEffect, useState } from 'react'
import {
  Activity,
  ArrowUpRight,
  Brain,
  Database,
  HeartPulse,
  LockKeyhole,
  MessageCircle,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import './Dashboard.css'

type SystemStatus = {
  api: 'online'
  database: 'connected' | 'disconnected'
  dataset: { present: boolean; files: number }
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api').replace(/\/$/, '')

const navigation: { section: string; items: { label: string; icon: typeof Activity; active?: boolean }[] }[] = [
  {
    section: 'WORKSPACE',
    items: [
      { label: 'Dashboard', icon: Activity, active: true },
      { label: 'AI assistant', icon: MessageCircle },
      { label: 'Wellbeing', icon: HeartPulse },
    ],
  },
  {
    section: 'INTELLIGENCE',
    items: [
      { label: 'Insights', icon: Sparkles },
      { label: 'Safety monitor', icon: ShieldCheck },
      { label: 'Model evaluation', icon: Brain },
    ],
  },
  {
    section: 'PRIVACY & RESEARCH',
    items: [
      { label: 'Privacy center', icon: LockKeyhole },
      { label: 'Dataset', icon: Database },
      { label: 'Federated ML', icon: Network },
    ],
  },
]

function Dashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [apiUnavailable, setApiUnavailable] = useState(false)

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${apiBaseUrl}/system/status`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('System status request failed')
        return response.json() as Promise<SystemStatus>
      })
      .then((status) => {
        setSystemStatus(status)
        setApiUnavailable(false)
      })
      .catch((error: unknown) => {
        if (error instanceof Error && error.name === 'AbortError') return
        setApiUnavailable(true)
      })

    return () => controller.abort()
  }, [])

  const apiLabel = apiUnavailable ? 'API offline' : systemStatus ? 'API connected' : 'Checking API'

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#dashboard" aria-label="Wellbeing Intelligence dashboard">
          <span className="brand-mark"><Activity size={19} strokeWidth={2.4} /></span>
          <span className="brand-copy"><strong>wellbeing</strong><small>INTELLIGENCE PLATFORM</small></span>
        </a>
        <div className="workspace-picker">
          <span className="workspace-monogram">R</span>
          <span><strong>Research workspace</strong><small>Personal environment</small></span>
          <span className="workspace-caret" aria-hidden="true">v</span>
        </div>
        <nav className="primary-nav" aria-label="Main navigation">
          {navigation.map((group) => (
            <div className="nav-group" key={group.section}>
              <p className="nav-heading">{group.section}</p>
              {group.items.map(({ label, icon: Icon, active }) => (
                <button
                  className={`nav-item${active ? ' is-active' : ''}`}
                  type="button"
                  key={label}
                  disabled={!active}
                  aria-current={active ? 'page' : undefined}
                  title={active ? label : `${label} will be available in a later phase`}
                >
                  <Icon size={17} strokeWidth={1.8} />
                  <span>{label}</span>
                  {active && <span className="nav-current-dot" />}
                </button>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-foot"><span className="build-indicator" /><span>Foundation phase</span><span className="build-version">v0.1</span></div>
      </aside>

      <main className="main-panel" id="dashboard">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-divider">/</span><strong>Dashboard</strong></div>
          <div className="topbar-actions">
            <span className={`api-pill ${apiUnavailable ? 'is-offline' : ''}`}><span className="status-dot" />{apiLabel}</span>
            <button className="icon-button" type="button" aria-label="Search" title="Search"><Search size={18} /></button>
            <div className="user-avatar" aria-label="Research workspace">R</div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="page-intro">
            <div>
              <p className="eyebrow">PRIVACY-PRESERVING WELLBEING</p>
              <h1>Good to have you here.</h1>
              <p className="intro-copy">A clear view of your wellbeing workspace and research pipeline.</p>
            </div>
            <div className="date-stamp"><span className="date-stamp-dot" />SYSTEM OVERVIEW</div>
          </section>

          <section className="welcome-band" aria-label="Workspace readiness">
            <div className="welcome-mark"><Activity size={22} /></div>
            <div className="welcome-copy">
              <span className="welcome-kicker">YOUR RESEARCH WORKSPACE</span>
              <h2>{systemStatus?.dataset.present ? 'Your source files are here. Review is the next step.' : 'Built for careful, data-led wellbeing research.'}</h2>
              <p>File presence does not mean the data has been validated. Personal wellbeing and model metrics will appear only after real records and experiments exist.</p>
            </div>
            <div className="welcome-index"><span>01</span><span className="index-rule" /><span>FOUNDATION</span></div>
          </section>

          <section className="metrics-grid" aria-label="Workspace status">
            <article className="metric-card metric-highlight">
              <div className="metric-top"><span className="metric-icon"><Database size={17} /></span><span className="metric-label">RESEARCH DATASET</span><span className="metric-corner"><ArrowUpRight size={15} /></span></div>
              <p className="metric-value">{systemStatus ? (systemStatus.dataset.present ? `${systemStatus.dataset.files} files` : 'Not found') : 'Checking'}</p>
              <p className="metric-note">{systemStatus?.dataset.present ? 'Source files detected under datasets/' : 'No source files found under datasets/'}</p>
            </article>
            <article className="metric-card">
              <div className="metric-top"><span className="metric-icon mood-icon"><HeartPulse size={17} /></span><span className="metric-label">WELLBEING CHECK-INS</span></div>
              <p className="metric-value metric-muted">Not recorded</p><p className="metric-note">No check-in data is available yet</p>
            </article>
            <article className="metric-card">
              <div className="metric-top"><span className="metric-icon model-icon"><Brain size={17} /></span><span className="metric-label">MODEL EVALUATIONS</span></div>
              <p className="metric-value metric-muted">Not run</p><p className="metric-note">Metrics will follow a real training run</p>
            </article>
            <article className="metric-card">
              <div className="metric-top"><span className="metric-icon privacy-icon"><LockKeyhole size={17} /></span><span className="metric-label">DATABASE</span></div>
              <p className="metric-value">{systemStatus?.database === 'connected' ? 'Connected' : systemStatus?.database === 'disconnected' ? 'Offline' : 'Checking'}</p>
              <p className="metric-note">PostgreSQL service status</p>
            </article>
          </section>

          <section className="content-grid">
            <article className="panel trend-panel">
              <div className="panel-heading"><div><p className="panel-overline">WELLBEING</p><h2>Personal trends</h2></div><span className="period-label">RECENT ACTIVITY</span></div>
              <div className="chart-empty">
                <div className="chart-grid-lines"><span /><span /><span /><span /></div>
                <div className="chart-empty-content"><span className="empty-chart-icon"><HeartPulse size={19} /></span><strong>Your trend will take shape here</strong><p>Check-in history will be shown once real entries are recorded.</p></div>
                <div className="chart-axis"><span>EARLIER</span><span>NOW</span></div>
              </div>
            </article>

            <article className="panel pipeline-panel">
              <div className="panel-heading">
                <div><p className="panel-overline">RESEARCH PIPELINE</p><h2>Data readiness</h2></div>
                <span className={`readiness-tag ${systemStatus?.dataset.present ? 'is-ready' : ''}`}><span className="status-dot" />{systemStatus?.dataset.present ? 'FILES FOUND' : 'AWAITING DATA'}</span>
              </div>
              <div className="pipeline-steps">
                <div className={`pipeline-step ${systemStatus?.dataset.present ? 'is-current' : ''}`}>
                  <span className="step-marker">01</span>
                  <div><strong>Source dataset</strong><span>{systemStatus ? (systemStatus.dataset.present ? 'Files found; schema and license review pending' : 'Place your dataset under datasets/') : 'Checking local dataset folder'}</span></div>
                </div>
                <div className="pipeline-connector" />
                <div className="pipeline-step"><span className="step-marker">02</span><div><strong>Validation & exploration</strong><span>Begins in Phase 3</span></div></div>
                <div className="pipeline-connector" />
                <div className="pipeline-step"><span className="step-marker">03</span><div><strong>Model experiments</strong><span>Uses measured pipeline outputs</span></div></div>
              </div>
              <div className="dataset-location"><span className="location-label">LOCAL DATASET ROOT</span><code>datasets/</code><span className="location-note">Dataset files are excluded from Git commits.</span></div>
            </article>
          </section>

          <section className="bottom-grid">
            <article className="panel activity-panel">
              <div className="panel-heading"><div><p className="panel-overline">WORKSPACE</p><h2>Recent activity</h2></div><span className="activity-count">0 EVENTS</span></div>
              <div className="activity-empty"><span className="activity-empty-mark"><Activity size={17} /></span><div><strong>No activity to show</strong><p>Check-ins, conversations, and experiment runs will appear here when available.</p></div></div>
            </article>
            <article className="privacy-note">
              <div className="privacy-note-icon"><ShieldCheck size={18} /></div>
              <div><p className="panel-overline">PRIVACY BY DESIGN</p><h2>Your dataset stays local.</h2><p>Dataset files are ignored by Git and mounted read-only for the API. We will review its schema and sensitivity before any processing.</p></div>
              <span className="privacy-note-rule" />
            </article>
          </section>

          {apiUnavailable && <p className="connection-notice" role="status">The API is not reachable. Start the services with <code>docker compose up --build</code> to load live system status.</p>}
          <footer className="page-footer"><span>WELLBEING INTELLIGENCE PLATFORM</span><span>Supportive research only - Not a diagnostic system</span></footer>
        </div>
      </main>
    </div>
  )
}

export default Dashboard