"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Calendar, Eye, AlertTriangle, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { mockPatients } from "@/lib/mock-data"

interface PatientsPageProps {
  onViewStudyDetails: (study: any) => void
}

export default function PatientsPage({ onViewStudyDetails }: PatientsPageProps) {
  const [expandedPatients, setExpandedPatients] = useState<Set<string>>(new Set(["P1234"]))

  const togglePatientExpansion = (patientId: string) => {
    const newExpanded = new Set(expandedPatients)
    if (newExpanded.has(patientId)) {
      newExpanded.delete(patientId)
    } else {
      newExpanded.add(patientId)
    }
    setExpandedPatients(newExpanded)
  }

  const getDiagnosisBadge = (diagnosis: string, confidence: number) => {
    if (diagnosis === "Sin Análisis") {
      return {
        variant: "outline" as const,
        icon: AlertTriangle,
        color: "text-yellow-600",
      }
    }
    if (diagnosis.toLowerCase().includes("pneumonia")) {
      return {
        variant: "destructive" as const,
        icon: AlertTriangle,
        color: "text-red-600",
      }
    }
    return {
      variant: "secondary" as const,
      icon: CheckCircle,
      color: "text-green-600",
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Patient Studies</h2>
        <Badge variant="outline" className="text-sm">
          {mockPatients.length} Patients • {mockPatients.reduce((acc, p) => acc + p.studies.length, 0)} Studies
        </Badge>
      </div>

      <div className="grid gap-4">
        {mockPatients.map((patient) => {
          const isExpanded = expandedPatients.has(patient.patientId)
          const latestStudy = patient.studies[0] // Studies are sorted by date desc

          return (
            <Card key={patient.patientId} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePatientExpansion(patient.patientId)}
                      className="p-1"
                    >
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </Button>
                    <div>
                      <CardTitle className="text-lg">{patient.name}</CardTitle>
                      <p className="text-sm text-gray-600">ID: {patient.patientId}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{patient.studies.length} Studies</p>
                    <p className="text-xs text-gray-500">
                      Latest: {new Date(latestStudy.studyDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardHeader>

              {isExpanded && (
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {patient.studies.map((study, index) => {
                      const badge = getDiagnosisBadge(study.diagnosis, study.confidence)

                      return (
                        <div
                          key={`${study.patientId}-${study.studyDate}`}
                          className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          {/* Thumbnail */}
                          <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                            <img
                              src="/placeholder.svg?height=64&width=64"
                              alt="X-ray thumbnail"
                              className="w-full h-full object-cover"
                            />
                          </div>

                          {/* Study Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <Calendar className="h-4 w-4 text-gray-500" />
                              <span className="text-sm font-medium">
                                {new Date(study.studyDate).toLocaleDateString("en-US", {
                                  year: "numeric",
                                  month: "short",
                                  day: "numeric",
                                })}
                              </span>
                              {index === 0 && (
                                <Badge variant="outline" className="text-xs">
                                  Latest
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant={badge.variant} className="flex items-center gap-1">
                                <badge.icon className="h-3 w-3" />
                                {study.diagnosis}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-600">Confidence:</span>
                              {study.diagnosis === "Sin Análisis" ? (
                                <span className="text-xs text-gray-500">Pending analysis</span>
                              ) : (
                                <>
                                  <Progress value={study.confidence * 100} className="w-20 h-2" />
                                  <span className="text-xs font-medium">{Math.round(study.confidence * 100)}%</span>
                                </>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <Button
                            onClick={() => onViewStudyDetails(study)}
                            size="sm"
                            className="flex items-center gap-2"
                          >
                            <Eye className="h-4 w-4" />
                            View Details
                          </Button>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
