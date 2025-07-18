"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, FileImage, Loader2, Activity, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { simulateAnalysis } from "@/lib/simulation"

type AnalysisResult = {
  diagnosis: string
  confidence: number
  imagePath: string
}

interface UploadSectionProps {
  onAnalysisComplete: (result: AnalysisResult) => void
  onError: (error: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function UploadSection({ onAnalysisComplete, onError, isLoading, setIsLoading }: UploadSectionProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>("")
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

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    setUploadProgress(0)

    try {
      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 15
        })
      }, 300)

      // Simular análisis con IA
      const result = await simulateAnalysis(selectedFile)

      clearInterval(progressInterval)
      setUploadProgress(100)

      setTimeout(() => {
        onAnalysisComplete(result)
        setIsLoading(false)
      }, 800)
    } catch (error) {
      onError(error instanceof Error ? error.message : "Error en el análisis")
      setIsLoading(false)
      setUploadProgress(0)
    }
  }

  return (
    <div className="space-y-6">
      <Card className="border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Subir Radiografía de Tórax
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`p-8 text-center cursor-pointer rounded-2xl transition-colors ${
              isDragActive ? "bg-blue-50 border-blue-300" : "bg-gray-50 hover:bg-gray-100"
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-blue-600 font-medium">Suelta la imagen de rayos X aquí...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">
                  Arrastra y suelta una radiografía de tórax, o haz clic para seleccionar
                </p>
                <p className="text-sm text-gray-500">Soporta JPEG, PNG, BMP, TIFF (máx 10MB)</p>
              </div>
            )}
          </div>

          {previewUrl && (
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">Vista Previa</h3>
              <div className="relative">
                <img
                  src={previewUrl || "/placeholder.svg"}
                  alt="Vista previa de rayos X"
                  className="max-w-full h-64 object-contain mx-auto rounded-lg shadow-md"
                />
                {selectedFile && (
                  <div className="mt-2 text-sm text-gray-600">
                    {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </div>
                )}
              </div>
            </div>
          )}

          {isLoading && (
            <div className="mt-6 space-y-3">
              <Progress value={uploadProgress} className="w-full" />
              <p className="text-sm text-gray-600 text-center">
                {uploadProgress < 50
                  ? "Subiendo imagen..."
                  : uploadProgress < 90
                    ? "Procesando con IA..."
                    : "Finalizando análisis..."}
              </p>
            </div>
          )}

          <div className="mt-6 flex justify-center">
            <Button onClick={handleAnalyze} disabled={!selectedFile || isLoading} size="lg" className="px-8">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analizando...
                </>
              ) : (
                <>
                  <Activity className="mr-2 h-4 w-4" />
                  Analizar Rayos X
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Información del Demo */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900 mb-1">Simulación de Análisis IA</h3>
              <p className="text-sm text-blue-800">
                Esta demo simula el análisis de neumonía usando inteligencia artificial. Los resultados son ficticios y
                generados aleatoriamente para demostración.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
