"use client"

import { useState } from "react"
import { Moon, Sun, Globe, Bell, Eye } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(false)
  const [defaultHeatmap, setDefaultHeatmap] = useState(true)
  const [language, setLanguage] = useState("english")
  const [demoNotifications, setDemoNotifications] = useState(true)

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Settings</h2>
        <p className="text-gray-600">Customize your AI Pneumonia Assistant experience.</p>
      </div>

      <div className="grid gap-6">
        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-5 w-5" />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Dark Mode</Label>
                <p className="text-sm text-gray-500">Switch between light and dark themes</p>
              </div>
              <div className="flex items-center gap-2">
                <Sun className="h-4 w-4" />
                <Switch checked={darkMode} onCheckedChange={setDarkMode} />
                <Moon className="h-4 w-4" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Analysis Display
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Default Heatmap Overlay</Label>
                <p className="text-sm text-gray-500">Show AI attention heatmap by default on X-ray images</p>
              </div>
              <Switch checked={defaultHeatmap} onCheckedChange={setDefaultHeatmap} />
            </div>
          </CardContent>
        </Card>

        {/* Language Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Language & Region
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Interface Language</Label>
                <p className="text-sm text-gray-500">Choose your preferred language for the interface</p>
              </div>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="spanish">Español</SelectItem>
                  <SelectItem value="french">Français</SelectItem>
                  <SelectItem value="german">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Demo Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Demo Mode
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Demo Mode Notifications</Label>
                <p className="text-sm text-gray-500">Show reminders that this is a demonstration system</p>
              </div>
              <Switch checked={demoNotifications} onCheckedChange={setDemoNotifications} />
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Bell className="h-5 w-5 text-amber-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-amber-900">Demo Mode Active</h3>
                  <p className="text-sm text-amber-800 mt-1">
                    This application is running in demonstration mode with mock data. All analysis results and reports
                    are simulated for educational purposes only.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
