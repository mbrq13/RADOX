"use client"

import { useState, useEffect } from "react"
import { Activity } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Header from "@/components/header"
import PatientsPage from "@/components/patients-page"
import UploadPage from "@/components/upload-page"
import SettingsPage from "@/components/settings-page"
import StudyDetailsPage from "@/components/study-details-page"
import HowItWorks from "@/components/how-it-works"
import LoginPage from "@/components/login-page"
import { useAuth } from "@/lib/auth-context"

type TabType = "patients" | "upload" | "settings"
type ViewType = "main" | "study-details"

export default function PneumoniaAssistant() {
  const { user, isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>("patients")
  const [currentView, setCurrentView] = useState<ViewType>("main")
  const [selectedStudy, setSelectedStudy] = useState<any>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  // Redirect to patients tab after login
  useEffect(() => {
    if (isAuthenticated) {
      setActiveTab("patients")
      setCurrentView("main")
    }
  }, [isAuthenticated])

  const handleViewStudyDetails = (study: any) => {
    setSelectedStudy(study)
    setCurrentView("study-details")
  }

  const handleBackToPatients = () => {
    setCurrentView("main")
    setSelectedStudy(null)
    setActiveTab("patients")
  }

  const handleUploadComplete = (patientId: string) => {
    setActiveTab("patients")
    setCurrentView("main")
    setRefreshKey(k => k + 1) // Forzar refresco
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />
  }

  const renderMainContent = () => {
    if (currentView === "study-details" && selectedStudy) {
      return <StudyDetailsPage study={selectedStudy} onBack={handleBackToPatients} />
    }

    switch (activeTab) {
      case "patients":
        return <PatientsPage onViewStudyDetails={handleViewStudyDetails} refreshKey={refreshKey} />
      case "upload":
        return user?.role === "viewer" ? (
          <div className="text-center py-12">
            <Card className="max-w-md mx-auto border-amber-200 bg-amber-50">
              <CardContent className="pt-6">
                <Activity className="h-12 w-12 text-amber-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-amber-900 mb-2">Acceso Restringido</h3>
                <p className="text-sm text-amber-800">
                  Los usuarios con rol de "Visualizador" no tienen permisos para subir nuevos estudios.
                </p>
              </CardContent>
            </Card>
          </div>
        ) : (
          <UploadPage onUploadComplete={handleUploadComplete} />
        )
      case "settings":
        return <SettingsPage />
      default:
        return <PatientsPage onViewStudyDetails={handleViewStudyDetails} refreshKey={refreshKey} />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Demo Notice */}
        <Card className="mb-6 border-amber-200 bg-amber-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-amber-800">
              <Activity className="h-4 w-4" />
              <span className="text-sm font-medium">Modo Demo Activo</span>
            </div>
            <p className="text-xs text-amber-700 mt-1">
              Sesión iniciada como: <strong>{user?.name}</strong> ({user?.role}) - Sistema de demostración con datos
              simulados.
            </p>
          </CardContent>
        </Card>

        {/* Main Content */}
        {renderMainContent()}

        {/* How It Works Section - Only show on main view */}
        {currentView === "main" && <HowItWorks />}
      </div>
    </div>
  )
}
