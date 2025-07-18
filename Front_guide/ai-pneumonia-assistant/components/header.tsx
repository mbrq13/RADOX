"use client"

import { Users, Upload, Settings, Stethoscope, LogOut, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/lib/auth-context"

type TabType = "patients" | "upload" | "settings"

interface HeaderProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  const { user, logout } = useAuth()

  const tabs = [
    { id: "patients" as TabType, label: "Pacientes", icon: Users },
    { id: "upload" as TabType, label: "Subir", icon: Upload, disabled: user?.role === "viewer" },
    { id: "settings" as TabType, label: "Configuración", icon: Settings },
  ]

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "administrador":
        return "destructive"
      case "médico":
        return "default"
      case "radiólogo":
        return "secondary"
      case "viewer":
        return "outline"
      default:
        return "secondary"
    }
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "administrador":
        return "Admin"
      case "médico":
        return "Médico"
      case "radiólogo":
        return "Radiólogo"
      case "viewer":
        return "Visualizador"
      default:
        return role
    }
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Stethoscope className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">RADOX Assistant</h1>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <nav className="flex gap-1">
              {tabs.map((tab) => (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? "default" : "ghost"}
                  onClick={() => onTabChange(tab.id)}
                  className="flex items-center gap-2"
                  disabled={tab.disabled}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </Button>
              ))}
            </nav>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="flex items-center gap-2 bg-transparent">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">{user?.name}</span>
                  <Badge variant={getRoleBadgeVariant(user?.role || "")} className="text-xs">
                    {getRoleLabel(user?.role || "")}
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Mi Cuenta</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled>
                  <User className="mr-2 h-4 w-4" />
                  <div>
                    <div className="font-medium">{user?.name}</div>
                    <div className="text-xs text-gray-500">@{user?.username}</div>
                  </div>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Badge variant="secondary" className="ml-2">
              MedGemma AI
            </Badge>
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden flex items-center gap-2">
            <select
              value={activeTab}
              onChange={(e) => onTabChange(e.target.value as TabType)}
              className="border rounded-md px-3 py-1 text-sm"
            >
              {tabs.map((tab) => (
                <option key={tab.id} value={tab.id} disabled={tab.disabled}>
                  {tab.label}
                </option>
              ))}
            </select>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
