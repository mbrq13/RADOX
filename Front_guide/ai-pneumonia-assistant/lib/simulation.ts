// Simulación completa de análisis y generación de reportes

export interface AnalysisResult {
  diagnosis: string
  confidence: number
  imagePath: string
}

// Simular análisis de imagen con IA
export async function simulateAnalysis(file: File): Promise<AnalysisResult> {
  // Simular tiempo de procesamiento
  await new Promise((resolve) => setTimeout(resolve, 2000 + Math.random() * 2000))

  // Generar resultados aleatorios pero realistas
  const scenarios = [
    {
      diagnosis: "Neumonía Detectada",
      confidence: Math.floor(75 + Math.random() * 20), // 75-95%
    },
    {
      diagnosis: "Posible Neumonía",
      confidence: Math.floor(60 + Math.random() * 15), // 60-75%
    },
    {
      diagnosis: "Sin Signos de Neumonía",
      confidence: Math.floor(20 + Math.random() * 40), // 20-60%
    },
    {
      diagnosis: "Radiografía Normal",
      confidence: Math.floor(10 + Math.random() * 30), // 10-40%
    },
  ]

  const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)]

  return {
    ...randomScenario,
    imagePath: `processed_${file.name}_${Date.now()}.jpg`,
  }
}

// Simular generación de reporte médico
export async function simulateReportGeneration(result: AnalysisResult): Promise<string> {
  // Simular tiempo de generación
  await new Promise((resolve) => setTimeout(resolve, 3000 + Math.random() * 2000))

  const currentDate = new Date().toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  const currentTime = new Date().toLocaleTimeString("es-ES")

  // Generar reporte basado en el diagnóstico
  let reportContent = ""

  if (result.diagnosis.toLowerCase().includes("neumonía detectada")) {
    reportContent = `
REPORTE MÉDICO - ANÁLISIS DE RADIOGRAFÍA TORÁCICA
================================================================

INFORMACIÓN DEL PACIENTE:
- Fecha de análisis: ${currentDate}
- Hora: ${currentTime}
- Tipo de estudio: Radiografía de tórax PA
- Método de análisis: Inteligencia Artificial MedGemma-4B

HALLAZGOS RADIOLÓGICOS:
El análisis automatizado mediante inteligencia artificial ha identificado patrones compatibles con neumonía.

DIAGNÓSTICO IA: ${result.diagnosis}
NIVEL DE CONFIANZA: ${result.confidence}%

DESCRIPCIÓN DETALLADA:
- Se observan opacidades pulmonares sugestivas de consolidación
- Patrón de infiltrado compatible con proceso infeccioso
- Distribución típica de neumonía bacteriana
- No se evidencian signos de derrame pleural significativo

RECOMENDACIONES:
1. EVALUACIÓN MÉDICA URGENTE requerida
2. Correlación clínica con síntomas del paciente
3. Considerar estudios complementarios (hemograma, PCR, cultivos)
4. Iniciar tratamiento antibiótico según protocolo médico
5. Seguimiento radiológico en 48-72 horas

NOTA IMPORTANTE:
Este análisis ha sido realizado mediante inteligencia artificial y debe ser 
validado por un radiólogo certificado. No sustituye el criterio médico profesional.

LIMITACIONES DEL ESTUDIO:
- Análisis basado únicamente en imagen radiográfica
- Requiere correlación con historia clínica
- Sensibilidad del sistema: 89.2%
- Especificidad del sistema: 92.7%

Generado automáticamente por Sistema IA MedGemma
Fecha de generación: ${currentDate} - ${currentTime}
    `
  } else if (result.diagnosis.toLowerCase().includes("posible")) {
    reportContent = `
REPORTE MÉDICO - ANÁLISIS DE RADIOGRAFÍA TORÁCICA
================================================================

INFORMACIÓN DEL PACIENTE:
- Fecha de análisis: ${currentDate}
- Hora: ${currentTime}
- Tipo de estudio: Radiografía de tórax PA
- Método de análisis: Inteligencia Artificial MedGemma-4B

HALLAZGOS RADIOLÓGICOS:
El análisis automatizado identifica cambios sutiles que podrían ser compatibles con neumonía incipiente.

DIAGNÓSTICO IA: ${result.diagnosis}
NIVEL DE CONFIANZA: ${result.confidence}%

DESCRIPCIÓN DETALLADA:
- Opacidades tenues en campos pulmonares
- Patrón intersticial levemente aumentado
- Posibles infiltrados en fase inicial
- Silueta cardíaca dentro de límites normales

RECOMENDACIONES:
1. Evaluación médica para correlación clínica
2. Seguimiento estrecho de síntomas respiratorios
3. Considerar repetir radiografía en 24-48 horas si persisten síntomas
4. Vigilar signos de progresión: fiebre, tos, disnea
5. Mantener medidas de soporte general

INTERPRETACIÓN:
Los hallazgos sugieren la posibilidad de un proceso inflamatorio pulmonar 
en etapa temprana. Se requiere evaluación médica para determinar la 
necesidad de intervención terapéutica.

SEGUIMIENTO RECOMENDADO:
- Control clínico en 24-48 horas
- Nueva radiografía si empeoramiento clínico
- Considerar estudios adicionales según evolución

Generado automáticamente por Sistema IA MedGemma
Fecha de generación: ${currentDate} - ${currentTime}
    `
  } else {
    reportContent = `
REPORTE MÉDICO - ANÁLISIS DE RADIOGRAFÍA TORÁCICA
================================================================

INFORMACIÓN DEL PACIENTE:
- Fecha de análisis: ${currentDate}
- Hora: ${currentTime}
- Tipo de estudio: Radiografía de tórax PA
- Método de análisis: Inteligencia Artificial MedGemma-4B

HALLAZGOS RADIOLÓGICOS:
El análisis automatizado no identifica signos radiológicos sugestivos de neumonía.

DIAGNÓSTICO IA: ${result.diagnosis}
NIVEL DE CONFIANZA: ${result.confidence}%

DESCRIPCIÓN DETALLADA:
- Campos pulmonares con transparencia conservada
- Ausencia de consolidaciones o infiltrados
- Silueta cardiomediastínica normal
- Diafragmas bien definidos
- No se observan signos de derrame pleural

INTERPRETACIÓN:
La radiografía de tórax presenta características dentro de parámetros normales 
según el análisis de inteligencia artificial. No se identifican signos 
radiológicos compatibles con neumonía.

RECOMENDACIONES:
1. Resultado tranquilizador desde el punto de vista radiológico
2. Correlacionar con síntomas clínicos del paciente
3. Si persisten síntomas respiratorios, considerar otras causas
4. Mantener seguimiento clínico habitual
5. Repetir estudios solo si hay cambios en el cuadro clínico

NOTA IMPORTANTE:
Un resultado normal no excluye completamente patología pulmonar, 
especialmente en fases muy tempranas de infección. La correlación 
clínica siempre es fundamental.

SEGUIMIENTO:
- Control médico según síntomas
- Nueva evaluación si aparecen signos de alarma
- Mantener medidas preventivas generales

Generado automáticamente por Sistema IA MedGemma
Fecha de generación: ${currentDate} - ${currentTime}
    `
  }

  return reportContent.trim()
}

// Simular diferentes escenarios de error (opcional)
export function simulateRandomError(): never {
  const errors = [
    "Error de conexión con el servidor de análisis",
    "Imagen no válida para análisis",
    "Tiempo de espera agotado en el procesamiento",
    "Error interno del modelo de IA",
  ]

  throw new Error(errors[Math.floor(Math.random() * errors.length)])
}
