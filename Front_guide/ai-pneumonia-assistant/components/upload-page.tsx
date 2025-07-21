"use client"

import { useState, useCallback, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, FileImage, Loader2, Calendar, User, AlertTriangle, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
// Quitar importación de mockPatients y helpers
// import { mockPatients, createNewPatientWithPendingStudy } from "@/lib/mock-data"

interface UploadPageProps {
  onUploadComplete: (patientId: string) => void
}

interface AnalysisResult {
  success: boolean
  resultado: {
    diagnostico: string
    confianza: number
    porcentaje: number
    tieneNeumonía: boolean
    puedeGenerarInforme: boolean
    imagePath: string
    heatmap?: string // Base64 encoded heatmap image
  }
  timestamp: string
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
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false)
  const [patients, setPatients] = useState<any[]>([])
  const [loadingPatients, setLoadingPatients] = useState(false)

  // Obtener pacientes reales del backend
  const fetchPatients = async () => {
    setLoadingPatients(true)
    try {
      const res = await fetch("http://localhost:8000/api/v1/patients")
      if (!res.ok) throw new Error("Error fetching patients")
      const data = await res.json()
      setPatients(data)
    } catch (err) {
      setPatients([])
    } finally {
      setLoadingPatients(false)
    }
  }

  useEffect(() => {
    fetchPatients()
  }, [])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setAnalysisResult(null) // Reset previous results
      setIsAnalysisComplete(false) // Reset completion state
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
    if (!selectedFile || !finalPatientId) return;

    setIsUploading(true);
    setUploadProgress(0);
    setAnalysisResult(null);
    setIsAnalysisComplete(false);

    let progressInterval: NodeJS.Timeout | undefined;

    try {
      // Simular progreso de carga
      progressInterval = setInterval(() => {
        setUploadProgress((prev: number) => {
          if (prev >= 90) {
            if (progressInterval) clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // 1. Crear paciente si es nuevo
      if (patientId === "__new__") {
        await fetch("http://localhost:8000/api/v1/patients", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: newPatientId,
            nombre: newPatientName,
            fecha_registro: new Date().toISOString(),
          }),
        });
        await fetchPatients(); // Refrescar lista tras crear
      }

      // 2. Subir estudio (imagen)
      const formData = new FormData();
      formData.append("patient_id", finalPatientId);
      formData.append("descripcion", `Estudio del ${studyDate}`);
      formData.append("file", selectedFile);

      const res = await fetch("http://localhost:8000/api/v1/studies", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Error al subir el estudio");
      const study = await res.json();

      // 3. Mostrar resultado simulado (puedes adaptar para análisis real luego)
      const isPneumonia = Math.random() > 0.5;
      const confidence = isPneumonia ? 0.7 + Math.random() * 0.3 : 0.1 + Math.random() * 0.3;
      const heatmapPlaceholder = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

      // PATCH para guardar diagnostico/confianza en el estudio
      await fetch(`http://localhost:8000/api/v1/studies/${study.id}`, {
        method: "PATCH",
        body: (() => {
          const fd = new FormData();
          fd.append("diagnostico", isPneumonia ? "Neumonía" : "Normal");
          fd.append("confianza", confidence.toString());
          return fd;
        })(),
      });

      const backendUrl = 'http://localhost:8000';
      const result: AnalysisResult = {
        success: true,
        resultado: {
          diagnostico: isPneumonia ? "Neumonía" : "Normal",
          confianza: confidence,
          porcentaje: Math.round(confidence * 100),
          tieneNeumonía: isPneumonia,
          puedeGenerarInforme: isPneumonia && confidence >= 0.7,
          imagePath: `${backendUrl}/uploads/images/${study.filename}`,
          heatmap: heatmapPlaceholder,
        },
        timestamp: new Date().toISOString(),
      };
      setAnalysisResult(result);
      setIsAnalysisComplete(true);

      if (progressInterval) clearInterval(progressInterval);
      setUploadProgress(100);
      setIsUploading(false);
    } catch (error) {
      console.error("Upload failed:", error);
      if (progressInterval) {
        clearInterval(progressInterval);
      }
      setIsUploading(false);
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      alert(`Error en el análisis: ${errorMessage}`);
    }
  };

  const generateReport = async () => {
    if (!analysisResult || !analysisResult.resultado.puedeGenerarInforme) {
      alert("No se puede generar informe. Se requiere detección de neumonía con alta confianza.")
      return
    }

    setIsGeneratingReport(true)

    try {
      // Simulate report generation time
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Simulate report data
      const reportData = {
        case_id: `CASE_${Date.now()}`,
        timestamp: new Date().toISOString(),
        generated_by: "RADOX AI System",
        full_report: `INFORME MÉDICO SIMULADO

PACIENTE: ${patientId === "__new__" ? newPatientName : (patients.find(p => p.id === patientId)?.nombre || 'N/A')}
FECHA DEL ESTUDIO: ${studyDate}
DIAGNÓSTICO: ${analysisResult.resultado.diagnostico}
CONFIANZA: ${(analysisResult.resultado.confianza * 100).toFixed(1)}%

HALLAZGOS:
- ${analysisResult.resultado.diagnostico === 'Neumonía' ? 'Se observan opacidades pulmonares sugestivas de neumonía' : 'No se observan hallazgos patológicos significativos'}
- Campos pulmonares bien ventilados
- Siluetas cardíacas normales

IMPRESIÓN DIAGNÓSTICA:
${analysisResult.resultado.diagnostico === 'Neumonía' ? 'Neumonía probable' : 'Radiografía de tórax normal'}

RECOMENDACIONES:
${analysisResult.resultado.diagnostico === 'Neumonía' ? 'Se recomienda evaluación clínica adicional y tratamiento antibiótico según protocolo' : 'No se requieren estudios adicionales'}`
      }

      console.log('Informe generado (simulado):', reportData)
      
      // Complete the upload process
      const finalPatientId = patientId === "__new__" ? newPatientId : patientId;
      onUploadComplete(finalPatientId)

    } catch (error) {
      console.error('Error generando informe:', error)
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
      alert(`Error al generar informe: ${errorMessage}`)
    } finally {
      setIsGeneratingReport(false)
    }
  }

  const startNewAnalysis = () => {
    setSelectedFile(null)
    setPreviewUrl("")
    setAnalysisResult(null)
    setIsAnalysisComplete(false)
    setIsUploading(false)
    setUploadProgress(0)
    }

  const completeWithoutReport = () => {
    const finalPatientId = patientId === "__new__" ? newPatientId : patientId;
    onUploadComplete(finalPatientId)
  }

  const getDiagnosisColor = (diagnosis: string) => {
    if (diagnosis === 'Neumonía') return 'text-red-600'
    if (diagnosis === 'Normal') return 'text-green-600'
    return 'text-gray-600'
  }

  const getDiagnosisIcon = (diagnosis: string) => {
    if (diagnosis === 'Neumonía') return <AlertTriangle className="h-6 w-6 text-red-600" />
    if (diagnosis === 'Normal') return <CheckCircle className="h-6 w-6 text-green-600" />
    return null
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
                {patients.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.id} - {p.nombre}
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
                {loadingPatients ? "Loading patients..." : "Select an existing patient or add a new one"}
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
              disabled={!selectedFile || !(patientId && (patientId !== "__new__" || (newPatientId && newPatientName))) || isUploading || isAnalysisComplete}
              className="w-full"
              size="lg"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : isAnalysisComplete ? (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Analysis Complete
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

      {/* Analysis Results */}
      {analysisResult && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              AI Analysis Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Diagnosis and Confidence */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {getDiagnosisIcon(analysisResult.resultado.diagnostico)}
                  <div>
                    <h3 className="font-semibold">Diagnosis</h3>
                    <p className={`text-lg font-bold ${getDiagnosisColor(analysisResult.resultado.diagnostico)}`}>
                      {analysisResult.resultado.diagnostico}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Confidence</h3>
                  <div className="flex items-center gap-2">
                    <Progress value={analysisResult.resultado.confianza * 100} className="flex-1" />
                    <span className="text-sm font-medium">
                      {(analysisResult.resultado.confianza * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Details</h3>
                  <div className="text-sm space-y-1">
                    <p><span className="font-medium">Analysis Date:</span> {new Date(analysisResult.timestamp).toLocaleString()}</p>
                    <p><span className="font-medium">Can Generate Report:</span> {analysisResult.resultado.puedeGenerarInforme ? 'Yes' : 'No'}</p>
                  </div>
                </div>
              </div>

              {/* Heatmap */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">CNN Heatmap</h3>
                  {analysisResult.resultado.heatmap ? (
                    <div className="bg-gray-100 rounded-lg p-2">
                      <img
                        src={analysisResult.resultado.heatmap}
                        alt="CNN Heatmap"
                        className="w-full h-48 object-contain rounded"
                      />
                      <p className="text-xs text-gray-600 mt-2 text-center">
                        Areas highlighted by CNN model
                      </p>
                    </div>
                  ) : (
                    <div className="bg-gray-100 rounded-lg p-4 text-center">
                      <p className="text-gray-500">Heatmap not available</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Actions</h3>
                  {analysisResult.resultado.puedeGenerarInforme ? (
                    <div className="space-y-3">
                      <p className="text-sm text-gray-600">
                        Pneumonia detected with high confidence. You can now generate a detailed medical report.
                      </p>
                      <Button
                        onClick={generateReport}
                        disabled={isGeneratingReport}
                        className="w-full"
                        size="lg"
                      >
                        {isGeneratingReport ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Generating Report...
                          </>
                        ) : (
                          <>
                            <FileImage className="mr-2 h-4 w-4" />
                            Generate Report & Exit
                          </>
                        )}
                      </Button>
                      <Button
                        onClick={completeWithoutReport}
                        variant="outline"
                        className="w-full"
                        size="lg"
                      >
                        Exit Without Report
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <p className="text-sm text-gray-600">
                        {analysisResult.resultado.diagnostico === 'Normal' 
                          ? 'No pneumonia detected. No medical report needed.'
                          : 'Pneumonia detected but confidence is below threshold for report generation.'
                        }
                      </p>
                      <Button
                        onClick={completeWithoutReport}
                        className="w-full"
                        size="lg"
                      >
                        Complete Upload
                      </Button>
                    </div>
                  )}
                </div>

                {/* New Analysis Button */}
                <div className="pt-4 border-t">
                  <Button
                    onClick={startNewAnalysis}
                    variant="outline"
                    className="w-full"
                    size="lg"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    New Analysis
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
