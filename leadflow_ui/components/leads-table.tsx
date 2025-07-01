"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp, ExternalLink, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Business } from "@/app/page"

interface LeadsTableProps {
  businesses: Business[]
  selectedBusiness: Business | null
  onSelectBusiness: (business: Business) => void
}

type SortField = "name" | "website" | "email"
type SortDirection = "asc" | "desc"

export function LeadsTable({ businesses, selectedBusiness, onSelectBusiness }: LeadsTableProps) {
  const [sortField, setSortField] = useState<SortField>("name")
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc")

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const sortedBusinesses = [...businesses].sort((a, b) => {
    const aValue = a[sortField] || ""
    const bValue = b[sortField] || ""
    const comparison = aValue.localeCompare(bValue)
    return sortDirection === "asc" ? comparison : -comparison
  })

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
  }

  return (
    <Card className="bg-dark-card border-dark-border h-full flex flex-col">
      <CardHeader className="flex-shrink-0 pb-3">
        <CardTitle className="text-white flex items-center justify-between">
          <span>Leads ({businesses.length})</span>
          {businesses.length > 0 && (
            <Badge variant="secondary" className="bg-neon-green/20 text-neon-green border-neon-green/30">
              {businesses.length} found
            </Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        {businesses.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-400 p-6">
            <div className="text-center">
              <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No leads found yet</p>
              <p className="text-sm">Run a search to find potential leads</p>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex-shrink-0 bg-dark-card border-b border-dark-border px-4 py-3">
              <div className="grid grid-cols-12 gap-4 text-sm">
                <div className="col-span-3 text-gray-300 font-medium">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("name")}
                    className="h-auto p-0 font-medium text-gray-300 hover:text-white"
                  >
                    Name <SortIcon field="name" />
                  </Button>
                </div>
                <div className="col-span-3 text-gray-300 font-medium">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("website")}
                    className="h-auto p-0 font-medium text-gray-300 hover:text-white"
                  >
                    Website <SortIcon field="website" />
                  </Button>
                </div>
                <div className="col-span-3 text-gray-300 font-medium">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("email")}
                    className="h-auto p-0 font-medium text-gray-300 hover:text-white"
                  >
                    Email <SortIcon field="email" />
                  </Button>
                </div>
                <div className="col-span-3 text-gray-300 font-medium">Status</div>
              </div>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto">
              {sortedBusinesses.map((business, index) => (
                <div
                  key={index}
                  onClick={() => onSelectBusiness(business)}
                  className={`grid grid-cols-12 gap-4 p-4 cursor-pointer transition-colors hover:bg-dark-border/30 border-b border-dark-border/50 ${
                    selectedBusiness === business ? "bg-neon-blue/10 border-l-4 border-l-neon-blue" : ""
                  }`}
                >
                  <div className="col-span-3">
                    <div className="font-medium text-white text-sm">{business.name}</div>
                  </div>
                  <div className="col-span-3">
                    {business.website ? (
                      <a
                        href={business.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-neon-blue hover:text-neon-blue/80 flex items-center gap-1 text-sm"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span className="truncate">{business.website.replace(/^https?:\/\//, "")}</span>
                        <ExternalLink className="h-3 w-3 flex-shrink-0" />
                      </a>
                    ) : (
                      <span className="text-gray-500 text-sm">No website</span>
                    )}
                  </div>
                  <div className="col-span-3">
                    {business.email ? (
                      <span className="text-gray-300 text-sm truncate block">{business.email}</span>
                    ) : (
                      <span className="text-gray-500 text-sm">No email</span>
                    )}
                  </div>
                  <div className="col-span-3">
                    <div className="flex gap-1 flex-wrap">
                      {business.summary && (
                        <Badge
                          variant="secondary"
                          className="bg-neon-violet/20 text-neon-violet border-neon-violet/30 text-xs"
                        >
                          Summary
                        </Badge>
                      )}
                      {business.outreach_email && (
                        <Badge
                          variant="secondary"
                          className="bg-neon-green/20 text-neon-green border-neon-green/30 text-xs"
                        >
                          Email
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
