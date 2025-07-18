"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, FileImage, Loader2, Calendar, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { mockPatients, createNewPatientWithPendingStudy } from "@/lib/mock-data"

interface UploadPageProps {
  onUploadComplete: (patientId: string) => void
}

export default function UploadPage({ onUploadComplete }: UploadPageProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>("")
  const [patientId, setPatientId] = useState("")
  const [newPatientId, setNewPatientId] = useState("")
  const [newPatientName, setNewPatientName] = useState("")
  const [studyDate, setStudyDate] = useState(new Date().toISOString().split("T")[0])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".bmp", ".tiff"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

      const handleUpload = async () => {
        const finalPatientId = patientId === "__new__" ? newPatientId : patientId;
        if (!selectedFile || !finalPatientId) return
        setIsUploading(true)
        setUploadProgress(0)
        
        let progressInterval: NodeJS.Timeout | undefined;
        
        try {
            // Simulate file upload
            const formData = new FormData()
            formData.append("image", selectedFile)
            formData.append("patientId", finalPatientId)
            if (patientId === "__new__") {
                formData.append("patientName", newPatientName)
            }
            formData.append("studyDate", studyDate)

            // Simulate upload progress
            progressInterval = setInterval(() => {
                setUploadProgress((prev) => {
                    if (prev >= 90) {
                        clearInterval(progressInterval)
                        return 90
                    }
                    return prev + 10
                })
            }, 200)

            // Simulate processing time
            await new Promise((resolve) => setTimeout(resolve, 2000))

            // Create new patient/study in mock data
            const imagePath = `/uploads/${finalPatientId}_${studyDate.replace(/-/g, '')}.png`
            if (patientId === "__new__") {
                createNewPatientWithPendingStudy(finalPatientId, newPatientName, studyDate, imagePath)
            } else {
                // For existing patients, we'll add the study with pending analysis
                const existingPatient = mockPatients.find(p => p.patientId === finalPatientId)
                if (existingPatient) {
                    const newStudy = {
                        patientId: finalPatientId,
                        studyDate,
                        diagnosis: "Sin Análisis",
                        confidence: 0,
                        imagePath,
                    }
                    existingPatient.studies.unshift(newStudy)
                }
            }

            clearInterval(progressInterval)
            setUploadProgress(100)

            setTimeout(() => {
                onUploadComplete(finalPatientId)
                setIsUploading(false)
            }, 500)
        } catch (error) {
            console.error("Upload failed:", error)
            if (progressInterval) {
                clearInterval(progressInterval)
            }
            setIsUploading(false)
        }
    }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Chest X-Ray</h2>
        <p className="text-gray-600">Upload a new chest X-ray for AI analysis and add it to a patient's studies.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              Select Image
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`p-8 text-center cursor-pointer rounded-2xl border-2 border-dashed transition-colors ${
                isDragActive ? "bg-blue-50 border-blue-300" : "bg-gray-50 hover:bg-gray-100 border-gray-300"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              {isDragActive ? (
                <p className="text-blue-600 font-medium">Drop the X-ray image here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">Drag and drop a chest X-ray image, or click to select</p>
                  <p className="text-sm text-gray-500">Supports JPEG, PNG, BMP, TIFF (max 10MB)</p>
                </div>
              )}
            </div>

            {previewUrl && (
              <div className="mt-4">
                <h3 className="text-sm font-medium mb-2">Preview</h3>
                <img
                  src={previewUrl || "/placeholder.svg"}
                  alt="X-ray preview"
                  className="w-full h-48 object-contain bg-gray-100 rounded-lg"
                />
                {selectedFile && (
                  <p className="text-xs text-gray-600 mt-2">
                    {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Patient Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Patient Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="patientId">Patient ID</Label>
              <select
                id="patientId"
                value={patientId}
                onChange={e => setPatientId(e.target.value)}
                className="mt-1 w-full border rounded p-2"
              >
                <option value="">-- Select existing patient --</option>
                {mockPatients.map(p => (
                  <option key={p.patientId} value={p.patientId}>
                    {p.patientId} - {p.name}
                  </option>
                ))}
                <option value="__new__">Add new patient...</option>
              </select>
              {patientId === "__new__" && (
                <>
                  <Input
                    id="newPatientId"
                    value={newPatientId}
                    onChange={e => setNewPatientId(e.target.value)}
                    placeholder="New Patient ID"
                    className="mt-2"
                  />
                  <Input
                    id="newPatientName"
                    value={newPatientName}
                    onChange={e => setNewPatientName(e.target.value)}
                    placeholder="New Patient Name"
                    className="mt-2"
                  />
                </>
              )}
              <p className="text-xs text-gray-500 mt-1">
                Select an existing patient or add a new one
              </p>
            </div>

            <div>
              <Label htmlFor="studyDate" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Study Date
              </Label>
              <Input
                id="studyDate"
                type="date"
                value={studyDate}
                onChange={(e) => setStudyDate(e.target.value)}
                className="mt-1"
              />
            </div>

            {isUploading && (
              <div className="space-y-2">
                <Progress value={uploadProgress} className="w-full" />
                <p className="text-sm text-gray-600 text-center">
                  {uploadProgress < 50 ? "Uploading image..." : "Analyzing with AI..."}
                </p>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!selectedFile || !(patientId && (patientId !== "__new__" || (newPatientId && newPatientName))) || isUploading}
              className="w-full"
              size="lg"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload & Analyze
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
