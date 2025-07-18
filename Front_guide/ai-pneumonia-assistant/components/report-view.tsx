"use client"

import { useState } from "react"
import { Copy, Download, RotateCcw, FileText, Check, Printer } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

type AnalysisResult = {
  diagnosis: string
  confidence: number
  imagePath: string
}

interface ReportViewProps {
  reportText: string
  analysisResult: AnalysisResult | null
  onStartOver: () => void
}

export default function ReportView({ reportText, analysisResult, onStartOver }: ReportViewProps) {
  const [copied, setCopied] = useState(false)

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(reportText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Error al copiar al portapapeles:", error)
    }
  }

  const handleDownloadReport = () => {
    const element = document.createElement("a")
    const file = new Blob([reportText], { type: "text/plain;charset=utf-8" })
    element.href = URL.createObjectURL(file)
    element.download = `reporte-neumonia-${new Date().toISOString().split("T")[0]}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const handlePrint = () => {
    const printWindow = window.open("", "_blank")
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Reporte Médico - Análisis de Neumonía</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
              h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
              .header { margin-bottom: 30px; }
              .content { white-space: pre-wrap; }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>Reporte Médico - Análisis de Neumonía IA</h1>
              <p><strong>Fecha:</strong> ${new Date().toLocaleDateString("es-ES")}</p>
              <p><strong>Diagnóstico:</strong> ${analysisResult?.diagnosis || "N/A"}</p>
              <p><strong>Confianza:</strong> ${analysisResult?.confidence || 0}%</p>
            </div>
            <div class="content">${reportText}</div>
          </body>
        </html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  return (
    <div className="space-y-6">
      {/* Encabezado del Reporte */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Reporte Médico Generado
            </CardTitle>
            {analysisResult && (
              <Badge
                variant={analysisResult.diagnosis.toLowerCase().includes("neumonía") ? "destructive" : "secondary"}
              >
                {analysisResult.diagnosis} ({analysisResult.confidence}%)
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleCopyToClipboard} variant="outline" size="sm">
              {copied ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  ¡Copiado!
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copiar al Portapapeles
                </>
              )}
            </Button>

            <Button onClick={handleDownloadReport} variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Descargar Reporte
            </Button>

            <Button onClick={handlePrint} variant="outline" size="sm">
              <Printer className="mr-2 h-4 w-4" />
              Imprimir
            </Button>

            <Button onClick={onStartOver} variant="outline" size="sm">
              <RotateCcw className="mr-2 h-4 w-4" />
              Nuevo Análisis
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Contenido del Reporte */}
      <Card>
        <CardHeader>
          <CardTitle>Reporte Detallado</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96 w-full rounded-md border p-4">
            <div className="whitespace-pre-wrap text-sm leading-relaxed font-mono">
              {reportText || "No se ha generado ningún reporte aún."}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Información del Reporte */}
      <Card>
        <CardHeader>
          <CardTitle>Información del Reporte</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Generado:</span>
              <p className="text-gray-600">{new Date().toLocaleString("es-ES")}</p>
            </div>
            <div>
              <span className="font-medium">Modelo IA:</span>
              <p className="text-gray-600">MedGemma-4B-IT (Simulado)</p>
            </div>
            {analysisResult && (
              <>
                <div>
                  <span className="font-medium">Diagnóstico:</span>
                  <p className="text-gray-600">{analysisResult.diagnosis}</p>
                </div>
                <div>
                  <span className="font-medium">Nivel de Confianza:</span>
                  <p className="text-gray-600">{analysisResult.confidence}%</p>
                </div>
              </>
            )}
            <div>
              <span className="font-medium">Tipo de Análisis:</span>
              <p className="text-gray-600">Detección de Neumonía por IA</p>
            </div>
            <div>
              <span className="font-medium">Estado:</span>
              <p className="text-gray-600">Reporte Completo</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Aviso Legal */}
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="pt-6">
          <div className="text-sm text-amber-800">
            <p className="font-medium mb-2">⚠️ Aviso Importante - Simulación</p>
            <p>
              Este reporte ha sido generado por una simulación con fines demostrativos únicamente. No debe utilizarse
              para diagnósticos médicos reales. Siempre consulte con un profesional de la salud calificado para
              cualquier preocupación médica.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
