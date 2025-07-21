"use client"

import { useState, useEffect } from "react"
import { ChevronDown, ChevronRight, Calendar, Image as ImageIcon, Eye, AlertTriangle, CheckCircle, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"

interface Patient {
  id: string
  nombre: string
  edad?: number
  genero?: string
  fecha_registro: string
}

interface Study {
  id: string
  patient_id: string
  fecha_estudio: string
  filename: string
  descripcion?: string
  diagnostico?: string
  confianza?: number
}

interface PatientsPageProps {
  onViewPatientDetails?: (patient: Patient) => void
  refreshKey?: number
}

export default function PatientsPage({ onViewPatientDetails, refreshKey }: PatientsPageProps) {
  const [patients, setPatients] = useState<Patient[]>([])
  const [expandedPatients, setExpandedPatients] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [studiesByPatient, setStudiesByPatient] = useState<Record<string, Study[]>>({})
  const [loadingStudies, setLoadingStudies] = useState<string | null>(null)
  const [totalStudies, setTotalStudies] = useState(0)
  const [studyToDelete, setStudyToDelete] = useState<{study: Study, patientId: string} | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const fetchPatients = async () => {
      setLoading(true)
      try {
        const res = await fetch("http://localhost:8000/api/v1/patients")
        if (!res.ok) throw new Error("Error fetching patients")
        const data = await res.json()
        setPatients(data)
      } catch (err) {
        setPatients([])
      } finally {
        setLoading(false)
      }
    }
    fetchPatients()
    // Limpiar estudios cacheados para forzar refetch
    setStudiesByPatient({})
  }, [refreshKey])

  // Calcular total de estudios
  useEffect(() => {
    const fetchAllStudies = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/studies")
        if (!res.ok) throw new Error("Error fetching studies")
        const data = await res.json()
        setTotalStudies(data.length)
      } catch {
        setTotalStudies(0)
      }
    }
    fetchAllStudies()
  }, [patients])

  const togglePatientExpansion = async (patientId: string) => {
    const newExpanded = new Set(expandedPatients)
    if (newExpanded.has(patientId)) {
      newExpanded.delete(patientId)
    } else {
      newExpanded.add(patientId)
      // Si no se han cargado los estudios, pedirlos
      if (!studiesByPatient[patientId]) {
        setLoadingStudies(patientId)
        try {
          const res = await fetch(`http://localhost:8000/api/v1/studies?patient_id=${patientId}`)
          if (res.ok) {
            const data = await res.json()
            setStudiesByPatient(prev => ({ ...prev, [patientId]: data }))
          }
        } finally {
          setLoadingStudies(null)
        }
      }
    }
    setExpandedPatients(newExpanded)
  }

  const handleDeleteStudy = async () => {
    if (!studyToDelete) return
    setDeleting(true)
    try {
      await fetch(`http://localhost:8000/api/v1/studies/${studyToDelete.study.id}`, { method: "DELETE" })
      // Actualizar lista de estudios del paciente
      setStudiesByPatient(prev => ({
        ...prev,
        [studyToDelete.patientId]: (prev[studyToDelete.patientId] || []).filter(s => s.id !== studyToDelete.study.id)
      }))
      setStudyToDelete(null)
    } finally {
      setDeleting(false)
    }
  }

  // Badge de diagnóstico
  const getDiagnosisBadge = (diagnosis: string | undefined, confidence: number | undefined) => {
    if (!diagnosis || diagnosis === "Sin Análisis") {
      return {
        variant: "outline" as const,
        icon: AlertTriangle,
        color: "text-yellow-600",
      }
    }
    if (diagnosis.toLowerCase().includes("neumonía") || diagnosis.toLowerCase().includes("pneumonia")) {
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

  const backendUrl = 'http://localhost:8000';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Patient Studies</h2>
        <Badge variant="outline" className="text-sm">
          {patients.length} Patients • {totalStudies} Studies
        </Badge>
      </div>
      <div className="grid gap-4">
        {loading && <div className="text-gray-500">Loading patients...</div>}
        {!loading && patients.length === 0 && <div className="text-gray-500">No patients found.</div>}
        {patients.map((patient) => {
          const isExpanded = expandedPatients.has(patient.id)
          const studies = studiesByPatient[patient.id] || []
          // Ordenar estudios por fecha descendente
          const sortedStudies = [...studies].sort((a, b) => new Date(b.fecha_estudio).getTime() - new Date(a.fecha_estudio).getTime())
          const latestStudy = sortedStudies[0]
          return (
            <Card key={patient.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePatientExpansion(patient.id)}
                      className="p-1"
                    >
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </Button>
                    <div>
                      <CardTitle className="text-lg">{patient.nombre}</CardTitle>
                      <p className="text-sm text-gray-600">ID: {patient.id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{studies.length} Studies</p>
                    <p className="text-xs text-gray-500">
                      Latest: {latestStudy ? new Date(latestStudy.fecha_estudio).toLocaleDateString() : "-"}
                    </p>
                  </div>
                </div>
              </CardHeader>
              {isExpanded && (
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {loadingStudies === patient.id && (
                      <div className="text-gray-500">Loading studies...</div>
                    )}
                    {!loadingStudies && studies.length === 0 && (
                      <div className="text-gray-500">No studies found for this patient.</div>
                    )}
                    {sortedStudies.map((study, index) => {
                      console.log("STUDY OBJETO:", study);
                      const imgUrl = study.filename ? `${backendUrl}/uploads/images/${study.filename}` : "/placeholder.svg?height=64&width=64";
                      console.log("IMG URL:", imgUrl);
                      const badge = getDiagnosisBadge(study.diagnostico, study.confianza)
                      return (
                        <div
                          key={study.id}
                          className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          {/* Thumbnail */}
                          <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                            <img
                              src={imgUrl}
                              alt="X-ray thumbnail"
                              className="w-full h-full object-cover"
                            />
                          </div>
                          {/* Study Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <Calendar className="h-4 w-4 text-gray-500" />
                              <span className="text-sm font-medium">
                                {new Date(study.fecha_estudio).toLocaleDateString("en-US", {
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
                                {study.diagnostico || "Sin Análisis"}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-600">Confidence:</span>
                              {typeof study.confianza !== "number" ? (
                                <span className="text-xs text-gray-500">Pending analysis</span>
                              ) : (
                                <>
                                  <Progress value={study.confianza * 100} className="w-20 h-2" />
                                  <span className="text-xs font-medium">{Math.round(study.confianza * 100)}%</span>
                                </>
                              )}
                            </div>
                          </div>
                          {/* Actions */}
                          <Button
                            onClick={() => {}}
                            size="sm"
                            className="flex items-center gap-2"
                          >
                            <Eye className="h-4 w-4" />
                            View Details
                          </Button>
                          <Button
                            onClick={() => setStudyToDelete({study, patientId: patient.id})}
                            size="sm"
                            variant="destructive"
                            className="flex items-center gap-2"
                          >
                            <Trash2 className="h-4 w-4" />
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
      {/* Modal de confirmación de borrado */}
      <Dialog open={!!studyToDelete} onOpenChange={open => { if (!open) setStudyToDelete(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar borrado</DialogTitle>
          </DialogHeader>
          <div>¿Seguro que desea borrar este estudio? Esta acción no se puede deshacer.</div>
          <DialogFooter>
            <Button onClick={() => setStudyToDelete(null)} variant="outline" disabled={deleting}>Cancelar</Button>
            <Button onClick={handleDeleteStudy} variant="destructive" disabled={deleting}>
              {deleting ? "Borrando..." : "Borrar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

