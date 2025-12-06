"use client"

import { useState, useEffect } from "react"
import { SidebarNav } from "@/components/sidebar-nav"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Activity, TrendingUp } from "lucide-react"
import { fetchAPI } from "@/lib/api"

type HealthMetric = {
  id?: string
  type: string
  value: number
  unit: string
  recorded_at?: string
  timestamp?: string
}

const metricTypes = ["Heart Rate", "Blood Pressure", "Weight", "Temperature", "Blood Sugar", "Oxygen Level"]

export default function HealthTrackerPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [metrics, setMetrics] = useState<HealthMetric[]>([])
  const [selectedType, setSelectedType] = useState("Heart Rate")
  const [newMetric, setNewMetric] = useState({
    type: "Heart Rate",
    value: "",
    unit: "bpm",
  })

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const data = await fetchAPI("/health-metrics")
      setMetrics(data.metrics || data || [])
    } catch (error) {
      console.error("[v0] Failed to fetch health metrics:", error)
    }
  }

  const handleSave = async () => {
    if (!newMetric.value) return

    try {
      await fetchAPI("/health-metrics", {
        method: "POST",
        body: JSON.stringify({
          type: newMetric.type,
          value: Number.parseFloat(newMetric.value),
          unit: newMetric.unit,
        }),
      })

      setNewMetric({ ...newMetric, value: "" })
      fetchMetrics()
    } catch (error) {
      console.error("[v0] Failed to save metric:", error)
    }
  }

  const filteredMetrics = metrics.filter((m) => m.type === selectedType)
  const chartData = filteredMetrics.map((m, idx) => ({
    name: `Entry ${idx + 1}`,
    value: m.value,
    date: m.recorded_at || m.timestamp || new Date().toISOString(),
  }))

  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav onCollapseChange={setIsSidebarCollapsed} />

      <main className={`flex-1 p-6 transition-all duration-300 ${isSidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <div className="mb-6">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="h-8 w-8 text-primary" />
            Health Tracker
          </h1>
          <p className="text-muted-foreground mt-1">Monitor and track your vital health metrics</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Add New Metric</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="type">Metric Type</Label>
                <Select value={newMetric.type} onValueChange={(value) => setNewMetric({ ...newMetric, type: value })}>
                  <SelectTrigger id="type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {metricTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="value">Value</Label>
                <Input
                  id="value"
                  type="number"
                  value={newMetric.value}
                  onChange={(e) => setNewMetric({ ...newMetric, value: e.target.value })}
                  placeholder="Enter value"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="unit">Unit</Label>
                <Input
                  id="unit"
                  value={newMetric.unit}
                  onChange={(e) => setNewMetric({ ...newMetric, unit: e.target.value })}
                  placeholder="e.g., bpm, kg, °C"
                />
              </div>

              <Button onClick={handleSave} className="w-full">
                Save Entry
              </Button>
            </CardContent>
          </Card>

          {/* Dashboard */}
          <div className="space-y-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Metrics Overview
                </CardTitle>
                <div className="mt-2">
                  <Label>Select Metric to View</Label>
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {metricTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="value" stroke="hsl(var(--primary))" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No data available for {selectedType}</p>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Recent Entries</CardTitle>
              </CardHeader>
              <CardContent>
                {filteredMetrics.length > 0 ? (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {filteredMetrics
                      .slice(-10)
                      .reverse()
                      .map((metric, idx) => (
                        <div key={idx} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                          <span className="font-medium">{metric.type}</span>
                          <span className="text-primary font-semibold">
                            {metric.value} {metric.unit}
                          </span>
                        </div>
                      ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-4">No entries yet</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
