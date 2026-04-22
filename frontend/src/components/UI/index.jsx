import React from 'react'
import { Loader2, PackageOpen } from 'lucide-react'

// ─── Spinner ─────────────────────────────────────────────────────────────────
export function Spinner({ size = 18, className = '' }) {
  return <Loader2 size={size} className={`animate-spin text-accent ${className}`} />
}

// ─── Full-page loader ─────────────────────────────────────────────────────────
export function PageLoader({ message = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-32 text-muted">
      <Spinner size={28} />
      <p className="text-sm font-mono">{message}</p>
    </div>
  )
}

// ─── Skeleton shimmer line ────────────────────────────────────────────────────
export function SkeletonLine({ w = 'w-full', h = 'h-4' }) {
  return <div className={`shimmer-line rounded ${w} ${h}`} />
}

// ─── Skeleton card ────────────────────────────────────────────────────────────
export function SkeletonCard() {
  return (
    <div className="card animate-pulse space-y-3">
      <SkeletonLine w="w-1/3" h="h-4" />
      <SkeletonLine w="w-2/3" h="h-3" />
      <SkeletonLine w="w-1/2" h="h-3" />
    </div>
  )
}

// ─── Error banner ─────────────────────────────────────────────────────────────
export function ErrorBanner({ message, onDismiss }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-3 p-4 bg-rose/10 border border-rose/20 rounded-xl text-rose text-sm animate-fade-in">
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="text-rose/60 hover:text-rose text-lg leading-none">&times;</button>
      )}
    </div>
  )
}

// ─── Empty state ─────────────────────────────────────────────────────────────
export function EmptyState({ icon: Icon = PackageOpen, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
      <div className="w-14 h-14 rounded-2xl bg-surface-3 border border-border flex items-center justify-center">
        <Icon size={24} className="text-muted" />
      </div>
      <div>
        <p className="text-white font-medium">{title}</p>
        {description && <p className="text-sm text-muted mt-1 max-w-xs">{description}</p>}
      </div>
      {action}
    </div>
  )
}

// ─── Section header ───────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-start justify-between gap-4 mb-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-white">{title}</h1>
        {subtitle && <p className="text-sm text-muted mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}

// ─── Stat card ────────────────────────────────────────────────────────────────
export function StatCard({ label, value, icon: Icon, color = 'accent' }) {
  const colorMap = {
    accent:  'text-accent bg-accent/10 border-accent/20',
    cyan:    'text-cyan bg-cyan/10 border-cyan/20',
    emerald: 'text-emerald bg-emerald/10 border-emerald/20',
    amber:   'text-amber bg-amber/10 border-amber/20',
  }
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${colorMap[color]}`}>
        <Icon size={18} />
      </div>
      <div>
        <p className="text-2xl font-display font-bold text-white">{value}</p>
        <p className="text-xs text-muted">{label}</p>
      </div>
    </div>
  )
}
