// Mock data for demonstration

export interface Study {
  patientId: string
  studyDate: string
  diagnosis: string
  confidence: number
  imagePath: string
}

export interface Patient {
  patientId: string
  name: string
  studies: Study[]
}

export const mockPatients: Patient[] = [
  {
    patientId: "P1234",
    name: "John Smith",
    studies: [
      {
        patientId: "P1234",
        studyDate: "2025-01-17",
        diagnosis: "Pneumonia Detected",
        confidence: 0.87,
        imagePath: "/uploads/p1234_20250117.png",
      },
      {
        patientId: "P1234",
        studyDate: "2025-01-10",
        diagnosis: "Normal",
        confidence: 0.23,
        imagePath: "/uploads/p1234_20250110.png",
      },
      {
        patientId: "P1234",
        studyDate: "2024-12-15",
        diagnosis: "Possible Pneumonia",
        confidence: 0.65,
        imagePath: "/uploads/p1234_20241215.png",
      },
    ],
  },
  {
    patientId: "P5678",
    name: "Maria Garcia",
    studies: [
      {
        patientId: "P5678",
        studyDate: "2025-01-16",
        diagnosis: "Normal",
        confidence: 0.18,
        imagePath: "/uploads/p5678_20250116.png",
      },
      {
        patientId: "P5678",
        studyDate: "2025-01-08",
        diagnosis: "Pneumonia Detected",
        confidence: 0.92,
        imagePath: "/uploads/p5678_20250108.png",
      },
    ],
  },
  {
    patientId: "P9012",
    name: "Robert Johnson",
    studies: [
      {
        patientId: "P9012",
        studyDate: "2025-01-15",
        diagnosis: "Possible Pneumonia",
        confidence: 0.71,
        imagePath: "/uploads/p9012_20250115.png",
      },
    ],
  },
  {
    patientId: "P3456",
    name: "Emily Chen",
    studies: [
      {
        patientId: "P3456",
        studyDate: "2025-01-14",
        diagnosis: "Normal",
        confidence: 0.15,
        imagePath: "/uploads/p3456_20250114.png",
      },
      {
        patientId: "P3456",
        studyDate: "2025-01-07",
        diagnosis: "Normal",
        confidence: 0.28,
        imagePath: "/uploads/p3456_20250107.png",
      },
      {
        patientId: "P3456",
        studyDate: "2024-12-20",
        diagnosis: "Pneumonia Detected",
        confidence: 0.89,
        imagePath: "/uploads/p3456_20241220.png",
      },
    ],
  },
]

// Helper function to find patient by ID
export const findPatientById = (patientId: string): Patient | undefined => {
  return mockPatients.find((patient) => patient.patientId === patientId)
}

// Helper function to add new study to existing patient or create new patient
export const addStudyToPatient = (study: Study, patientName?: string): void => {
  const existingPatient = findPatientById(study.patientId)

  if (existingPatient) {
    // Add to existing patient and sort by date (newest first)
    existingPatient.studies.unshift(study)
    existingPatient.studies.sort((a, b) => new Date(b.studyDate).getTime() - new Date(a.studyDate).getTime())
  } else {
    // Create new patient
    const newPatient: Patient = {
      patientId: study.patientId,
      name: patientName || `Patient ${study.patientId}`, // Use provided name or default
      studies: [study],
    }
    mockPatients.push(newPatient)
  }
}

// Helper function to create a new patient with pending analysis
export const createNewPatientWithPendingStudy = (patientId: string, patientName: string, studyDate: string, imagePath: string): void => {
  const newStudy: Study = {
    patientId,
    studyDate,
    diagnosis: "Sin Análisis", // Initial state
    confidence: 0,
    imagePath,
  }
  
  addStudyToPatient(newStudy, patientName)
}
