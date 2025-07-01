"use client"

import { BarChart3, Mail, Play, Settings, Zap } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const menuItems = [
  {
    title: "Dashboard",
    icon: BarChart3,
    url: "#",
    isActive: true,
  },
  {
    title: "Run Search",
    icon: Play,
    url: "#",
  },
  {
    title: "Email Generator",
    icon: Mail,
    url: "#",
  },
  {
    title: "Analytics",
    icon: Zap,
    url: "#",
  },
  {
    title: "Settings",
    icon: Settings,
    url: "#",
  },
]

export function DashboardSidebar() {
  return (
    <Sidebar className="border-r border-dark-border bg-dark-card/50 backdrop-blur-sm">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={item.isActive}
                    className="data-[active=true]:bg-gradient-to-r data-[active=true]:from-neon-blue/20 data-[active=true]:to-neon-violet/20 data-[active=true]:border-r-2 data-[active=true]:border-neon-blue hover:bg-dark-border/50"
                  >
                    <a href={item.url} className="flex items-center gap-3">
                      <item.icon className="h-5 w-5" />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
