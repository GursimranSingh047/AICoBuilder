import React, { useState, useEffect } from 'react'
import { Zap, Lightbulb, BarChart2, CheckCircle, ArrowRight } from 'lucide-react'
import { suggestAPI } from '../api/client'
import { PageHeader, ErrorBanner, Spinner } from '../components/UI'
import { useNavigate } from 'react-router-dom'

const TYPE_COLORS = {
  ecommerce: 'tag-amber',   social: 'tag-cyan',  analytics: 'tag-accent',
  cms: 'tag-emerald',       saas: 'tag-accent',   mobile: 'tag-cyan',
  productivity: 'tag-emerald', api: 'tag-amber',  ml: 'tag-accent',
  game: 'tag-rose',          fintech: 'tag-amber', healthcare: 'tag-emerald',
  education: 'tag-cyan',
}

const STACK_ICON = { frontend: '🖥', backend: '⚙️', database: '🗄', extra: '✨' }

export default function Suggestions() {
  const navigate = useNavigate()
  const [idea, setIdea]           = useState('')
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [allStacks, setAllStacks] = useState(null)
  const [activeType, setActiveType] = useState(null)
  const [typeFeatures, setTypeFeatures] = useState([])

  // Load all stacks for the explorer
  useEffect(() => {
    suggestAPI.stacks().then(r => setAllStacks(r.data)).catch(() => {})
  }, [])

  const handleSuggest = async () => {
    if (!idea.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { data } = await suggestAPI.suggest(idea)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleTypeClick = async (type) => {
    setActiveType(type)
    try {
      const { data } = await suggestAPI.features(type)
      setTypeFeatures(data.features || [])
    } catch { setTypeFeatures([]) }
  }

  const confidencePct = result ? Math.round(result.confidence * 100) : 0

  return (
    <div className="px-8 py-8 max-w-4xl mx-auto animate-fade-in">
      <PageHeader
        title="ML Suggestions"
        subtitle="Predict the ideal stack and features from your idea"
      />

      {/* Input */}
      <div className="card mb-6 space-y-4">
        <label className="text-xs font-mono text-muted uppercase tracking-wider block">Your Project Idea</label>
        <div className="flex gap-3">
          <input
            value={idea}
            onChange={e => setIdea(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSuggest()}
            placeholder="e.g. A social platform for developers to share code snippets"
            className="input-base flex-1"
          />
          <button onClick={handleSuggest} disabled={!idea.trim() || loading} className="btn-primary">
            {loading ? <Spinner size={15} /> : <Zap size={15} />}
            {loading ? 'Analysing…' : 'Analyse'}
          </button>
        </div>
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-4 animate-slide-up mb-8">
          {/* Type + confidence */}
          <div className="card flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center">
                <BarChart2 size={18} className="text-accent" />
              </div>
              <div>
                <p className="text-xs text-muted font-mono uppercase tracking-wider">Detected Type</p>
                <p className="text-lg font-display font-bold text-white capitalize">{result.project_type}</p>
              </div>
            </div>
            {/* Confidence bar */}
            <div className="flex-1 max-w-xs">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-muted font-mono">Confidence</span>
                <span className="text-xs text-accent font-mono font-medium">{confidencePct}%</span>
              </div>
              <div className="h-1.5 bg-surface-3 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all duration-700"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
            </div>
            <button
              onClick={() => navigate(`/generator?idea=${encodeURIComponent(idea)}`)}
              className="btn-primary flex-shrink-0"
            >
              Generate Project <ArrowRight size={14} />
            </button>
          </div>

          {/* Stack grid */}
          <div>
            <h3 className="text-xs text-muted font-mono uppercase tracking-wider mb-3">Recommended Stack</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(result.recommended_stack).map(([key, value]) => (
                <div key={key} className="card flex items-center gap-3">
                  <span className="text-lg">{STACK_ICON[key] || '🔧'}</span>
                  <div>
                    <p className="text-[10px] text-muted uppercase tracking-wider font-mono">{key}</p>
                    <p className="text-sm font-semibold text-white">{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-xs text-muted font-mono uppercase tracking-wider mb-3">Suggested Features</h3>
            <div className="grid grid-cols-2 gap-2">
              {result.suggested_features.map(f => (
                <div key={f} className="flex items-center gap-2 bg-surface-2 border border-border rounded-lg px-3 py-2">
                  <CheckCircle size={13} className="text-emerald flex-shrink-0" />
                  <span className="text-sm text-subtle">{f}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Stack Explorer */}
      {allStacks && (
        <div>
          <h2 className="font-display text-lg font-bold text-white mb-1">Stack Explorer</h2>
          <p className="text-sm text-muted mb-4">Browse recommended stacks by project type</p>
          <div className="grid grid-cols-4 gap-2 mb-4">
            {Object.keys(allStacks).map(type => (
              <button
                key={type}
                onClick={() => handleTypeClick(type)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all capitalize border
                  ${activeType === type
                    ? 'bg-accent text-white border-accent'
                    : 'bg-surface-2 border-border text-muted hover:text-white hover:border-accent/40'
                  }`}
              >
                {type}
              </button>
            ))}
          </div>

          {activeType && (
            <div className="card animate-slide-up space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white capitalize">{activeType} Stack</h3>
                <span className={TYPE_COLORS[activeType] || 'tag-muted'}>{activeType}</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(allStacks[activeType]).map(([k, v]) => (
                  <div key={k} className="bg-surface-2 rounded-lg p-3 border border-border">
                    <p className="text-[10px] text-muted uppercase tracking-wider font-mono mb-1">{STACK_ICON[k]} {k}</p>
                    <p className="text-sm text-white font-medium">{v}</p>
                  </div>
                ))}
              </div>
              {typeFeatures.length > 0 && (
                <div>
                  <p className="text-xs text-muted font-mono uppercase tracking-wider mb-2">Features</p>
                  <div className="flex flex-wrap gap-2">
                    {typeFeatures.map(f => (
                      <span key={f} className="tag-muted">{f}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
