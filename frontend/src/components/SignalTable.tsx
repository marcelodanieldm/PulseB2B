"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import {
  ArrowUpDown,
  TrendingUp,
  TrendingDown,
  Zap,
  Lock,
  ExternalLink,
  Filter,
  Search
} from "lucide-react"
import { cn } from "@/lib/cn"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CompanyProfileModal } from "./CompanyProfileModal"

export interface Company {
  id: string
  company_name: string
  pulse_score: number
  desperation_level: "CRITICAL" | "HIGH" | "MODERATE" | "LOW"
  urgency: string
  hiring_probability: number
  expansion_density: number
  tech_stack: string[]
  funding_amount: number
  funding_date: string
  last_seen: string
  has_red_flags: boolean
  website_url?: string
  recommendation: string
}

interface SignalTableProps {
  data: Company[]
  isPremium: boolean
  onUpgrade: () => void
}

export function SignalTable({ data, isPremium, onUpgrade }: SignalTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([
    { id: "pulse_score", desc: true }
  ])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = React.useState("")
  const [selectedCompany, setSelectedCompany] = React.useState<Company | null>(null)

  const getDesperationColor = (level: string) => {
    switch (level) {
      case "CRITICAL": return "text-red-500 bg-red-500/10"
      case "HIGH": return "text-amber-500 bg-amber-500/10"
      case "MODERATE": return "text-blue-500 bg-blue-500/10"
      default: return "text-gray-500 bg-gray-500/10"
    }
  }

  const columns: ColumnDef<Company>[] = [
    {
      accessorKey: "pulse_score",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-transparent px-0"
        >
          Signal Strength
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const score = row.getValue("pulse_score") as number
        const level = row.original.desperation_level
        
        return (
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">{score.toFixed(0)}</span>
                <span className="text-xs text-muted-foreground">/100</span>
              </div>
              <Badge className={cn("text-xs mt-1", getDesperationColor(level))}>
                {level === "CRITICAL" && <Zap className="w-3 h-3 mr-1" />}
                {level}
              </Badge>
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: "company_name",
      header: "Company",
      cell: ({ row }) => {
        const company = row.original
        const isLocked = !isPremium && company.pulse_score >= 70
        
        return (
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-base">{company.company_name}</span>
                {company.has_red_flags && (
                  <Badge variant="destructive" className="text-xs">
                    Red Flag
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted-foreground">
                  Last seen: {new Date(company.last_seen).toLocaleDateString()}
                </span>
                {isLocked && (
                  <Lock className="w-3 h-3 text-muted-foreground" />
                )}
              </div>
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: "hiring_probability",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="hover:bg-transparent px-0"
        >
          Hiring Probability
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const probability = row.getValue("hiring_probability") as number
        const isHigh = probability >= 75
        
        return (
          <div className="flex items-center gap-2">
            {isHigh ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-gray-500" />
            )}
            <span className={cn(
              "font-medium",
              isHigh ? "text-green-500" : "text-gray-400"
            )}>
              {probability.toFixed(0)}%
            </span>
          </div>
        )
      },
    },
    {
      accessorKey: "expansion_density",
      header: "Expansion",
      cell: ({ row }) => {
        const density = row.getValue("expansion_density") as number
        
        return (
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-800 rounded-full h-2 max-w-[100px]">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(density, 100)}%` }}
              />
            </div>
            <span className="text-sm text-muted-foreground">
              {density.toFixed(0)}%
            </span>
          </div>
        )
      },
    },
    {
      accessorKey: "tech_stack",
      header: "Tech Stack",
      cell: ({ row }) => {
        const techStack = row.getValue("tech_stack") as string[]
        const displayStack = techStack?.slice(0, 3) || []
        const remaining = (techStack?.length || 0) - 3
        
        return (
          <div className="flex items-center gap-1 flex-wrap">
            {displayStack.map((tech, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {tech}
              </Badge>
            ))}
            {remaining > 0 && (
              <Badge variant="outline" className="text-xs">
                +{remaining}
              </Badge>
            )}
          </div>
        )
      },
    },
    {
      accessorKey: "funding_amount",
      header: "Funding",
      cell: ({ row }) => {
        const amount = row.getValue("funding_amount") as number
        const date = row.original.funding_date
        
        return (
          <div className="flex flex-col">
            <span className="font-semibold">
              {amount > 0 ? `$${(amount / 1000000).toFixed(1)}M` : "N/A"}
            </span>
            {date && (
              <span className="text-xs text-muted-foreground">
                {new Date(date).toLocaleDateString()}
              </span>
            )}
          </div>
        )
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const company = row.original
        const isLocked = !isPremium && company.pulse_score >= 70
        
        return (
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (isLocked) {
                  onUpgrade()
                } else {
                  setSelectedCompany(company)
                }
              }}
              className="hover:bg-accent"
            >
              {isLocked ? (
                <>
                  <Lock className="w-4 h-4 mr-1" />
                  Unlock
                </>
              ) : (
                <>
                  View Details
                  <ExternalLink className="w-4 h-4 ml-1" />
                </>
              )}
            </Button>
          </div>
        )
      },
    },
  ]

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  })

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search companies..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        
        <Button variant="outline" size="sm">
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-gray-800 bg-gray-950">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b border-gray-800">
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-6 py-4 text-left text-sm font-medium text-muted-foreground"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-gray-800 hover:bg-gray-900/50 transition-colors cursor-pointer"
                    onClick={() => {
                      const isLocked = !isPremium && row.original.pulse_score >= 70
                      if (isLocked) {
                        onUpgrade()
                      } else {
                        setSelectedCompany(row.original)
                      }
                    }}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-6 py-4">
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="h-24 text-center text-muted-foreground"
                  >
                    No companies found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-800">
          <div className="text-sm text-muted-foreground">
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{" "}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              table.getFilteredRowModel().rows.length
            )}{" "}
            of {table.getFilteredRowModel().rows.length} companies
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      {/* Company Profile Modal */}
      {selectedCompany && (
        <CompanyProfileModal
          company={selectedCompany}
          isPremium={isPremium}
          open={!!selectedCompany}
          onClose={() => setSelectedCompany(null)}
          onUpgrade={onUpgrade}
        />
      )}
    </div>
  )
}
