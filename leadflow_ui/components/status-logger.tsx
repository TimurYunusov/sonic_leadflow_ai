"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Activity, CheckCircle, AlertCircle, XCircle, Info } from "lucide-react"
import type { LogEntry } from "@/app/page"

interface StatusLoggerProps {
  logs: LogEntry[]
}

export function StatusLogger({ logs }: StatusLoggerProps) {
  const getLogIcon = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-neon-green" />
      case "error":
        return <XCircle className="h-4 w-4 text-red-400" />
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-400" />
      default:
        return <Info className="h-4 w-4 text-neon-blue" />
    }
  }

  const getLogBadgeColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return "bg-neon-green/20 text-neon-green border-neon-green/30"
      case "error":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      case "warning":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      default:
        return "bg-neon-blue/20 text-neon-blue border-neon-blue/30"
    }
  }

  return (
    <Card className="bg-dark-card border-dark-border h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Activity className="h-5 w-5 text-neon-blue" />
          Pipeline Status
          {logs.length > 0 && (
            <Badge variant="secondary" className="bg-gray-700 text-gray-300">
              {logs.length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-6 pb-6">
          {logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No activity yet</p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="flex items-start gap-3 p-3 rounded-lg bg-dark-bg/50 border border-dark-border/50"
                >
                  <div className="flex-shrink-0 mt-0.5">{getLogIcon(log.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="secondary" className={`text-xs ${getLogBadgeColor(log.type)}`}>
                        {log.type}
                      </Badge>
                      <span className="text-xs text-gray-400">{log.timestamp.toLocaleTimeString()}</span>
                    </div>
                    <p className="text-sm text-gray-300 leading-relaxed">{log.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
