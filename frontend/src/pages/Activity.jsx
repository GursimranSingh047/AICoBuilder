import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ClockIcon, 
  EyeIcon, 
  ArrowDownTrayIcon,
  UserIcon,
  FolderIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { API_BASE_URL } from '../config/api'

const Activity = () => {
  const { user } = useAuth()
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [actionFilter, setActionFilter] = useState('')
  const [summary, setSummary] = useState(null)

  const fetchActivities = async (pageNum = 1, filter = '') => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: pageNum,
        per_page: 20,
        ...(filter && { action_filter: filter })
      })

      const response = await fetch(`${API_BASE_URL}/activity/feed?${params}`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setActivities(data.activities)
        setTotalPages(Math.ceil(data.total / data.per_page))
      } else {
        toast.error('Failed to load activities')
      }
    } catch (error) {
      console.error('Error fetching activities:', error)
      toast.error('Failed to load activities')
    } finally {
      setLoading(false)
    }
  }

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/activity/summary`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSummary(data)
      }
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  useEffect(() => {
    fetchActivities(page, actionFilter)
    fetchSummary()
  }, [page, actionFilter, user])

  const getActionIcon = (action) => {
    switch (action) {
      case 'project_created':
        return <FolderIcon className="w-5 h-5 text-green-400" />
      case 'project_viewed':
        return <EyeIcon className="w-5 h-5 text-blue-400" />
      case 'project_downloaded':
        return <ArrowDownTrayIcon className="w-5 h-5 text-purple-400" />
      case 'user_login':
        return <UserIcon className="w-5 h-5 text-yellow-400" />
      default:
        return <ClockIcon className="w-5 h-5 text-gray-400" />
    }
  }

  const getActionColor = (action) => {
    switch (action) {
      case 'project_created':
        return 'bg-green-500/10 text-green-400 border-green-500/20'
      case 'project_viewed':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      case 'project_downloaded':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
      case 'user_login':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
  }

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)

    if (diffInSeconds < 60) return 'Just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
    return date.toLocaleDateString()
  }

  const actionFilters = [
    { value: '', label: 'All Activities' },
    { value: 'project_created', label: 'Projects Created' },
    { value: 'project_viewed', label: 'Projects Viewed' },
    { value: 'project_downloaded', label: 'Downloads' },
    { value: 'user_login', label: 'Logins' }
  ]

  if (loading && activities.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Activity Feed</h1>
          <p className="text-gray-400">Track your project activities and engagement</p>
        </motion.div>

        {/* Summary Cards */}
        {summary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Activities</p>
                  <p className="text-2xl font-bold text-white">{summary.total_activities}</p>
                </div>
                <ClockIcon className="w-8 h-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Today</p>
                  <p className="text-2xl font-bold text-white">{summary.daily_activity_count}</p>
                </div>
                <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                  <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">This Week</p>
                  <p className="text-2xl font-bold text-white">{summary.weekly_activity_count}</p>
                </div>
                <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                  <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Top Action</p>
                  <p className="text-lg font-semibold text-white">
                    {summary.top_actions[0]?.action.replace('_', ' ') || 'None'}
                  </p>
                </div>
                <FunnelIcon className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
          </motion.div>
        )}

        {/* Filter Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="flex flex-wrap gap-3">
            {actionFilters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => {
                  setActionFilter(filter.value)
                  setPage(1)
                }}
                className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                  actionFilter === filter.value
                    ? 'bg-blue-500/20 text-blue-400 border-blue-500/50'
                    : 'bg-gray-800/50 text-gray-400 border-gray-700/50 hover:bg-gray-700/50'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Activity List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl overflow-hidden"
        >
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <LoadingSpinner />
            </div>
          ) : activities.length === 0 ? (
            <div className="text-center p-12">
              <ClockIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No Activities Found</h3>
              <p className="text-gray-500">Start using the platform to see your activity here</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700/50">
              {activities.map((activity, index) => (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-6 hover:bg-gray-700/30 transition-colors duration-200"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className={`w-10 h-10 rounded-full border flex items-center justify-center ${getActionColor(activity.action)}`}>
                        {getActionIcon(activity.action)}
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-white font-medium">
                            {activity.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </p>
                          {activity.description && (
                            <p className="text-gray-400 text-sm mt-1">{activity.description}</p>
                          )}
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            {activity.user_name && (
                              <span className="flex items-center space-x-1">
                                <UserIcon className="w-3 h-3" />
                                <span>{activity.user_name}</span>
                              </span>
                            )}
                            {activity.project_name && (
                              <span className="flex items-center space-x-1">
                                <FolderIcon className="w-3 h-3" />
                                <span>{activity.project_name}</span>
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-gray-400 text-sm">{formatTimeAgo(activity.created_at)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Pagination */}
        {totalPages > 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center space-x-4 mt-8"
          >
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-400 hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <ChevronLeftIcon className="w-4 h-4" />
              <span>Previous</span>
            </button>
            
            <span className="text-gray-400">
              Page {page} of {totalPages}
            </span>
            
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-400 hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <span>Next</span>
              <ChevronRightIcon className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Activity