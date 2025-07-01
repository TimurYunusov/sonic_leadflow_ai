"use client"

import { Mail, Building, ExternalLink, Copy, Check } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import type { Business } from "@/app/page"

interface PreviewPanelProps {
  selectedBusiness: Business | null
}

export function PreviewPanel({ selectedBusiness }: PreviewPanelProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null)

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedField(field)
      setTimeout(() => setCopiedField(null), 2000)
    } catch (err) {
      console.error("Failed to copy text: ", err)
    }
  }

  if (!selectedBusiness) {
    return (
      <Card className="bg-dark-card border-dark-border h-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center text-gray-400">
            <Building className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Select a lead to view details</p>
            <p className="text-sm">Click on any row in the table</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-dark-card border-dark-border h-full flex flex-col">
      <CardHeader className="flex-shrink-0 pb-3">
        <CardTitle className="text-white flex items-center gap-2">
          <Building className="h-5 w-5 text-neon-blue" />
          Lead Details
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white break-words">{selectedBusiness.name}</h3>

            <div className="space-y-3">
              {selectedBusiness.website && (
                <div className="flex items-start justify-between gap-2">
                  <a
                    href={selectedBusiness.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neon-blue hover:text-neon-blue/80 flex items-center gap-1 break-all text-sm"
                  >
                    <span>{selectedBusiness.website}</span>
                    <ExternalLink className="h-3 w-3 flex-shrink-0" />
                  </a>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(selectedBusiness.website, "website")}
                    className="h-6 w-6 p-0 flex-shrink-0"
                  >
                    {copiedField === "website" ? (
                      <Check className="h-3 w-3 text-neon-green" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              )}

              {selectedBusiness.email && (
                <div className="flex items-start justify-between gap-2">
                  <span className="text-gray-300 text-sm break-all">{selectedBusiness.email}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(selectedBusiness.email, "email")}
                    className="h-6 w-6 p-0 flex-shrink-0"
                  >
                    {copiedField === "email" ? (
                      <Check className="h-3 w-3 text-neon-green" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>

          <Separator className="bg-dark-border" />

          {/* Summary */}
          {selectedBusiness.summary && (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="secondary" className="bg-neon-violet/20 text-neon-violet border-neon-violet/30">
                  Summary
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(selectedBusiness.summary, "summary")}
                  className="h-6 w-6 p-0 flex-shrink-0"
                >
                  {copiedField === "summary" ? (
                    <Check className="h-3 w-3 text-neon-green" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap break-words">
                {selectedBusiness.summary}
              </p>
            </div>
          )}

          {/* Pain Points */}
          {selectedBusiness.pain_points && (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="secondary" className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                  Pain Points
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(selectedBusiness.pain_points, "pain_points")}
                  className="h-6 w-6 p-0 flex-shrink-0"
                >
                  {copiedField === "pain_points" ? (
                    <Check className="h-3 w-3 text-neon-green" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap break-words">
                {selectedBusiness.pain_points}
              </p>
            </div>
          )}

          <Separator className="bg-dark-border" />

          {/* Outreach Email */}
          {selectedBusiness.outreach_email && (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-neon-green" />
                  <span className="font-medium text-white">Outreach Email</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(selectedBusiness.outreach_email, "outreach_email")}
                  className="h-6 w-6 p-0 flex-shrink-0"
                >
                  {copiedField === "outreach_email" ? (
                    <Check className="h-3 w-3 text-neon-green" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </div>
              <div className="bg-dark-bg rounded-lg p-4 border border-dark-border">
                <pre className="text-gray-300 text-sm whitespace-pre-wrap break-words font-mono leading-relaxed">
                  {selectedBusiness.outreach_email}
                </pre>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
