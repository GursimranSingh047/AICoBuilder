import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Sparkles, 
  Zap, 
  Code, 
  Rocket, 
  ArrowRight, 
  Play,
  ChevronDown,
  Star,
  Users,
  Clock
} from 'lucide-react'

const TypewriterText = ({ text, delay = 0 }) => {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentIndex < text.length) {
        setDisplayText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }
    }, delay + currentIndex * 50)

    return () => clearTimeout(timer)
  }, [currentIndex, text, delay])

  return (
    <span>
      {displayText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="text-accent"
      >
        |
      </motion.span>
    </span>
  )
}

const FeatureCard = ({ icon: Icon, title, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    className="group relative"
  >
    <div className="absolute inset-0 bg-gradient-to-r from-accent/20 to-cyan/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    <div className="relative bg-surface-1/80 backdrop-blur-sm border border-border/60 rounded-2xl p-6 hover:border-accent/40 transition-all duration-300 group-hover:transform group-hover:scale-105">
      <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
        <Icon size={24} className="text-accent" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-muted text-sm leading-relaxed">{description}</p>
    </div>
  </motion.div>
)

const StatCard = ({ number, label, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.6 }}
    className="text-center"
  >
    <div className="text-3xl font-bold text-white mb-1">{number}</div>
    <div className="text-sm text-muted">{label}</div>
  </motion.div>
)

export default function Landing() {
  const navigate = useNavigate()
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const features = [
    {
      icon: Sparkles,
      title: "AI-Powered Generation",
      description: "Transform your ideas into full-stack applications with advanced AI that understands modern development patterns."
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Generate complete projects in seconds, not hours. From concept to deployable code in under a minute."
    },
    {
      icon: Code,
      title: "Production Ready",
      description: "Clean, maintainable code following best practices. Includes proper folder structure, documentation, and deployment configs."
    },
    {
      icon: Rocket,
      title: "Modern Tech Stack",
      description: "Built with the latest technologies - React, FastAPI, PostgreSQL, Docker, and more. Always up-to-date."
    }
  ]

  return (
    <div className="min-h-screen bg-[#0c0c0f] relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 dot-grid opacity-40" />
      
      {/* Gradient orbs */}
      <motion.div
        className="absolute w-96 h-96 bg-accent/20 rounded-full blur-3xl"
        style={{
          left: mousePosition.x * 0.02,
          top: mousePosition.y * 0.02,
        }}
        animate={{
          x: [0, 100, 0],
          y: [0, -100, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      <motion.div
        className="absolute w-96 h-96 bg-cyan/20 rounded-full blur-3xl right-0 bottom-0"
        animate={{
          x: [0, -100, 0],
          y: [0, 100, 0],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 flex items-center justify-between px-8 py-6"
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="text-xl font-bold text-white">AI Co-Builder</span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/login')}
            className="text-muted hover:text-white transition-colors"
          >
            Sign In
          </button>
          <button 
            onClick={() => navigate('/signup')}
            className="btn-primary"
          >
            Get Started
          </button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 pt-20 pb-32">
        <div className="text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-6"
          >
            <h1 className="text-6xl md:text-7xl font-bold text-white leading-tight">
              Welcome to{' '}
              <span className="bg-gradient-to-r from-accent to-cyan bg-clip-text text-transparent">
                AI Co-Builder
              </span>
            </h1>
            
            <div className="text-xl md:text-2xl text-muted max-w-3xl mx-auto">
              <TypewriterText 
                text="Build Projects with AI – Faster, Smarter, Better" 
                delay={1000}
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 3, duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <motion.button
              onClick={() => navigate('/generator')}
              className="group relative px-8 py-4 bg-accent hover:bg-accent-hover text-white font-semibold rounded-xl transition-all duration-300 flex items-center gap-3"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-accent to-cyan rounded-xl blur opacity-75 group-hover:opacity-100 transition-opacity" />
              <div className="relative flex items-center gap-3">
                <Sparkles size={20} />
                Get Started Free
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </motion.button>
            
            <motion.button
              className="group flex items-center gap-3 px-6 py-4 text-muted hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-12 h-12 bg-surface-1 border border-border rounded-full flex items-center justify-center group-hover:border-accent/40 transition-colors">
                <Play size={16} className="ml-0.5" />
              </div>
              Watch Demo
            </motion.button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 3.5, duration: 0.6 }}
            className="grid grid-cols-3 gap-8 max-w-md mx-auto pt-16"
          >
            <StatCard number="10K+" label="Projects Generated" delay={3.7} />
            <StatCard number="50+" label="Tech Stacks" delay={3.9} />
            <StatCard number="<60s" label="Average Build Time" delay={4.1} />
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 4.5, duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold text-white mb-4">
            Why Choose AI Co-Builder?
          </h2>
          <p className="text-xl text-muted max-w-2xl mx-auto">
            Experience the future of development with our AI-powered platform
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <FeatureCard
              key={feature.title}
              {...feature}
              delay={5 + index * 0.2}
            />
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 6, duration: 0.8 }}
        className="relative z-10 max-w-4xl mx-auto px-8 pb-32 text-center"
      >
        <div className="bg-gradient-to-r from-accent/10 to-cyan/10 border border-accent/20 rounded-3xl p-12">
          <h3 className="text-3xl font-bold text-white mb-4">
            Ready to Build Something Amazing?
          </h3>
          <p className="text-lg text-muted mb-8 max-w-2xl mx-auto">
            Join thousands of developers who are already building faster with AI. 
            Start your first project today – it's completely free.
          </p>
          <motion.button
            onClick={() => navigate('/generator')}
            className="btn-primary text-lg px-8 py-4"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles size={20} />
            Start Building Now
            <ArrowRight size={18} />
          </motion.button>
        </div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 7, duration: 0.6 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-muted"
        >
          <ChevronDown size={24} />
        </motion.div>
      </motion.div>
    </div>
  )
}