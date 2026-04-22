import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Sparkles, MessageSquare, Lightbulb,
  LogOut, LogIn, User, Zap
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const links = [
  { to: '/',           label: 'Dashboard',  icon: LayoutDashboard, end: true },
  { to: '/generator',  label: 'Generator',  icon: Sparkles },
  { to: '/chat',       label: 'AI Chat',    icon: MessageSquare },
  { to: '/suggestions',label: 'Suggestions',icon: Lightbulb },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <aside className="w-60 flex-shrink-0 h-screen flex flex-col border-r border-border bg-surface-1">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center animate-pulse-glow">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <div className="font-display text-base font-bold text-white leading-none">ProjectPilot</div>
            <div className="text-[10px] text-muted font-mono mt-0.5">AI Co-Builder</div>
          </div>
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-[10px] font-mono uppercase text-muted/60 px-3 pb-2 tracking-wider">Navigation</p>
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `sidebar-link${isActive ? ' active' : ''}`
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-border">
        {user ? (
          <div className="space-y-1">
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="w-7 h-7 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center">
                <User size={13} className="text-accent" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{user.username}</p>
                <p className="text-[10px] text-muted truncate">{user.email}</p>
              </div>
            </div>
            <button onClick={logout} className="sidebar-link w-full">
              <LogOut size={15} />
              <span>Sign out</span>
            </button>
          </div>
        ) : (
          <div className="space-y-1">
            <button onClick={() => navigate('/login')} className="sidebar-link w-full">
              <LogIn size={15} />
              <span>Sign in</span>
            </button>
            <button onClick={() => navigate('/signup')} className="btn-primary w-full justify-center text-xs">
              Get started
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}
