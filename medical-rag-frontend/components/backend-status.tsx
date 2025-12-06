"use client"

import { useEffect, useState } from "react"
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react"
import { API_BASE_URL } from "@/lib/api"

export function BackendStatus({ isCollapsed = false }: { isCollapsed?: boolean }) {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking")

  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(3000),
      })
      setStatus(response.ok ? "online" : "offline")
    } catch {
      setStatus("offline")
    }
  }

  if (isCollapsed) {
    if (status === "checking") {
      return (
        <div className="flex items-center justify-center p-2">
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        </div>
      )
    }

    if (status === "offline") {
      return (
        <div className="flex items-center justify-center p-2" title="Backend offline">
          <AlertCircle className="h-4 w-4 text-red-500" />
        </div>
      )
    }

    return (
      <div className="flex items-center justify-center p-2" title="Connected">
        <CheckCircle className="h-4 w-4 text-green-500" />
      </div>
    )
  }

  if (status === "checking") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted/50 text-sm">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Checking backend...</span>
      </div>
    )
  }

  if (status === "offline") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-50 text-red-700 text-sm">
        <AlertCircle className="h-4 w-4" />
        <span>Backend offline</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-50 text-green-700 text-sm">
      <CheckCircle className="h-4 w-4" />
      <span>Connected</span>
    </div>
  )
}
