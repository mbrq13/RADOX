import { type NextRequest, NextResponse } from "next/server"
import { addStudyToPatient } from "@/lib/mock-data"

export async function POST(request: NextRequest) {
  try {
    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 2000 + Math.random() * 2000))

    const formData = await request.formData()
    const image = formData.get("image") as File
    const patientId = formData.get("patientId") as string
    const studyDate = formData.get("studyDate") as string

    if (!image || !patientId || !studyDate) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Mock analysis results
    const scenarios = [
      { diagnosis: "Pneumonia Detected", confidence: 0.75 + Math.random() * 0.2 },
      { diagnosis: "Possible Pneumonia", confidence: 0.6 + Math.random() * 0.15 },
      { diagnosis: "Normal", confidence: 0.1 + Math.random() * 0.4 },
      { diagnosis: "Normal", confidence: 0.1 + Math.random() * 0.3 },
    ]

    const result = scenarios[Math.floor(Math.random() * scenarios.length)]
    const imagePath = `/uploads/${patientId}_${studyDate.replace(/-/g, "")}.png`

    const study = {
      patientId,
      studyDate,
      diagnosis: result.diagnosis,
      confidence: result.confidence,
      imagePath,
    }

    // Add to mock data
    addStudyToPatient(study)

    return NextResponse.json(study)
  } catch (error) {
    console.error("Analysis error:", error)
    return NextResponse.json({ error: "Analysis failed" }, { status: 500 })
  }
}
