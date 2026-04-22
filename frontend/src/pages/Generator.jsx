import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Zap, ArrowRight, RotateCcw, Download, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import { projectsAPI, suggestAPI } from '../api/client'
import { PageHeader, ErrorBanner, Spinner } from '../components/UI'
import FileTree from '../components/FileTree'
import CodeViewer from '../components/CodeViewer'

const EXAMPLE_IDEAS = [
  'A SaaS dashboard for monitoring API usage with charts and billing',
  'A real-time collaborative whiteboard app with rooms and auth',
  'An ecommerce store with cart, Stripe checkout, and admin panel',
  'A blog CMS with markdown editor and tag-based filtering',
  'A social platform for developers to share code snippets',
]

export default function Generator() {
  const navigate = useNavigate()
  const [idea, setIdea]             = useState('')
  const [projectName, setProjectName] = useState('')
  const [loading, setLoading]       = useState(false)
  const [suggesting, setSuggesting] = useState(false)
  const [error, setError]           = useState(null)
  const [result, setResult]         = useState(null)
  const [suggestion, setSuggestion] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [showAllFiles, setShowAllFiles] = useState(false)

  // ── Quick ML suggestion ─────────────────────────────────────────────────
  const handleSuggest = async () => {
    if (!idea.trim()) return
    setSuggesting(true)
    try {
      const { data } = await suggestAPI.suggest(idea)
      setSuggestion(data)
    } catch (e) {
      // non-blocking
    } finally {
      setSuggesting(false)
    }
  }

  // ── Generate full project ───────────────────────────────────────────────
  const handleGenerate = async () => {
    if (!idea.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    setSuggestion(null)
    setSelectedFile(null)
    try {
      const { data } = await projectsAPI.generate(idea, projectName || null)
      setResult(data)
      // Auto-select README
      if (data.files?.['README.md']) setSelectedFile('README.md')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => { setResult(null); setSuggestion(null); setIdea(''); setProjectName(''); setError(null) }

  const files = result?.files || {}
  const visibleFiles = showAllFiles ? Object.keys(files) : Object.keys(files).slice(0, 8)

  return (
    <div className="px-8 py-8 max-w-6xl mx-auto animate-fade-in">
      <PageHeader
        title="Project Generator"
        subtitle="Describe your idea — AI builds the full project"
        actions={result && (
          <button onClick={reset} className="btn-ghost">
            <RotateCcw size={14} /> New Project
          </button>
        )}
      />

      {!result ? (
        /* ── Input panel ───────────────────────────────────────────────── */
        <div className="max-w-2xl mx-auto space-y-5 animate-slide-up">

          {/* Idea input */}
          <div className="card space-y-4">
            <div>
              <label className="text-xs font-mono text-muted uppercase tracking-wider mb-2 block">Your Idea</label>
              <textarea
                value={idea}
                onChange={e => setIdea(e.target.value)}
                placeholder="Describe what you want to build…"
                rows={4}
                className="input-base resize-none leading-relaxed"
              />
            </div>
            <div>
              <label className="text-xs font-mono text-muted uppercase tracking-wider mb-2 block">Project Name <span className="text-muted/50">(optional)</span></label>
              <input
                value={projectName}
                onChange={e => setProjectName(e.target.value)}
                placeholder="e.g. TaskFlow"
                className="input-base"
              />
            </div>

            <div className="flex gap-3">
              <button onClick={handleSuggest} disabled={!idea.trim() || suggesting} className="btn-outline flex-1">
                {suggesting ? <Spinner size={14} /> : <Zap size={14} />}
                {suggesting ? 'Analysing…' : 'Get Suggestions'}
              </button>
              <button onClick={handleGenerate} disabled={!idea.trim() || loading} className="btn-primary flex-1">
                {loading ? <Spinner size={14} /> : <Sparkles size={14} />}
                {loading ? 'Generating…' : 'Generate Project'}
              </button>
            </div>
          </div>

          {/* Loading progress */}
          {loading && (
            <div className="card space-y-3 animate-fade-in">
              <div className="flex items-center gap-3">
                <Spinner size={16} />
                <span className="text-sm text-subtle">Building your project…</span>
              </div>
              {['Analysing idea with ML model', 'Selecting tech stack', 'Scaffolding folder structure', 'Generating code with Gemini', 'Writing README'].map((step, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-muted" style={{ animationDelay: `${i * 0.4}s` }}>
                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" style={{ animationDelay: `${i * 0.3}s` }} />
                  {step}
                </div>
              ))}
            </div>
          )}

          {/* ML suggestion result */}
          {suggestion && !loading && (
            <div className="card animate-slide-up space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">ML Recommendations</p>
                <span className="tag-accent">
                  {suggestion.project_type} · {Math.round(suggestion.confidence * 100)}% conf
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(suggestion.recommended_stack).map(([k, v]) => (
                  <div key={k} className="bg-surface-2 rounded-lg p-3 border border-border">
                    <p className="text-[10px] text-muted uppercase tracking-wider font-mono mb-1">{k}</p>
                    <p className="text-sm text-white font-medium">{v}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-[10px] text-muted uppercase tracking-wider font-mono mb-2">Suggested Features</p>
                <div className="flex flex-wrap gap-2">
                  {suggestion.suggested_features.map(f => (
                    <span key={f} className="tag-muted">{f}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Example ideas */}
          <div>
            <p className="text-xs text-muted mb-2 font-mono">Example ideas:</p>
            <div className="space-y-1.5">
              {EXAMPLE_IDEAS.map(ex => (
                <button
                  key={ex}
                  onClick={() => setIdea(ex)}
                  className="w-full text-left text-xs text-muted hover:text-white bg-surface-1 hover:bg-surface-2 border border-border hover:border-accent/30 rounded-lg px-3 py-2 transition-all"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      ) : (
        /* ── Result panel ──────────────────────────────────────────────── */
        <div className="animate-slide-up space-y-6">

          {/* Project meta */}
          <div className="card flex items-start justify-between gap-4">
            <div>
              <h2 className="font-display text-xl font-bold text-white">{result.name}</h2>
              <p className="text-sm text-muted mt-1">{idea.slice(0, 120)}{idea.length > 120 ? '…' : ''}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                {Object.entries(result.tech_stack || {}).map(([k, v]) => (
                  <span key={k} className="tag-muted"><span className="text-muted/60">{k}:</span> {v}</span>
                ))}
              </div>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <a
                href={projectsAPI.downloadUrl(result.project_id)}
                className="btn-outline"
                download
              >
                <Download size={14} /> Download ZIP
              </a>
              <button
                onClick={() => navigate(`/projects/${result.project_id}`)}
                className="btn-primary"
              >
                Open Viewer <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* File explorer + code viewer */}
          <div className="grid grid-cols-5 gap-4" style={{ height: '520px' }}>
            <div className="col-span-2 overflow-hidden">
              <FileTree
                files={files}
                onSelect={setSelectedFile}
                selected={selectedFile}
              />
            </div>
            <div className="col-span-3 overflow-hidden">
              <CodeViewer
                path={selectedFile}
                content={selectedFile ? files[selectedFile] : null}
              />
            </div>
          </div>

          {/* Features */}
          {result.tech_stack?.project_type && (
            <div className="card">
              <p className="text-xs text-muted uppercase tracking-wider font-mono mb-3">Detected Project Type</p>
              <span className="tag-accent">{result.tech_stack.project_type}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
