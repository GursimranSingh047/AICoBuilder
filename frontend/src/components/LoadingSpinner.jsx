import React from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Zap, Code, Rocket } from 'lucide-react'

const LoadingSpinner = ({ message = "Loading...", type = "default" }) => {
  const icons = [Sparkles, Zap, Code, Rocket]
  
  if (type === "project-generation") {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-6">
        <div className="relative">
          {/* Outer ring */}
          <motion.div
            className="w-20 h-20 border-4 border-accent/20 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Inner ring */}
          <motion.div
            className="absolute inset-2 w-16 h-16 border-4 border-cyan/30 rounded-full border-t-cyan"
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Center icon */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          >
            <Sparkles size={24} className="text-accent" />
          </motion.div>
        </div>
        
        <div className="text-center space-y-2">
          <motion.h3
            className="text-lg font-semibold text-white"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {message}
          </motion.h3>
          <p className="text-sm text-muted">This may take a few moments...</p>
        </div>
        
        {/* Floating icons */}
        <div className="relative w-32 h-8">
          {icons.map((Icon, index) => (
            <motion.div
              key={index}
              className="absolute"
              style={{ left: `${index * 25}%` }}
              animate={{
                y: [0, -10, 0],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: index * 0.3
              }}
            >
              <Icon size={16} className="text-muted" />
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center p-4">
      <motion.div
        className="w-8 h-8 border-2 border-accent/20 border-t-accent rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      {message && (
        <span className="ml-3 text-sm text-muted">{message}</span>
      )}
    </div>
  )
}

export default LoadingSpinner