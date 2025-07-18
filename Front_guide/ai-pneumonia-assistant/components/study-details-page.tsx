"use client"

import { useState } from "react"
import { ArrowLeft, Download, Copy, FileText, Loader2, Eye, EyeOff, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"

interface StudyDetailsPageProps {
  study: any
  onBack: () => void
}

export default function StudyDetailsPage({ study, onBack }: StudyDetailsPageProps) {
  const [showHeatmap, setShowHeatmap] = useState(false)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [reportText, setReportText] = useState("")
  const [copied, setCopied] = useState(false)

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true)

    try {
      const response = await fetch("/api/generate-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          patientId: study.patientId,
          studyDate: study.studyDate,
          diagnosis: study.diagnosis,
          confidence: study.confidence,
          imagePath: study.imagePath,
        }),
      })

      const data = await response.json()
      setReportText(data.reportText)
    } catch (error) {
      console.error("Error generating report:", error)
    } finally {
      setIsGeneratingReport(false)
    }
  }

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(reportText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Error copying to clipboard:", error)
    }
  }

  const handleDownloadPDF = () => {
    const element = document.createElement("a")
    const file = new Blob([reportText], { type: "text/plain" })
    element.href = URL.createObjectURL(file)
    element.download = `pneumonia-report-${study.patientId}-${study.studyDate}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const getDiagnosisBadge = (diagnosis: string) => {
    if (diagnosis.toLowerCase().includes("pneumonia")) {
      return { variant: "destructive" as const, color: "text-red-600" }
    }
    return { variant: "secondary" as const, color: "text-green-600" }
  }

  const badge = getDiagnosisBadge(study.diagnosis)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={onBack} className="flex items-center gap-2 bg-transparent">
          <ArrowLeft className="h-4 w-4" />
          Back to Patient Studies
        </Button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Study Details</h2>
          <p className="text-gray-600">
            Patient {study.patientId} • {new Date(study.studyDate).toLocaleDateString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Preview */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Chest X-Ray</CardTitle>
              <div className="flex items-center gap-2">
                <Switch id="heatmap" checked={showHeatmap} onCheckedChange={setShowHeatmap} />
                <label htmlFor="heatmap" className="text-sm font-medium flex items-center gap-1">
                  {showHeatmap ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  Heatmap Overlay
                </label>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden">
              <img
                src="/placeholder.svg?height=400&width=400"
                alt="Chest X-ray"
                className="w-full h-full object-cover"
              />
              {showHeatmap && (
                <div className="absolute inset-0 bg-gradient-to-br from-red-500/30 via-transparent to-yellow-500/20 rounded-lg">
                  <div className="absolute top-1/3 left-1/2 w-16 h-16 bg-red-500/50 rounded-full blur-sm transform -translate-x-1/2"></div>
                </div>
              )}
            </div>
            <div className="mt-4 text-sm text-gray-600">
              <p>
                <strong>Resolution:</strong> 512x512 pixels
              </p>
              <p>
                <strong>File:</strong> {study.imagePath}
              </p>
              <p>
                <strong>Analysis Model:</strong> CNN + MedGemma-4B
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Diagnosis */}
            <div>
              <h3 className="text-lg font-medium mb-2">Diagnosis</h3>
              <Badge variant={badge.variant} className="text-sm">
                {study.diagnosis}
              </Badge>
            </div>

            {/* Confidence */}
            <div>
              <h3 className="text-lg font-medium mb-3">Confidence Level</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">AI Confidence</span>
                  <span className="text-sm font-medium">{Math.round(study.confidence * 100)}%</span>
                </div>
                <Progress value={study.confidence * 100} className="h-3" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Low</span>
                  <span>Moderate</span>
                  <span>High</span>
                </div>
              </div>
            </div>

            {/* Generate Report */}
            <div className="pt-4 border-t">
              <Button onClick={handleGenerateReport} disabled={isGeneratingReport} className="w-full mb-4" size="lg">
                {isGeneratingReport ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Generate Medical Report
                  </>
                )}
              </Button>

              {reportText && (
                <div className="flex gap-2">
                  <Button onClick={handleCopyReport} variant="outline" size="sm" className="flex-1 bg-transparent">
                    {copied ? (
                      <>
                        <Check className="mr-2 h-4 w-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy
                      </>
                    )}
                  </Button>
                  <Button onClick={handleDownloadPDF} variant="outline" size="sm" className="flex-1 bg-transparent">
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Report Display */}
      {reportText && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Medical Report</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64 w-full rounded-md border p-4">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{reportText}</div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
