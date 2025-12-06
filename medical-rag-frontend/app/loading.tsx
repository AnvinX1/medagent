"use client"

import { Activity, Loader2 } from "lucide-react"

export default function Loading() {
  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center z-50">
      <div className="text-center space-y-6">
        {/* Logo and branding */}
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="relative">
            <Activity className="h-16 w-16 text-primary animate-pulse" />
            <div className="absolute inset-0 h-16 w-16 text-primary/20 animate-ping">
              <Activity className="h-16 w-16" />
            </div>
          </div>
        </div>

        {/* Title */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-primary">Hygeia AI</h1>
          <p className="text-muted-foreground text-sm">Your Health Companion</p>
        </div>

        {/* Loading indicator */}
        <div className="flex items-center justify-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Loading your health dashboard...</span>
        </div>

        {/* Progress bar */}
        <div className="w-64 h-1 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-primary rounded-full animate-[loading_1.5s_ease-in-out_infinite]" />
        </div>
      </div>

      <style jsx>{`
        @keyframes loading {
          0% {
            width: 0%;
            margin-left: 0%;
          }
          50% {
            width: 50%;
            margin-left: 25%;
          }
          100% {
            width: 0%;
            margin-left: 100%;
          }
        }
      `}</style>
    </div>
  )
}
