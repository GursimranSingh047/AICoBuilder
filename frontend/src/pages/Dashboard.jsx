import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Sparkles, MessageSquare, Lightbulb, FolderOpen, ArrowRight, Clock, 
  CheckCircle, AlertCircle, Loader, Activity, BarChart3, TrendingUp,
  Users, Eye, Download
} from 'lucide-react'
import { projectsAPI } from '../api/client'
import { PageHeader, StatCard, SkeletonCard, EmptyState } from '../components/UI'
import { useAuth } from '../context/AuthContext'
import { API_BASE_URL } from '../config/api'

const statusIcon = {
  completed: <CheckCircle size={13} className="text-emerald" />,
  generating:<Loader size={13} className="text-amber animate-spin" />,
  failed:    <AlertCircle size={13} className="text-rose" />,
  pending:   <Clock size={13} className="text-muted" />,
}

const statusColor = {
  completed:  'tag-emerald',
  generating: 'tag-amber',
  failed:     'tag-rose',
  pending:    'tag-muted',
}

const quickActions = [
  { label: 'Generate Project', desc: 'Turn your idea into a full codebase', icon: Sparkles, to: '/generator', color: 'accent' },
  { label: 'AI Chat',          desc: 'Ask anything about your project',      icon: MessageSquare, to: '/chat', color: 'cyan' },
  { label: 'Get Suggestions',  desc: 'ML-powered stack recommendations',     icon: Lightbulb, to: '/suggestions', color: 'amber' },
  { label: 'Activity Feed',    desc: 'Track your project activities',        icon: Activity, to: '/activity', color: 'green' },
  { label: 'Analytics',        desc: 'View insights and performance',        icon: BarChart3, to: '/analytics', color: 'purple' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [activitySummary, setActivitySummary] = useState(null)
  const [realtimeStats, setRealtimeStats] = useState(null)

  useEffect(() => {
    // Fetch projects
    projectsAPI.list(0, 10)
      .then(r => setProjects(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))

    // Fetch activity summary
    fetch(`${API_BASE_URL}/activity/summary`, {
      headers: {
        'Authorization': user?.token ? `Bearer ${user.token}` : '',
        'Content-Type': 'application/json'
      }
    })
    .then(res => res.ok ? res.json() : null)
    .then(data => setActivitySummary(data))
    .catch(() => {})

    // Fetch realtime stats
    fetch(`${API_BASE_URL}/analytics/realtime`, {
      headers: {
        'Authorization': user?.token ? `Bearer ${user.token}` : '',
        'Content-Type': 'application/json'
      }
    })
    .then(res => res.ok ? res.json() : null)
    .then(data => setRealtimeStats(data))
    .catch(() => {})
  }, [user])

  const stats = {
    total:     projects.length,
    completed: projects.filter(p => p.status === 'completed').length,
    stacks:    [...new Set(projects.map(p => p.tech_stack?.frontend).filter(Boolean))].length,
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="px-8 py-8 max-w-5xl mx-auto"
    >
      <PageHeader
        title="Dashboard"
        subtitle="Your AI-powered project workspace"
        actions={
          <button onClick={() => navigate('/generator')} className="btn-primary">
            <Sparkles size={15} />
            New Project
          </button>
        }
      />

      {/* Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8"
      >
        <StatCard label="Total Projects"     value={stats.total}     icon={FolderOpen}    color="accent" />
        <StatCard label="Completed"          value={stats.completed} icon={CheckCircle}   color="emerald" />
        <StatCard label="Unique Stacks"      value={stats.stacks}    icon={Sparkles}      color="cyan" />
        <StatCard 
          label="Today's Activity" 
          value={activitySummary?.daily_activity_count || 0} 
          icon={Activity} 
          color="green" 
        />
        <StatCard 
          label="Active Generations" 
          value={realtimeStats?.active_generations || 0} 
          icon={TrendingUp} 
          color="purple" 
        />
      </motion.div>

      {/* Quick actions */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        className="mb-8"
      >
        <h2 className="text-sm font-semibold text-subtle mb-3 uppercase tracking-wider font-mono">Quick Actions</h2>
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          {quickActions.map(({ label, desc, icon: Icon, to, color }, index) => (
            <motion.button
              key={to}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1, duration: 0.6 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(to)}
              className="card-hover text-left group flex flex-col gap-3"
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center
                ${color === 'accent' ? 'bg-accent/15 border border-accent/25 text-accent' : ''}
                ${color === 'cyan'   ? 'bg-cyan/10   border border-cyan/20   text-cyan'   : ''}
                ${color === 'amber'  ? 'bg-amber/10  border border-amber/20  text-amber'  : ''}
                ${color === 'green'  ? 'bg-green-500/10  border border-green-500/20  text-green-400'  : ''}
                ${color === 'purple' ? 'bg-purple-500/10 border border-purple-500/20 text-purple-400' : ''}
              `}>
                <Icon size={17} />
              </div>
              <div>
                <p className="text-sm font-semibold text-white group-hover:text-accent transition-colors">{label}</p>
                <p className="text-xs text-muted mt-0.5">{desc}</p>
              </div>
              <ArrowRight size={14} className="text-muted group-hover:text-accent group-hover:translate-x-1 transition-all" />
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Recent projects */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
        >
          <h2 className="text-sm font-semibold text-subtle mb-3 uppercase tracking-wider font-mono">Recent Projects</h2>
          {loading ? (
            <div className="space-y-3">
              {[1,2,3].map(i => <SkeletonCard key={i} />)}
            </div>
          ) : projects.length === 0 ? (
            <EmptyState
              icon={FolderOpen}
              title="No projects yet"
              description="Generate your first project to get started"
              action={
                <button onClick={() => navigate('/generator')} className="btn-primary">
                  <Sparkles size={14} /> Generate Project
                </button>
              }
            />
          ) : (
            <div className="space-y-2">
              {projects.slice(0, 5).map((p, index) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1 + index * 0.1, duration: 0.6 }}
                  whileHover={{ scale: 1.01, x: 4 }}
                  onClick={() => navigate(`/projects/${p.id}`)}
                  className="card-hover flex items-center gap-4 cursor-pointer group"
                >
                  <div className="w-8 h-8 rounded-lg bg-surface-3 border border-border flex items-center justify-center flex-shrink-0">
                    <FolderOpen size={15} className="text-accent" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white group-hover:text-accent transition-colors truncate">{p.name}</p>
                    <p className="text-xs text-muted truncate">{p.tech_stack?.frontend || '—'} · {p.tech_stack?.backend || '—'}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className={statusColor[p.status] || 'tag-muted'}>
                      {statusIcon[p.status]}
                      {p.status}
                    </span>
                    <ArrowRight size={14} className="text-muted group-hover:text-accent" />
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Recent Activity Widget */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-subtle uppercase tracking-wider font-mono">Recent Activity</h2>
            <button 
              onClick={() => navigate('/activity')}
              className="text-xs text-accent hover:text-accent/80 transition-colors"
            >
              View All
            </button>
          </div>
          
          {activitySummary?.recent_activities ? (
            <div className="space-y-2">
              {activitySummary.recent_activities.slice(0, 5).map((activity, index) => (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.2 + index * 0.1, duration: 0.6 }}
                  className="card-hover flex items-center gap-3 text-sm"
                >
                  <div className="w-6 h-6 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center flex-shrink-0">
                    {activity.action === 'project_created' && <Sparkles size={12} className="text-accent" />}
                    {activity.action === 'project_viewed' && <Eye size={12} className="text-blue-400" />}
                    {activity.action === 'project_downloaded' && <Download size={12} className="text-green-400" />}
                    {activity.action === 'user_login' && <Users size={12} className="text-purple-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-xs truncate">
                      {activity.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    {activity.description && (
                      <p className="text-muted text-xs truncate">{activity.description}</p>
                    )}
                  </div>
                  <div className="text-xs text-muted flex-shrink-0">
                    {new Date(activity.created_at).toLocaleDateString()}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="card-hover flex items-center justify-center py-8">
              <div className="text-center">
                <Activity size={24} className="text-muted mx-auto mb-2" />
                <p className="text-xs text-muted">No recent activity</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  )
}
