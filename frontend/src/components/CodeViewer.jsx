import React, { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check, FileCode } from 'lucide-react'

function langFromPath(path = '') {
  const ext = path.split('.').pop()
  const map = {
    py: 'python', js: 'javascript', jsx: 'jsx', ts: 'typescript',
    tsx: 'tsx', json: 'json', md: 'markdown', css: 'css',
    html: 'html', yml: 'yaml', yaml: 'yaml', sh: 'bash',
    sql: 'sql', env: 'bash', txt: 'text',
  }
  return map[ext] || 'text'
}

export default function CodeViewer({ path, content }) {
  const [copied, setCopied] = useState(false)

  const copy = () => {
    if (!content) return
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-surface-1 border border-border rounded-xl overflow-hidden h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border flex-shrink-0">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald/60" />
        </div>
        <FileCode size={13} className="text-muted" />
        <span className="text-xs font-mono text-subtle flex-1 truncate">{path || 'Select a file'}</span>
        {content && (
          <button onClick={copy} className="flex items-center gap-1.5 text-xs text-muted hover:text-white transition-colors">
            {copied ? <Check size={13} className="text-emerald" /> : <Copy size={13} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        )}
      </div>

      {/* Code */}
      <div className="flex-1 overflow-auto">
        {!content ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-muted py-16">
            <FileCode size={32} className="opacity-30" />
            <p className="text-sm">Select a file from the tree</p>
          </div>
        ) : (
          <SyntaxHighlighter
            language={langFromPath(path)}
            style={vscDarkPlus}
            showLineNumbers
            wrapLongLines={false}
            customStyle={{
              margin: 0,
              background: 'transparent',
              padding: '16px',
              fontSize: '12.5px',
              lineHeight: '1.6',
            }}
            lineNumberStyle={{ color: '#3a3a4a', minWidth: '2.5em' }}
          >
            {content}
          </SyntaxHighlighter>
        )}
      </div>
    </div>
  )
}
