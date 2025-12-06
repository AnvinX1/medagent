"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { MessageSquare, Activity, Calendar, BarChart3, Crown, ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { BackendStatus } from "./backend-status"
import { useState, useEffect } from "react"

const navItems = [
  {
    title: "Chat",
    href: "/",
    icon: MessageSquare,
  },
  {
    title: "Health Tracker",
    href: "/health-tracker",
    icon: Activity,
  },
  {
    title: "Appointments",
    href: "/appointments",
    icon: Calendar,
  },
  {
    title: "Usage Stats",
    href: "/usage-stats",
    icon: BarChart3,
  },
  {
    title: "Pro Version",
    href: "/pro",
    icon: Crown,
  },
]

type SidebarNavProps = {
  onCollapseChange?: (collapsed: boolean) => void
}

export function SidebarNav({ onCollapseChange }: SidebarNavProps) {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("sidebar-collapsed")
      return saved === "true"
    }
    return false
  })

  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", String(isCollapsed))
    onCollapseChange?.(isCollapsed)
  }, [isCollapsed, onCollapseChange])

  const handleToggle = () => {
    setIsCollapsed(!isCollapsed)
  }

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen glass-effect border-r border-border p-6 flex flex-col gap-2 transition-all duration-300 ease-in-out z-40",
        isCollapsed ? "w-20" : "w-64",
      )}
    >
      {/* Toggle button */}
      <button
        onClick={handleToggle}
        className="absolute -right-3 top-8 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-lg hover:scale-110 transition-transform z-10"
        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>

      <div className="mb-8">
        <h1
          className={cn(
            "text-2xl font-bold text-primary flex items-center gap-2 transition-all",
            isCollapsed && "justify-center",
          )}
        >
          <Activity className="h-6 w-6 flex-shrink-0" />
          {!isCollapsed && "Hygeia AI"}
        </h1>
        {!isCollapsed && <p className="text-sm text-muted-foreground mt-1">Your Health Companion</p>}
      </div>

      <nav className="flex flex-col gap-2 flex-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                isActive ? "bg-primary text-primary-foreground shadow-md" : "hover:bg-secondary text-foreground",
                isCollapsed && "justify-center",
              )}
              title={isCollapsed ? item.title : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!isCollapsed && <span className="font-medium">{item.title}</span>}
            </Link>
          )
        })}
      </nav>

      <div
        className={cn(
          "mt-auto pt-4 border-t border-border transition-all",
          isCollapsed && "flex flex-col items-center",
        )}
      >
        <BackendStatus isCollapsed={isCollapsed} />
        {!isCollapsed && (
          <p className="text-xs text-muted-foreground mt-2">
            Backend: <code className="text-xs">localhost:8000</code>
          </p>
        )}
      </div>
    </aside>
  )
}
