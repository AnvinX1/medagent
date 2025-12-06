"use client"

import { useState, useEffect } from "react"
import { SidebarNav } from "@/components/sidebar-nav"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, MessageSquare, Users } from "lucide-react"
import { fetchAPI } from "@/lib/api"

type UsageStats = {
  total_messages?: number
  unique_sessions?: number
  total_queries?: number
  active_users?: number
}

export default function UsageStatsPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [stats, setStats] = useState<UsageStats>({})
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const data = await fetchAPI("/usage-stats")
      setStats(data)
    } catch (error) {
      console.error("[v0] Failed to fetch usage stats:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav onCollapseChange={setIsSidebarCollapsed} />

      <main className={`flex-1 p-6 transition-all duration-300 ${isSidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <div className="mb-6">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-primary" />
            Usage Statistics
          </h1>
          <p className="text-muted-foreground mt-1">Track your interaction with Hygeia AI</p>
        </div>

        {isLoading ? (
          <p className="text-center text-muted-foreground py-8">Loading statistics...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="shadow-lg border-l-4 border-l-primary">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  Total Messages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-primary">{stats.total_messages || stats.total_queries || 0}</p>
                <p className="text-sm text-muted-foreground mt-2">Messages exchanged with AI</p>
              </CardContent>
            </Card>

            <Card className="shadow-lg border-l-4 border-l-blue-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="h-5 w-5 text-blue-500" />
                  Unique Sessions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-blue-500">{stats.unique_sessions || stats.active_users || 0}</p>
                <p className="text-sm text-muted-foreground mt-2">Conversation sessions started</p>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  )
}
