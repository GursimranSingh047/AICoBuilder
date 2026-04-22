import React, { useState } from 'react'
import { ChevronRight, ChevronDown, FileCode, Folder, FolderOpen } from 'lucide-react'

// ─── Derive icon color from extension ────────────────────────────────────────
function fileColor(name) {
  const ext = name.split('.').pop()
  const map = {
    py: 'text-cyan',   jsx: 'text-accent', tsx: 'text-accent',
    js: 'text-amber',  ts: 'text-cyan',    json: 'text-amber',
    md: 'text-emerald',css: 'text-rose',   html: 'text-amber',
    yml: 'text-rose',  yaml: 'text-rose',  env: 'text-muted',
    txt: 'text-muted', sql: 'text-cyan',   sh: 'text-emerald',
  }
  return map[ext] || 'text-muted'
}

// ─── Build tree from flat path map ────────────────────────────────────────────
export function buildTree(files) {
  const root = {}
  Object.keys(files || {}).forEach((path) => {
    const parts = path.split('/')
    let node = root
    parts.forEach((part, i) => {
      if (!node[part]) node[part] = i === parts.length - 1 ? null : {}
      if (i < parts.length - 1) node = node[part]
    })
  })
  return root
}

// ─── Recursive tree node ──────────────────────────────────────────────────────
function TreeNode({ name, node, depth = 0, onSelect, selected, pathPrefix = '' }) {
  const [open, setOpen] = useState(depth === 0)
  const isFolder = node !== null && typeof node === 'object'
  const fullPath = pathPrefix ? `${pathPrefix}/${name}` : name

  if (isFolder) {
    return (
      <div>
        <button
          onClick={() => setOpen(o => !o)}
          className="flex items-center gap-1.5 w-full text-left px-2 py-1 rounded hover:bg-surface-3 transition-colors group"
          style={{ paddingLeft: `${depth * 14 + 8}px` }}
        >
          {open
            ? <ChevronDown size={13} className="text-muted flex-shrink-0" />
            : <ChevronRight size={13} className="text-muted flex-shrink-0" />
          }
          {open
            ? <FolderOpen size={13} className="text-amber flex-shrink-0" />
            : <Folder size={13} className="text-amber flex-shrink-0" />
          }
          <span className="text-xs text-subtle group-hover:text-white truncate">{name}</span>
        </button>
        {open && Object.entries(node).map(([child, childNode]) => (
          <TreeNode
            key={child}
            name={child}
            node={childNode}
            depth={depth + 1}
            onSelect={onSelect}
            selected={selected}
            pathPrefix={fullPath}
          />
        ))}
      </div>
    )
  }

  return (
    <button
      onClick={() => onSelect?.(fullPath)}
      className={`flex items-center gap-1.5 w-full text-left px-2 py-1 rounded transition-colors group
        ${selected === fullPath ? 'bg-accent/15 text-accent' : 'hover:bg-surface-3'}`}
      style={{ paddingLeft: `${depth * 14 + 8}px` }}
    >
      <FileCode size={13} className={`flex-shrink-0 ${fileColor(name)}`} />
      <span className={`text-xs truncate ${selected === fullPath ? 'text-accent' : 'text-subtle group-hover:text-white'}`}>
        {name}
      </span>
    </button>
  )
}

// ─── FileTree ─────────────────────────────────────────────────────────────────
export default function FileTree({ files = {}, onSelect, selected }) {
  const tree = buildTree(files)

  return (
    <div className="bg-surface-1 border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald/60" />
        </div>
        <span className="text-xs font-mono text-muted ml-1">Project Files</span>
        <span className="ml-auto text-[10px] tag-muted">{Object.keys(files).length} files</span>
      </div>

      {/* Tree */}
      <div className="py-2 max-h-96 overflow-y-auto font-mono">
        {Object.keys(files).length === 0 ? (
          <p className="text-xs text-muted text-center py-8">No files generated yet</p>
        ) : (
          Object.entries(tree).map(([name, node]) => (
            <TreeNode
              key={name}
              name={name}
              node={node}
              depth={0}
              onSelect={onSelect}
              selected={selected}
              pathPrefix=""
            />
          ))
        )}
      </div>
    </div>
  )
}
