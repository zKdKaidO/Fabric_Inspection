import { useEffect, useState } from 'react'
import { Activity, ClipboardCheck, History, Layers3, Microscope, RefreshCw, ShieldAlert } from 'lucide-react'

type Page = 'dashboard' | 'fabrics' | 'commissioning' | 'inspect' | 'history'
type Fabric = { fabric_id: string; name: string; description: string; profile: string | null; commissioning_status: string; commissioning_samples: number; commissioning_summary?: { validation_passed: boolean; message: string; number_of_samples: number } | null }
type Sample = { path: string; filename: string; preview_url: string }
type Result = { inspection_id: string; fabric_id: string; timestamp: string; status: 'PASS' | 'REVIEW' | 'HOLD'; explanation: string; anomaly_score: number; latency_ms: number; engine: string; defect_count: number; artifacts: { original: string; anomaly_map: string; overlay: string }; review?: { decision: string; notes: string } | null }
const pages: { id: Page; label: string; icon: typeof Activity }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: Activity }, { id: 'fabrics', label: 'Fabric Management', icon: Layers3 },
  { id: 'commissioning', label: 'Commissioning', icon: ClipboardCheck }, { id: 'inspect', label: 'Inspect', icon: Microscope }, { id: 'history', label: 'History', icon: History },
]
async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, init)
  if (!r.ok) { const body = await r.json().catch(() => ({})); throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail ?? r.statusText)) }
  return r.json()
}
const json = (body: unknown): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
const when = (s: string) => new Date(s).toLocaleString()
function Status({ value }: { value: string }) { return <span className={`status status-${value === 'HOLD' ? 'fail' : value.toLowerCase()}`}>{value.replaceAll('_', ' ')}</span> }

export default function App() {
  const [page, setPage] = useState<Page>('dashboard'), [fabrics, setFabrics] = useState<Fabric[]>([]), [history, setHistory] = useState<Result[]>([])
  const [profiles, setProfiles] = useState<string[]>([]), [error, setError] = useState(''), [online, setOnline] = useState(false)
  async function refresh() {
    try { const [f, h, p] = await Promise.all([api<Fabric[]>('/fabrics'), api<Result[]>('/inspections'), api<{ profile: string }[]>('/profiles')]); setFabrics(f); setHistory(h); setProfiles(p.map(x => x.profile)); setOnline(true); setError('') }
    catch (e) { setError((e as Error).message); setOnline(false) }
  }
  useEffect(() => { void refresh() }, [])
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="weave-logo"><span /></div><div><strong>FABRIC/QC</strong><small>Frozen Solution 1</small></div></div>
    <nav aria-label="Main navigation">{pages.map(p => <button key={p.id} onClick={() => setPage(p.id)} className={page === p.id ? 'active' : ''}><p.icon size={19} />{p.label}</button>)}</nav>
    <div className="sidebar-foot"><div className="engine-note">Seven frozen roll profiles</div><div className="connection"><i className={online ? 'online' : ''} />{online ? 'Local system ready' : 'Backend unavailable'}</div></div></aside>
    <main><header className="topbar"><div><span className="eyebrow">RAW-FABRID / TEXTILE INSPECTION</span><h1>{pages.find(p => p.id === page)?.label}</h1></div><button className="refresh" onClick={refresh}><RefreshCw size={16} />Refresh</button></header>
      {error && <div className="error-banner" role="alert"><ShieldAlert />{error}</div>}
      <section className="workspace">
        {page === 'dashboard' && <><div className="intro-row"><div><h2>Inspect with a known fabric profile</h2><p>Register a fabric, validate normal samples, then inspect. Every flagged result requires human review.</p></div><button className="primary" onClick={() => setPage('fabrics')}>Get started</button></div>
          <div className="metric-grid"><Metric label="Fabrics" value={fabrics.length} /><Metric label="Validated profiles" value={fabrics.filter(f => f.commissioning_status === 'READY').length} /><Metric label="Recent inspections" value={history.length} /></div>
          <div className="panel"><h3>Frozen research release</h3><p>One Solution 1 algorithm with seven roll-specific normal reference profiles. No model fitting or parameter controls are available.</p><p>New-fabric model fitting is not supported in this frozen research release.</p><p>A PASS result does not guarantee defect-free material. This system highlights anomalous texture; it does not determine cause or severity.</p></div></>}
        {page === 'fabrics' && <Fabrics fabrics={fabrics} profiles={profiles} refresh={refresh} next={() => setPage('commissioning')} />}
        {page === 'commissioning' && <Commissioning fabrics={fabrics} refresh={refresh} />}
        {page === 'inspect' && <Inspect fabrics={fabrics} refresh={refresh} />}
        {page === 'history' && <HistoryPage rows={history} refresh={refresh} />}
      </section></main></div>
}
function Metric({ label, value }: { label: string; value: number }) { return <div className="metric"><span>{label}</span><strong>{value}</strong></div> }
function FabricSelect({ fabrics, value, onChange }: { fabrics: Fabric[]; value: string; onChange: (s: string) => void }) {
  return <label>Fabric / Roll<select value={value} onChange={e => onChange(e.target.value)}><option value="">Select a registered fabric</option>{fabrics.map(f => <option value={f.fabric_id} key={f.fabric_id}>{f.name} · {f.profile ?? 'Profile selection required'}</option>)}</select></label>
}
function Fabrics({ fabrics, profiles, refresh, next }: { fabrics: Fabric[]; profiles: string[]; refresh: () => Promise<void>; next: () => void }) {
  const [id, setId] = useState(''), [name, setName] = useState(''), [profile, setProfile] = useState(''), [error, setError] = useState(''), [busy, setBusy] = useState(false)
  async function create(e: React.FormEvent) { e.preventDefault(); setBusy(true); setError(''); try { await api('/fabrics', json({ fabric_id: id, name, profile })); await refresh(); setId(''); setName(''); next() } catch (e) { setError((e as Error).message) } finally { setBusy(false) } }
  return <div className="management-grid"><div className="panel"><h2>Register a fabric</h2><form onSubmit={create}>
    <label>Fabric ID<input required minLength={2} pattern="[A-Za-z0-9][A-Za-z0-9_-]+" value={id} onChange={e => setId(e.target.value)} /></label><label>Name<input required minLength={2} value={name} onChange={e => setName(e.target.value)} /></label>
    <label>Existing frozen roll profile<select required value={profile} onChange={e => setProfile(e.target.value)}><option value="">Identify the fabric profile</option>{profiles.map(p => <option key={p}>{p}</option>)}</select></label>
    <p className="muted">Choose the known fabric identity. The system never selects a nearest profile or fits a new model.</p><button className="primary" disabled={busy}>{busy ? 'Saving…' : 'Register fabric'}</button>{error && <p role="alert">{error}</p>}</form></div>
    <div className="panel"><h2>Registered fabrics</h2>{fabrics.map(f => <div className="panel-head" key={f.fabric_id}><div><strong>{f.name}</strong><p>{f.fabric_id} · {f.profile ?? 'Legacy registration'}</p></div><Status value={f.commissioning_status} /></div>)}{!fabrics.length && <p>No fabrics registered yet.</p>}</div></div>
}
function Commissioning({ fabrics, refresh }: { fabrics: Fabric[]; refresh: () => Promise<void> }) {
  const [id, setId] = useState(''), [files, setFiles] = useState<FileList | null>(null), [message, setMessage] = useState(''), [busy, setBusy] = useState(false)
  const f = fabrics.find(x => x.fabric_id === id)
  async function action(fn: () => Promise<unknown>) { setBusy(true); setMessage(''); try { await fn(); await refresh() } catch (e) { setMessage((e as Error).message) } finally { setBusy(false) } }
  return <div className="panel"><h2>Validate normal samples</h2><p>Select a fabric and provide at least four verified normal references. Validation uses the selected frozen profile and unchanged review threshold. It never trains or recalibrates.</p>
    <FabricSelect fabrics={fabrics.filter(f => f.profile)} value={id} onChange={s => { setId(s); setMessage('') }} />
    {f && <><p><strong>{f.profile}</strong> · {f.commissioning_samples} stored references · <Status value={f.commissioning_status} /></p>
      <div className="step-grid"><div><h3>Upload full source frames</h3><p>Use original parent frames, at least 256×256. Detached dataset crops need their catalog context; select them using the demo option.</p><label>Normal reference images<input type="file" accept="image/*" multiple onChange={e => setFiles(e.target.files)} /></label>
        <button className="secondary" disabled={busy || !files?.length} onClick={() => action(async () => { const b = new FormData(); Array.from(files ?? []).forEach(file => b.append('files', file)); await api(`/fabrics/${id}/samples`, { method: 'POST', body: b }); setMessage('Normal references stored.') })}>Store references</button></div>
        <div><h3>Or select demo references</h3><p>Use four normal training patches from {f.profile}. Their actual parent context is preserved.</p><button className="secondary" disabled={busy} onClick={() => action(async () => { const samples = await api<Sample[]>(`/demo/samples?profile=${f.profile}&split=train&limit=4`); await api(`/fabrics/${id}/sample-selection`, json({ paths: samples.map(s => s.path) })); setMessage('Four normal catalog references selected.') })}>Select normal demo samples</button></div></div>
      <button className="primary" disabled={busy || f.commissioning_samples < 4} onClick={() => action(async () => { const result = await api<Fabric>(`/fabrics/${id}/commission`, { method: 'POST' }); setMessage(result.commissioning_summary?.message ?? result.commissioning_status) })}>{busy ? 'Validating…' : 'Validate and activate frozen profile'}</button>
      {f.commissioning_summary && <p>{f.commissioning_summary.message}</p>}</>}
    <p role="status" aria-live="polite">{message}</p><p className="muted">New-fabric model fitting is not supported in this frozen research release.</p></div>
}
function Inspect({ fabrics, refresh }: { fabrics: Fabric[]; refresh: () => Promise<void> }) {
  const [id, setId] = useState(''), [file, setFile] = useState<File | null>(null), [samples, setSamples] = useState<Sample[]>([]), [selected, setSelected] = useState(''), [mode, setMode] = useState<'upload' | 'demo'>('upload')
  const [result, setResult] = useState<Result | null>(null), [error, setError] = useState(''), [busy, setBusy] = useState(false)
  const f = fabrics.find(f => f.fabric_id === id)
  useEffect(() => { setSelected(''); setSamples([]); if (f?.profile) { let active = true; api<Sample[]>(`/demo/samples?profile=${f.profile}&split=test&limit=24`).then(s => { if (active) setSamples(s) }).catch(() => {}); return () => { active = false } } }, [f?.profile])
  async function run() { setBusy(true); setError(''); setResult(null); try {
    let r: Result
    if (mode === 'demo') r = await api<Result>('/demo/inspect', json({ fabric_id: id, image_path: selected }))
    else { if (!file) throw new Error('Select a full source frame.'); const body = new FormData(); body.append('fabric_id', id); body.append('file', file); r = await api<Result>('/inspect', { method: 'POST', body }) }
    setResult(r); await refresh()
  } catch (e) { setError((e as Error).message) } finally { setBusy(false) } }
  return <><div className="intro-row"><div><h2>Inspect a fabric image</h2><p>Use the known, validated roll profile. A flagged result requests human review.</p></div></div><div className="inspect-layout"><div className="panel inspect-controls">
    <FabricSelect fabrics={fabrics.filter(f => f.commissioning_status === 'READY')} value={id} onChange={setId} />
    <div className="mode-toggle"><button onClick={() => setMode('upload')} className={mode === 'upload' ? 'active' : ''}>Upload frame</button><button onClick={() => setMode('demo')} className={mode === 'demo' ? 'active' : ''}>Select demo</button></div>
    {mode === 'upload' ? <label>Full parent image<input type="file" accept="image/*" onChange={e => setFile(e.target.files?.[0] ?? null)} /><small>No resizing. Detached known dataset crops must use the catalog.</small></label> : <div className="sample-grid">{samples.map(s => <button key={s.path} title={s.filename} className={selected === s.path ? 'selected' : ''} onClick={() => setSelected(s.path)}><img alt={s.filename} src={s.preview_url} /></button>)}{!samples.length && <p>Select a validated fabric to load local demo images.</p>}</div>}
    <button className="primary" disabled={busy || !id || (mode === 'demo' ? !selected : !file)} onClick={run}>{busy ? 'Inspecting…' : 'Run inspection'}</button>{error && <p role="alert">{error}</p>}</div>
    <div>{result ? <ResultCard result={result} /> : <div className="panel"><h3>Inspection evidence</h3><p>The original, heatmap, overlay and decision will appear here and be saved to history.</p></div>}</div></div></>
}
function ResultCard({ result }: { result: Result }) {
  return <div className="panel result-card"><div className="panel-head"><h3>Inspection result</h3><Status value={result.status} /></div><p>{result.explanation}</p><div className="evidence-grid">{(['original', 'anomaly_map', 'overlay'] as const).map((key, i) => <figure key={key}><img src={result.artifacts[key]} alt={['Original image', 'Anomaly heatmap', 'Anomalous region overlay'][i]} /><figcaption>{['Original', 'Anomaly heatmap', 'Evidence overlay'][i]}</figcaption></figure>)}</div>
    <div className="result-metrics"><div><span>Model anomaly score</span><b>{result.anomaly_score.toFixed(6)}</b></div><div><span>Flagged regions</span><b>{result.defect_count}</b></div><div><span>Time</span><b>{result.latency_ms.toFixed(1)} ms</b></div></div><p className="decision-note">The model detects anomalous texture, not defect cause or severity. HOLD requires human confirmation.</p>{result.review && <p>Human review: {result.review.decision.replaceAll('_', ' ')} · {result.review.notes}</p>}</div>
}
function HistoryPage({ rows, refresh }: { rows: Result[]; refresh: () => Promise<void> }) {
  const [selected, setSelected] = useState<Result | null>(null), [notes, setNotes] = useState(''), [error, setError] = useState(''), [busy, setBusy] = useState(false)
  async function review(decision: string) { if (!selected) return; setBusy(true); setError(''); try { const r = await api<Result>(`/inspections/${selected.inspection_id}/review`, json({ decision, notes })); setSelected(r); await refresh() } catch (e) { setError((e as Error).message) } finally { setBusy(false) } }
  return <><div className="panel"><h2>Saved inspection history</h2><p>Recent saved results, including earlier release evidence. Historical model labels remain recorded.</p><div className="table-wrap"><table><thead><tr><th>Time</th><th>Fabric</th><th>Model</th><th>Decision</th><th>Score</th><th>Evidence</th></tr></thead><tbody>{rows.map(r => <tr key={r.inspection_id}><td>{when(r.timestamp)}</td><td>{r.fabric_id}</td><td>{r.engine}</td><td><Status value={r.status} /></td><td>{r.anomaly_score.toFixed(4)}</td><td><button className="secondary" onClick={() => { setSelected(r); setNotes(''); setError('') }}>Open</button></td></tr>)}</tbody></table></div>{!rows.length && <p>No inspections yet.</p>}</div>
    {selected && <><ResultCard result={selected} />{selected.status !== 'PASS' && <div className="panel"><h3>Human review</h3><label>Review notes<textarea value={notes} onChange={e => setNotes(e.target.value)} /></label><div className="review-actions"><button disabled={busy} onClick={() => review('CONFIRMED_DEFECT')}>Confirm defect</button><button disabled={busy} onClick={() => review('FALSE_ALARM')}>False alarm</button><button disabled={busy} onClick={() => review('UNSURE')}>Unsure</button></div>{error && <p role="alert">{error}</p>}</div>}</>}</>
}
