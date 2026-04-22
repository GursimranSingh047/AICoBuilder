import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Download, ArrowLeft, CheckCircle, Loader, AlertCircle,
  Clock, ExternalLink, Trash2, FolderOpen, Code2
} from 'lucide-react'
import { projectsAPI, chatAPI } from '../api/client'
import { PageLoader, ErrorBanner, Spinner } from '../components/UI'
import FileTree from '../components/FileTree'
import CodeViewer from '../components/CodeViewer'

const statusMap = {
  completed:  { icon: CheckCircle, color: 'text-emerald', bg: 'bg-emerald/10 border-emerald/20', label: 'Completed' },
  generating: { icon: Loader,      color: 'text-amber',   bg: 'bg-amber/10  border-amber/20',   label: 'Generating…' },
  failed:     { icon: AlertCircle, color: 'text-rose',    bg: 'bg-rose/10   border-rose/20',    label: 'Failed' },
  pending:    { icon: Clock,       color: 'text-muted',   bg: 'bg-surface-3 border-border',     label: 'Pending' },
}

export default function ProjectViewer() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [project, setProject]       = useState(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [deleting, setDeleting]     = useState(false)

  // AI explain panel
  const [explaining, setExplaining] = useState(false)
  const [explanation, setExplanation] = useState(null)

  useEffect(() => {
    projectsAPI.get(id)
      .then(r => {
        setProject(r.data)
        // Auto-select README.md or first file
        const files = r.data.generated_files || {}
        const first = files['README.md'] ? 'README.md' : Object.keys(files)[0] || null
        setSelectedFile(first)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!window.confirm('Delete this project? This cannot be undone.')) return
    setDeleting(true)
    try {
      await projectsAPI.delete(id)
      navigate('/')
    } catch (e) {
      setError(e.message)
      setDeleting(false)
    }
  }

  const handleExplain = async () => {
    const content = project?.generated_files?.[selectedFile]
    if (!content) return
    setExplaining(true)
    setExplanation(null)
    try {
      const { data } = await chatAPI.explain(content.slice(0, 3000))
      setExplanation(data.explanation)
    } catch (e) {
      setExplanation('Could not get explanation: ' + e.message)
    } finally {
      setExplaining(false)
    }
  }

  if (loading) return <PageLoader message="Loading project…" />
  if (error)   return (
    <div className="px-8 py-8 max-w-4xl mx-auto">
      <ErrorBanner message={error} />
      <button onClick={() => navigate('/')} className="btn-ghost mt-4">
        <ArrowLeft size={14} /> Back to Dashboard
      </button>
    </div>
  )
  if (!project) return null

  const files = project.generated_files || {}
  const StatusIcon = statusMap[project.status]?.icon || Clock
  const statusStyle = statusMap[project.status] || statusMap.pending

  return (
    <div className="px-8 py-8 max-w-7xl mx-auto animate-fade-in">

      {/* Top bar */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/')} className="btn-ghost px-2">
          <ArrowLeft size={16} />
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="font-display text-2xl font-bold text-white truncate">{project.name}</h1>
          <p className="text-xs text-muted mt-0.5 truncate">{project.idea_prompt}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Status badge */}
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium ${statusStyle.bg} ${statusStyle.color}`}>
            <StatusIcon size={12} className={project.status === 'generating' ? 'animate-spin' : ''} />
            {statusStyle.label}
          </span>
          {/* Explain button */}
          {selectedFile && files[selectedFile] && (
            <button onClick={handleExplain} disabled={explaining} className="btn-outline text-xs">
              {explaining ? <Spinner size={13} /> : <Code2 size={13} />}
              Explain File
            </button>
          )}
          {/* Download */}
          <a
            href={projectsAPI.downloadUrl(id)}
            className="btn-outline text-xs"
            download
          >
            <Download size={13} /> ZIP
          </a>
          {/* Delete */}
          <button onClick={handleDelete} disabled={deleting} className="btn-ghost text-xs text-rose hover:bg-rose/10">
            {deleting ? <Spinner size={13} /> : <Trash2 size={13} />}
          </button>
        </div>
      </div>

      {/* Tech stack strip */}
      <div className="flex flex-wrap gap-2 mb-5">
        {Object.entries(project.tech_stack || {}).map(([k, v]) => (
          <div key={k} className="flex items-center gap-1.5 bg-surface-2 border border-border rounded-lg px-3 py-1.5">
            <span className="text-[10px] text-muted font-mono uppercase">{k}</span>
            <span className="text-xs text-white font-medium">{v}</span>
          </div>
        ))}
        <span className="ml-auto text-xs text-muted self-center font-mono">
          {Object.keys(files).length} files generated
        </span>
      </div>

      {/* Main content: tree + code viewer */}
      <div className="grid grid-cols-12 gap-4" style={{ height: '560px' }}>

        {/* File tree */}
        <div className="col-span-3 overflow-hidden flex flex-col">
          <FileTree
            files={files}
            onSelect={f => { setSelectedFile(f); setExplanation(null) }}
            selected={selectedFile}
          />
        </div>

        {/* Code viewer + explanation */}
        <div className="col-span-9 flex flex-col gap-3 overflow-hidden">
          <div className={explanation ? 'flex-1' : 'h-full'}>
            <CodeViewer
              path={selectedFile}
              content={selectedFile ? files[selectedFile] : null}
            />
          </div>

          {/* AI explanation panel */}
          {(explanation || explaining) && (
            <div className="bg-surface-1 border border-accent/20 rounded-xl p-4 animate-slide-up flex-shrink-0 max-h-44 overflow-y-auto">
              <div className="flex items-center gap-2 mb-2">
                <Code2 size={13} className="text-accent" />
                <span className="text-xs font-semibold text-accent font-mono uppercase tracking-wider">AI Explanation</span>
                <button onClick={() => setExplanation(null)} className="ml-auto text-muted hover:text-white text-sm">&times;</button>
              </div>
              {explaining
                ? <div className="flex items-center gap-2 text-sm text-muted"><Spinner size={14} /> Analysing file…</div>
                : <p className="text-sm text-subtle whitespace-pre-wrap leading-relaxed">{explanation}</p>
              }
            </div>
          )}
        </div>
      </div>

      {/* Folder structure preview */}
      {project.folder_structure && Object.keys(project.folder_structure).length > 0 && (
        <div className="mt-6 card">
          <p className="text-xs text-muted font-mono uppercase tracking-wider mb-3 flex items-center gap-2">
            <FolderOpen size={13} /> Scaffold Structure
          </p>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(project.folder_structure).map(([layer, dirs]) => (
              <div key={layer}>
                <p className="text-xs font-semibold text-subtle capitalize mb-2">{layer}</p>
                <div className="space-y-1">
                  {(dirs || []).map(d => (
                    <div key={d} className="flex items-center gap-2 text-xs text-muted font-mono">
                      <span className="text-amber">📁</span> {d}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
