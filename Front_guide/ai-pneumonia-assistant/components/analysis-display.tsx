"use client"

import { useState } from "react"
import { FileText, Loader2, AlertTriangle, CheckCircle, Stethoscope } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { simulateReportGeneration } from "@/lib/simulation"

type AnalysisResult = {
  diagnosis: string
  confidence: number
  imagePath: string
}

interface AnalysisDisplayProps {
  result: AnalysisResult
  onReportGenerated: (report: string) => void
  onError: (error: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function AnalysisDisplay({
  result,
  onReportGenerated,
  onError,
  isLoading,
  setIsLoading,
}: AnalysisDisplayProps) {
  const [reportProgress, setReportProgress] = useState(0)

  const handleGenerateReport = async () => {
    setIsLoading(true)
    setReportProgress(0)

    try {
      // Simular progreso de generación de reporte
      const progressInterval = setInterval(() => {
        setReportProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 12
        })
      }, 400)

      const report = await simulateReportGeneration(result)

      clearInterval(progressInterval)
      setReportProgress(100)

      setTimeout(() => {
        onReportGenerated(report)
        setIsLoading(false)
      }, 600)
    } catch (error) {
      onError(error instanceof Error ? error.message : "Error generando el reporte")
      setIsLoading(false)
      setReportProgress(0)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-red-600"
    if (confidence >= 60) return "text-yellow-600"
    return "text-green-600"
  }

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 80) return { variant: "destructive" as const, icon: AlertTriangle, label: "Alto Riesgo" }
    if (confidence >= 60) return { variant: "secondary" as const, icon: AlertTriangle, label: "Riesgo Moderado" }
    return { variant: "secondary" as const, icon: CheckCircle, label: "Bajo Riesgo" }
  }

  const confidenceBadge = getConfidenceBadge(result.confidence)

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Resultados del Análisis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5" />
            Resultados del Análisis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Diagnóstico */}
          <div>
            <h3 className="text-lg font-medium mb-2">Diagnóstico</h3>
            <div className="flex items-center gap-2">
              <Badge variant={result.diagnosis.toLowerCase().includes("neumonía") ? "destructive" : "secondary"}>
                {result.diagnosis}
              </Badge>
            </div>
          </div>

          {/* Medidor de Confianza */}
          <div>
            <h3 className="text-lg font-medium mb-3">Nivel de Confianza</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Confianza de Neumonía</span>
                <Badge variant={confidenceBadge.variant} className="flex items-center gap-1">
                  <confidenceBadge.icon className="h-3 w-3" />
                  {result.confidence}%
                </Badge>
              </div>
              <Progress value={result.confidence} className="h-3" />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Bajo Riesgo</span>
                <span>Riesgo Moderado</span>
                <span>Alto Riesgo</span>
              </div>
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                <strong>Interpretación:</strong> {confidenceBadge.label} -
                {result.confidence >= 80
                  ? " Se recomienda evaluación médica inmediata."
                  : result.confidence >= 60
                    ? " Se sugiere seguimiento médico."
                    : " Resultado dentro de parámetros normales."}
              </div>
            </div>
          </div>

          {/* Sección de Generar Reporte */}
          <div className="pt-4 border-t">
            {isLoading && (
              <div className="space-y-3 mb-4">
                <Progress value={reportProgress} className="w-full" />
                <p className="text-sm text-gray-600 text-center">
                  {reportProgress < 30
                    ? "Iniciando análisis detallado..."
                    : reportProgress < 60
                      ? "Procesando con MedGemma IA..."
                      : reportProgress < 90
                        ? "Generando reporte médico..."
                        : "Finalizando reporte..."}
                </p>
              </div>
            )}

            <Button onClick={handleGenerateReport} disabled={isLoading} size="lg" className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generando Reporte...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Generar Reporte Médico
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Imagen de Rayos X */}
      <Card>
        <CardHeader>
          <CardTitle>Rayos X Procesados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
            <img
              src="/placeholder.svg?height=400&width=400"
              alt="Radiografía de tórax procesada"
              className="max-w-full max-h-full object-contain rounded-lg"
            />
          </div>

          <div className="mt-4 space-y-2">
            <div className="text-sm text-gray-600">
              <p>
                <strong>Estado:</strong> Imagen procesada y analizada
              </p>
              <p>
                <strong>Resolución:</strong> 512x512 píxeles
              </p>
              <p>
                <strong>Modelo IA:</strong> CNN + MedGemma-4B
              </p>
            </div>

            <div className="bg-blue-50 p-3 rounded-lg text-sm">
              <p className="text-blue-800">
                <strong>Nota:</strong> Esta es una imagen de demostración. En la versión real, aquí aparecería la
                radiografía procesada por el sistema.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
