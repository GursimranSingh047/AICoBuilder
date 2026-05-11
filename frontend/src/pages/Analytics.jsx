import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import {
  ChartBarIcon,
  ClockIcon,
  UserGroupIcon,
  CpuChipIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  CodeBracketIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { API_BASE_URL } from '../config/api'

const Analytics = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState(null)
  const [progressChart, setProgressChart] = useState(null)
  const [activityChart, setActivityChart] = useState(null)
  const [techStackChart, setTechStackChart] = useState(null)
  const [timeRange, setTimeRange] = useState('LAST_30_DAYS')

  const fetchDashboardAnalytics = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/analytics/dashboard`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        toast.error('Failed to load analytics')
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
      toast.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  const fetchChartData = async () => {
    try {
      // Fetch progress chart
      const progressResponse = await fetch(`${API_BASE_URL}/analytics/charts/progress-over-time?time_range=${timeRange}`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })
      if (progressResponse.ok) {
        const progressData = await progressResponse.json()
        setProgressChart(progressData)
      }

      // Fetch activity chart
      const activityResponse = await fetch(`${API_BASE_URL}/analytics/charts/daily-activity?time_range=LAST_7_DAYS`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })
      if (activityResponse.ok) {
        const activityData = await activityResponse.json()
        setActivityChart(activityData)
      }

      // Fetch tech stack chart
      const techResponse = await fetch(`${API_BASE_URL}/analytics/charts/tech-stack-popularity`, {
        headers: {
          'Authorization': user?.token ? `Bearer ${user.token}` : '',
          'Content-Type': 'application/json'
        }
      })
      if (techResponse.ok) {
        const techData = await techResponse.json()
        setTechStackChart(techData)
      }
    } catch (error) {
      console.error('Error fetching chart data:', error)
    }
  }

  useEffect(() => {
    fetchDashboardAnalytics()
    fetchChartData()
  }, [user, timeRange])

  const timeRangeOptions = [
    { value: 'LAST_7_DAYS', label: '7 Days' },
    { value: 'LAST_30_DAYS', label: '30 Days' },
    { value: 'LAST_90_DAYS', label: '90 Days' },
    { value: 'LAST_YEAR', label: '1 Year' }
  ]

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-white font-medium">
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-400">Insights into your project generation and usage patterns</p>
        </motion.div>

        {/* Overview Cards */}
        {dashboardData?.overview && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Projects</p>
                  <p className="text-3xl font-bold text-white">{dashboardData.overview.total_projects}</p>
                  <p className="text-green-400 text-sm mt-1">
                    {dashboardData.overview.success_rate}% success rate
                  </p>
                </div>
                <ChartBarIcon className="w-10 h-10 text-blue-400" />
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Completed</p>
                  <p className="text-3xl font-bold text-white">{dashboardData.overview.completed_projects}</p>
                  <p className="text-green-400 text-sm mt-1">
                    +{dashboardData.overview.in_progress_projects} in progress
                  </p>
                </div>
                <ArrowTrendingUpIcon className="w-10 h-10 text-green-400" />
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Active Users</p>
                  <p className="text-3xl font-bold text-white">{dashboardData.user_engagement?.active_users_month || 0}</p>
                  <p className="text-blue-400 text-sm mt-1">
                    {dashboardData.user_engagement?.active_users_today || 0} today
                  </p>
                </div>
                <UserGroupIcon className="w-10 h-10 text-purple-400" />
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Avg Generation Time</p>
                  <p className="text-3xl font-bold text-white">
                    {dashboardData.performance?.avg_generation_time || 0}s
                  </p>
                  <p className="text-yellow-400 text-sm mt-1">
                    {dashboardData.performance?.total_lines_generated || 0} lines total
                  </p>
                </div>
                <ClockIcon className="w-10 h-10 text-yellow-400" />
              </div>
            </div>
          </motion.div>
        )}

        {/* Time Range Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="flex flex-wrap gap-3">
            {timeRangeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setTimeRange(option.value)}
                className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                  timeRange === option.value
                    ? 'bg-blue-500/20 text-blue-400 border-blue-500/50'
                    : 'bg-gray-800/50 text-gray-400 border-gray-700/50 hover:bg-gray-700/50'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Progress Over Time Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <ArrowTrendingUpIcon className="w-6 h-6 mr-2 text-blue-400" />
              Projects Completed Over Time
            </h3>
            {progressChart ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={progressChart.data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="x" 
                    stroke="#9CA3AF"
                    fontSize={12}
                  />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    type="monotone" 
                    dataKey="y" 
                    stroke="#6366f1" 
                    strokeWidth={3}
                    dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#6366f1', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px]">
                <LoadingSpinner />
              </div>
            )}
          </motion.div>

          {/* Daily Activity Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <ChartBarIcon className="w-6 h-6 mr-2 text-green-400" />
              Daily Activity (Last 7 Days)
            </h3>
            {activityChart ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={activityChart.data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="x" 
                    stroke="#9CA3AF"
                    fontSize={12}
                  />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="y" 
                    fill="#22d3ee"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px]">
                <LoadingSpinner />
              </div>
            )}
          </motion.div>
        </div>

        {/* Tech Stack Popularity and Performance Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Tech Stack Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <CodeBracketIcon className="w-6 h-6 mr-2 text-purple-400" />
              Popular Tech Stacks
            </h3>
            {techStackChart && techStackChart.data.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={techStackChart.data}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ x, y, percent }) => `${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="y"
                  >
                    {techStackChart.data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color || techStackChart.colors[index % techStackChart.colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-gray-400">
                <div className="text-center">
                  <CodeBracketIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No tech stack data available</p>
                </div>
              </div>
            )}
          </motion.div>

          {/* Performance Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <CpuChipIcon className="w-6 h-6 mr-2 text-yellow-400" />
              Performance Metrics
            </h3>
            
            {dashboardData?.performance ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <ClockIcon className="w-6 h-6 text-blue-400" />
                    <div>
                      <p className="text-white font-medium">Average Generation Time</p>
                      <p className="text-gray-400 text-sm">Time to generate projects</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-blue-400">
                    {dashboardData.performance.avg_generation_time}s
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <ArrowTrendingUpIcon className="w-6 h-6 text-green-400" />
                    <div>
                      <p className="text-white font-medium">Success Rate</p>
                      <p className="text-gray-400 text-sm">Project completion rate</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-green-400">
                    {dashboardData.performance.success_rate}%
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CodeBracketIcon className="w-6 h-6 text-purple-400" />
                    <div>
                      <p className="text-white font-medium">Total Lines Generated</p>
                      <p className="text-gray-400 text-sm">Cumulative code output</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-purple-400">
                    {dashboardData.performance.total_lines_generated?.toLocaleString() || 0}
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <ArrowDownTrayIcon className="w-6 h-6 text-yellow-400" />
                    <div>
                      <p className="text-white font-medium">Average Project Size</p>
                      <p className="text-gray-400 text-sm">Lines per project</p>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-yellow-400">
                    {Math.round(dashboardData.performance.avg_project_size || 0)}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-[300px]">
                <LoadingSpinner />
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Analytics