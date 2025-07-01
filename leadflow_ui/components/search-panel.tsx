"use client"

import type React from "react"

import { useState } from "react"
import { Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface SearchPanelProps {
  onRunPipeline: (query: string, maxLinks: number) => void
  isLoading: boolean
}

export function SearchPanel({ onRunPipeline, isLoading }: SearchPanelProps) {
  const [query, setQuery] = useState("technology companies in South Loop Chicago")
  const [maxLinks, setMaxLinks] = useState(10)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onRunPipeline(query, maxLinks)
  }

  return (
    <Card className="bg-dark-card border-dark-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Search className="h-5 w-5 text-neon-blue" />
          Lead Search Configuration
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="query" className="text-gray-300">
                Business Type & Location
              </Label>
              <Input
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., restaurants in downtown Chicago"
                className="bg-dark-bg border-dark-border text-white placeholder:text-gray-500 focus:border-neon-blue focus:ring-neon-blue/20"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxLinks" className="text-gray-300">
                Max Businesses
              </Label>
              <Input
                id="maxLinks"
                type="number"
                min="1"
                max="25"
                value={maxLinks}
                onChange={(e) => setMaxLinks(Number.parseInt(e.target.value) || 10)}
                className="bg-dark-bg border-dark-border text-white focus:border-neon-blue focus:ring-neon-blue/20"
                disabled={isLoading}
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="w-full md:w-auto bg-gradient-to-r from-neon-blue to-neon-violet hover:from-neon-blue/80 hover:to-neon-violet/80 text-white font-medium"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Pipeline...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Run LeadFlow Pipeline
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
