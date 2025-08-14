// API client for communicating with the Express backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001"

export interface AnalysisResult {
  diagnosis: string
  confidence: number
  imagePath: string
}

export interface ReportRequest {
  diagnosis: string
  confidence: number
  imagePath: string
}

export async function analyzeImage(file: File): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append("image", file)

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Analysis failed: ${error}`)
  }

  return response.json()
}

export async function generateReport(request: ReportRequest): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/generate-report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Report generation failed: ${error}`)
  }

  const data = await response.json()
  return data.report || data.text || "Report generated successfully"
}
