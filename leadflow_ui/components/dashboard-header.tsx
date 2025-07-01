"use client"

import { Bell, Settings, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { SidebarTrigger } from "@/components/ui/sidebar"

export function DashboardHeader() {
  return (
    <header className="border-b border-dark-border bg-dark-card/50 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-blue to-neon-violet flex items-center justify-center">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <h1 className="text-xl font-semibold bg-gradient-to-r from-neon-blue to-neon-violet bg-clip-text text-transparent">
              Sonic LeadFlow AI
            </h1>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6">
          <Button variant="ghost" className="text-gray-300 hover:text-white">
            Dashboard
          </Button>
          <Button variant="ghost" className="text-gray-300 hover:text-white">
            Leads
          </Button>
          <Button variant="ghost" className="text-gray-300 hover:text-white">
            Campaigns
          </Button>
          <Button variant="ghost" className="text-gray-300 hover:text-white">
            Settings
          </Button>
        </nav>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="text-gray-300 hover:text-white">
            <Bell className="h-5 w-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-gradient-to-br from-neon-blue to-neon-violet text-white font-semibold">
                    JD
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-dark-card border-dark-border" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none text-white">John Doe</p>
                  <p className="text-xs leading-none text-gray-400">john@example.com</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-dark-border" />
              <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-dark-border">
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-dark-border">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-dark-border" />
              <DropdownMenuItem className="text-gray-300 hover:text-white hover:bg-dark-border">
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
