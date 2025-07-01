"use client"

import { useState } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { SearchPanel } from "@/components/search-panel"
import { LeadsTable } from "@/components/leads-table"
import { PreviewPanel } from "@/components/preview-panel"
import { StatusLogger } from "@/components/status-logger"
import { SidebarProvider } from "@/components/ui/sidebar"

export interface Business {
  name: string
  website: string
  email: string
  summary: string
  pain_points: string
  outreach_email: string
  url: string
}

export interface LogEntry {
  id: string
  message: string
  type: "info" | "success" | "error" | "warning"
  timestamp: Date
}

// Counter for unique IDs
let logCounter = 0

export default function Dashboard() {
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])

  const addLog = (message: string, type: LogEntry["type"] = "info") => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}-${++logCounter}`,
      message,
      type,
      timestamp: new Date(),
    }
    setLogs((prev) => [newLog, ...prev].slice(0, 50))
  }

  const runPipeline = async (query: string, maxLinks: number) => {
    setIsLoading(true)
    setBusinesses([])
    setSelectedBusiness(null)

    try {
      addLog(`Starting pipeline for: "${query}"`, "info")
      addLog("Connecting to API...", "info")

      const response = await fetch("http://127.0.0.1:8000/run-leadflow-pipeline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        mode: "cors",
        body: JSON.stringify({
          search_query: query,
          max_links: maxLinks,
        }),
      })

      addLog(`API Response Status: ${response.status}`, response.ok ? "success" : "error")

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      addLog("Parsing response data...", "info")
      const data = await response.json()
      const businessData = data.businesses || []

      addLog(`Found ${businessData.length} businesses`, "success")

      if (businessData.length > 0) {
        addLog("Processing business summaries...", "info")
        addLog("Generating outreach emails...", "info")
        addLog("Pipeline completed successfully!", "success")
      } else {
        addLog("No businesses found for this query", "warning")
      }

      setBusinesses(businessData)
    } catch (error) {
      console.error("Pipeline error:", error)
      const errorMessage = error instanceof Error ? error.message : "Unknown error occurred"
      addLog(`Error: ${errorMessage}`, "error")

      if (error instanceof TypeError && error.message.includes("fetch")) {
        addLog("Network error - check if API server is running on port 8000", "error")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <SidebarProvider>
        <div className="flex h-screen">
          <DashboardSidebar />

          <div className="flex-1 flex flex-col overflow-hidden">
            <DashboardHeader />

            <main className="flex-1 overflow-auto p-4 lg:p-6">
              <div className="space-y-6 max-w-full">
                <SearchPanel onRunPipeline={runPipeline} isLoading={isLoading} />

                <div className="flex flex-col xl:flex-row gap-6 min-h-0">
                  {/* Left Column - Leads Table */}
                  <div className="flex-1 min-w-0">
                    <LeadsTable
                      businesses={businesses}
                      selectedBusiness={selectedBusiness}
                      onSelectBusiness={setSelectedBusiness}
                    />
                  </div>

                  {/* Right Column - Preview and Status */}
                  <div className="w-full xl:w-96 flex flex-col gap-6 min-h-0">
                    <div className="flex-1 min-h-0">
                      <PreviewPanel selectedBusiness={selectedBusiness} />
                    </div>
                    <div className="h-64 flex-shrink-0">
                      <StatusLogger logs={logs} />
                    </div>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
}
