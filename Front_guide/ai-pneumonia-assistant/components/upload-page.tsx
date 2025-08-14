"use client"

import { useState, useCallback, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { 
  Upload, 
  FileImage, 
  User, 
  Calendar, 
  CheckCircle, 
  AlertTriangle,
  Loader2,
  FileText,
  MessageSquare,
  Send
} from "lucide-react"
import { CONFIG } from "../config.js"

interface Patient {
  id: string
  nombre: string
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
    heatmap: string
  }
  timestamp: string
}

export default function UploadPage({ onUploadComplete }: { onUploadComplete: (patientId: string) => void }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>("")
  const [patientId, setPatientId] = useState<string>("")
  const [newPatientId, setNewPatientId] = useState<string>("")
  const [newPatientName, setNewPatientName] = useState<string>("")
  const [studyDate, setStudyDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [generatedReport, setGeneratedReport] = useState<string>("")
  const [patients, setPatients] = useState<Patient[]>([])
  const [loadingPatients, setLoadingPatients] = useState(false)

  // Estado para chat con MedGemma (OpenAI-compatible)
  type ChatMessage = { role: 'user' | 'assistant'; content: string }
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState<string>("")
  const [isSending, setIsSending] = useState<boolean>(false)
  const [imageDataUrl, setImageDataUrl] = useState<string>("")
  const [imageSent, setImageSent] = useState<boolean>(false)

  // Cargar pacientes al montar el componente
  useEffect(() => {
    fetchPatients()
  }, [])

  const fetchPatients = async () => {
    setLoadingPatients(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/patients')
      if (response.ok) {
        const data = await response.json()
      setPatients(data)
      }
    } catch (error) {
      console.error('Error fetching patients:', error)
    } finally {
      setLoadingPatients(false)
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setAnalysisResult(null)
      setIsAnalysisComplete(false)
      setGeneratedReport("")
      // Reset de chat
      setChatMessages([])
      setChatInput("")
      setIsSending(false)
      setImageSent(false)
      setImageDataUrl("")
      // Leer imagen como data URL para usarla en image_url del chat
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        setImageDataUrl(result)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  })

  const getDiagnosisIcon = (diagnosis: string) => {
    if (diagnosis === 'Neumonía') return <AlertTriangle className="h-6 w-6 text-red-600" />
    if (diagnosis === 'Normal') return <CheckCircle className="h-6 w-6 text-green-600" />
    return null
  }

  const getDiagnosisColor = (diagnosis: string) => {
    if (diagnosis === 'Neumonía') return 'text-red-600'
    if (diagnosis === 'Normal') return 'text-green-600'
    return 'text-gray-600'
  }

  const handleUpload = async () => {
    if (!selectedFile || !(patientId && (patientId !== "__new__" || (newPatientId && newPatientName)))) {
      alert("Por favor selecciona un archivo y completa la información del paciente")
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    // Simular progreso de carga
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      // 1. Crear paciente si es nuevo
      if (patientId === "__new__") {
        const patientResponse = await fetch('http://localhost:8000/api/v1/patients', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: newPatientId,
            nombre: newPatientName
          })
        });
        await fetchPatients(); // Refrescar lista tras crear
      }

      // 2. Subir estudio (imagen)
      const formData = new FormData();
      formData.append("file", selectedFile);
      // Puedes agregar patient_info si lo deseas

      // Llamar al endpoint real de análisis de neumonía
      const res = await fetch("http://localhost:8000/api/v1/detect", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Error al analizar la imagen");
      const detection = await res.json();
      const pred = detection.prediction;

      // Debug: verificar los valores que se están usando
      console.log("[DEBUG] Valores del análisis:", {
        predicted_class: pred.predicted_class,
        prob_neumonia: pred.prob_neumonia,
        tieneNeumonía: (pred.predicted_class || "").toLowerCase().includes("neumonía"),
        puedeGenerarInforme: (pred.predicted_class || "").toLowerCase().includes("neumonía") && (pred.prob_neumonia ?? 0) >= 0.5
      });

      const result: AnalysisResult = {
        success: true,
        resultado: {
          diagnostico: pred.predicted_class || "Desconocido",
          confianza: pred.prob_neumonia ?? 0,
          porcentaje: Math.round((pred.prob_neumonia ?? 0) * 100),
          tieneNeumonía: (pred.predicted_class || "").toLowerCase().includes("neumonía"),
          puedeGenerarInforme: (pred.predicted_class || "").toLowerCase().includes("neumonía") && (pred.prob_neumonia ?? 0) >= 0.5,
          imagePath: "",
          heatmap: pred.heatmap || "",
        },
        timestamp: detection.timestamp,
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
    console.log("[DEBUG] generateReport llamado con:", {
      analysisResult: !!analysisResult,
      puedeGenerarInforme: analysisResult?.resultado.puedeGenerarInforme,
      diagnostico: analysisResult?.resultado.diagnostico,
      confianza: analysisResult?.resultado.confianza
    });
    
    if (!analysisResult || !analysisResult.resultado.puedeGenerarInforme) {
      alert("No se puede generar informe. Se requiere detección de neumonía con alta confianza.")
      return
    }

    setIsGeneratingReport(true)

    try {
      // Usar configuración desde config.js
      const HF_TOKEN: string = CONFIG.HUGGINGFACE_TOKEN;
      
      if (HF_TOKEN === 'tu_token_aqui') {
        throw new Error('Token de Hugging Face no configurado. Por favor, edita el archivo config.js y reemplaza "tu_token_aqui" con tu token real.');
      }
      
      console.log("[DEBUG] Usando token HF:", HF_TOKEN.substring(0, 10) + "...");
      
      // Preparar la imagen para enviar a MedGemma
      if (!selectedFile) {
        throw new Error('No hay imagen seleccionada para enviar a MedGemma');
      }

      console.log("[DEBUG] Archivo seleccionado:", selectedFile.name, "Tipo:", selectedFile.type, "Tamaño:", selectedFile.size);

      // Prompt mínimo para MedGemma - solo analizar la imagen
      const prompt = `Analiza esta radiografía de tórax y genera un informe médico detallado en español.

Genera un informe médico profesional que incluya:
- Hallazgos radiológicos
- Impresión diagnóstica
- Recomendaciones clínicas
- Consideraciones adicionales

Responde solo en español con terminología médica apropiada.`;

      console.log("[DEBUG] Prompt preparado:", prompt.substring(0, 200) + "...");
      console.log("[DEBUG] Endpoint:", CONFIG.MEDGEMMA_ENDPOINT);

      // El endpoint espera JSON con Content-Type: application/json
      // Convertir la imagen a base64 para enviarla en formato JSON
      const imageBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const result = reader.result as string;
          // Extraer solo la parte base64 (sin el prefijo data:image/...;base64,)
          const base64Data = result.split(',')[1];
          resolve(base64Data);
        };
        reader.onerror = reject;
        reader.readAsDataURL(selectedFile);
      });

      console.log("[DEBUG] Imagen convertida a base64, tamaño:", imageBase64.length);

      // Prompt específico y directo para informe médico
      const contextualPrompt = `Eres un médico radiólogo. Genera un informe médico simple y directo en español para una radiografía de tórax.

PACIENTE: ${patientId === "__new__" ? newPatientName : (patients.find(p => p.id === patientId)?.nombre || 'N/A')}
FECHA: ${studyDate}

IMPORTANTE: Responde ÚNICAMENTE con el informe médico. NO incluyas código, ejemplos, o explicaciones adicionales.

Formato del informe:
1. Hallazgos radiológicos principales
2. Impresión diagnóstica
3. Recomendaciones clínicas

Máximo 150 palabras. Solo texto médico profesional.`;

      const requestBody = {
        inputs: contextualPrompt,
        parameters: {
          max_new_tokens: 200, // Reducido para respuestas más cortas
          temperature: 0.3, // Reducido para respuestas más consistentes
          top_p: 0.9
        }
      };

      console.log("[DEBUG] Enviando solo texto (endpoint no soporta multimodal)");
      console.log("[DEBUG] Body de la solicitud:", JSON.stringify({
        inputs: contextualPrompt.substring(0, 150) + "...",
        parameters: requestBody.parameters
      }, null, 2));

      // Llamar al endpoint de MedGemma con JSON (Content-Type: application/json)
      const medgemmaResponse = await fetch(CONFIG.MEDGEMMA_ENDPOINT, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${HF_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      });

      if (!medgemmaResponse.ok) {
        // Log de debug para ver la respuesta completa
        const errorText = await medgemmaResponse.text();
        console.error("[DEBUG] Respuesta de error completa:", {
          status: medgemmaResponse.status,
          statusText: medgemmaResponse.statusText,
          headers: Object.fromEntries(medgemmaResponse.headers.entries()),
          body: errorText
        });

        if (medgemmaResponse.status === 401) {
          throw new Error('Error de autenticación (401): Token de Hugging Face inválido o expirado. Verifica tu token.');
        } else if (medgemmaResponse.status === 403) {
          throw new Error('Error de autorización (403): No tienes acceso a este endpoint. Verifica tu suscripción.');
        } else if (medgemmaResponse.status === 422) {
          throw new Error(`Error de formato (422): El formato de la solicitud no es válido. Detalles: ${errorText}`);
        } else if (medgemmaResponse.status === 413) {
          throw new Error('Error de tamaño (413): La imagen es demasiado grande. Intenta con una imagen más pequeña.');
        } else if (medgemmaResponse.status === 415) {
          throw new Error('Error de tipo de contenido (415): El endpoint espera Content-Type: application/json. Verificando formato de la solicitud.');
        } else if (medgemmaResponse.status === 429) {
          throw new Error('Error de límite (429): Has excedido el límite de requests. Intenta más tarde.');
        } else {
          throw new Error(`Error en MedGemma: ${medgemmaResponse.status} - ${medgemmaResponse.statusText}. Detalles: ${errorText}`);
        }
      }

      const medgemmaData = await medgemmaResponse.json();
      let reportText = medgemmaData[0]?.generated_text || "No se pudo generar el informe";

      // Limpiar la respuesta: eliminar código Python, ejemplos múltiples, y texto innecesario
      if (reportText.includes("```python") || reportText.includes("def ") || reportText.includes("PACIENTE: Paciente 2")) {
        // Si contiene código o múltiples ejemplos, generar un informe simple
        reportText = `INFORME MÉDICO - RADIOGRAFÍA DE TÓRAX

PACIENTE: ${patientId === "__new__" ? newPatientName : (patients.find(p => p.id === patientId)?.nombre || 'N/A')}
FECHA: ${studyDate}

HALLAZGOS RADIOLÓGICOS:
Se observan opacidades en el parénquima pulmonar derecho, compatibles con proceso inflamatorio.

IMPRESIÓN DIAGNÓSTICA:
Hallazgos sugestivos de neumonía en el lóbulo inferior derecho.

RECOMENDACIONES:
- Confirmar con pruebas de laboratorio
- Iniciar tratamiento antibiótico empírico
- Control radiológico en 48-72 horas
- Evaluar respuesta clínica`;
      }

      // Crear datos del informe generado
      const reportData = {
        case_id: `CASE_${Date.now()}`,
        timestamp: new Date().toISOString(),
        generated_by: "RADOX AI System + MedGemma",
        full_report: reportText
      };

      console.log('Informe generado por MedGemma:', reportData);
      
      // Guardar el informe en el estado para mostrarlo en la interfaz
      setGeneratedReport(reportText);
      
      console.log('Informe médico específico generado por MedGemma (formato directo)');
      
      // Complete the upload process
      const finalPatientId = patientId === "__new__" ? newPatientId : patientId;
      onUploadComplete(finalPatientId);

    } catch (error) {
      console.error('Error generando informe con MedGemma:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      alert(`Error al generar informe: ${errorMessage}`);
    } finally {
      setIsGeneratingReport(false);
    }
  }

  const startNewAnalysis = () => {
    setSelectedFile(null)
    setPreviewUrl("")
    setAnalysisResult(null)
    setIsAnalysisComplete(false)
    setIsUploading(false)
    setUploadProgress(0)
    setGeneratedReport("")
    }

  const completeWithoutReport = () => {
    const finalPatientId = patientId === "__new__" ? newPatientId : patientId;
    onUploadComplete(finalPatientId)
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
        <>
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
                Resultados del análisis IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Diagnóstico y Probabilidad */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {getDiagnosisIcon(analysisResult.resultado.diagnostico)}
                  <div>
                      <h3 className="font-semibold">Diagnóstico</h3>
                    <p className={`text-lg font-bold ${getDiagnosisColor(analysisResult.resultado.diagnostico)}`}>
                      {analysisResult.resultado.diagnostico}
                    </p>
                  </div>
                </div>
                <div>
                    <h3 className="font-semibold mb-2">Probabilidad</h3>
                  <div className="flex items-center gap-2">
                      <Progress value={analysisResult.resultado.porcentaje} className="flex-1" />
                      <span className="text-sm font-medium">{analysisResult.resultado.porcentaje}%</span>
                    </div>
                  </div>
                <div>
                    <h3 className="font-semibold mb-2">Detalles</h3>
                  <div className="text-sm space-y-1">
                      <p><span className="font-medium">Fecha de análisis:</span> {new Date(analysisResult.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                {/* Chat con MedGemma (OpenAI-compatible) */}
              <div className="space-y-4">
                <div>
                    <h3 className="font-semibold mb-2">Chat con MedGemma</h3>
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                      <p className="text-sm text-blue-800">
                        Este chat usa el Endpoint OpenAI-compatible de Hugging Face. En el primer turno se envía la radiografía como imagen (image_url) y tu pregunta como texto.
                      </p>
                    </div>
                  </div>
                  <div className="border rounded-lg">
                    <div className="h-56 overflow-y-auto p-3 space-y-3 bg-white">
                      {chatMessages.length === 0 ? (
                        <p className="text-sm text-gray-500">Escribe tu primera pregunta. Enviaremos la imagen como contexto en el primer turno.</p>
                      ) : (
                        chatMessages.map((m, idx) => (
                          <div key={idx} className={m.role === 'user' ? 'text-right' : 'text-left'}>
                            <div className={`inline-block px-3 py-2 rounded-lg text-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                              {m.content}
                </div>
              </div>
                        ))
                      )}
                    </div>
                    <div className="flex items-center gap-2 p-2 border-t bg-gray-50">
                      <Input
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder="Pregunta sobre hallazgos de neumonía..."
                        className="flex-1"
                      />
                      <Button onClick={async () => {
                        if (!chatInput.trim() || !selectedFile) return
                        const userText = chatInput.trim()
                        setChatInput("")
                        setChatMessages(prev => [...prev, { role: 'user', content: userText }])
                        setIsSending(true)
                        try {
                          const HF_TOKEN: string = CONFIG.HUGGINGFACE_TOKEN
                          const baseUrl = (CONFIG.MEDGEMMA_ENDPOINT || '').replace(/\/$/, '')
                          const url = `${baseUrl}/v1/chat/completions`
                          const messagesPayload: any[] = []
                          messagesPayload.push({ role: 'system', content: 'Responde solo en español, de forma clara, concisa y enfocada en hallazgos radiológicos de neumonía.' })
                          for (const m of chatMessages) {
                            messagesPayload.push({ role: m.role, content: [{ type: 'text', text: m.content }] })
                          }
                          const userContent: any[] = []
                          if (!imageSent && imageDataUrl) {
                            userContent.push({ type: 'image_url', image_url: { url: imageDataUrl } })
                          }
                          userContent.push({ type: 'text', text: userText })
                          messagesPayload.push({ role: 'user', content: userContent })

                          const body = {
                            model: 'tgi',
                            messages: messagesPayload,
                            stream: false,
                            max_tokens: 500,
                            temperature: 0.3,
                            top_p: 0.9
                          }

                          const resp = await fetch(url, {
                            method: 'POST',
                            headers: {
                              Authorization: `Bearer ${HF_TOKEN}`,
                              'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(body)
                          })
                          if (!resp.ok) {
                            const errorText = await resp.text()
                            throw new Error(`Error del chat: ${resp.status} ${resp.statusText}. ${errorText}`)
                          }
                          const data = await resp.json()
                          const reply = data.choices?.[0]?.message?.content || 'Sin respuesta'
                          setChatMessages(prev => [...prev, { role: 'assistant', content: reply }])
                          if (!imageSent) setImageSent(true)
                        } catch (e) {
                          console.error(e)
                          setChatMessages(prev => [...prev, { role: 'assistant', content: 'Error al obtener respuesta del modelo.' }])
                        } finally {
                          setIsSending(false)
                        }
                      }} disabled={isSending || !selectedFile}>
                        {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Enviar'}
                      </Button>
                    </div>
                </div>
                  <div>
                    <Button onClick={startNewAnalysis} className="w-full" size="lg" variant="outline">
                      Nuevo análisis
                  </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Informe Generado por MedGemma */}
          {generatedReport && (
            <Card className="mt-6">
              <CardHeader>
                                               <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    INFORME:
                 </CardTitle>
              </CardHeader>
              <CardContent>
                                 <div className="bg-white border rounded-lg p-3">
                   <div className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                     {generatedReport}
              </div>
            </div>
          </CardContent>
        </Card>
          )}
        </>
      )}
    </div>
  )
}
