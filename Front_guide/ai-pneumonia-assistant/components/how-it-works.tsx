"use client"

import { Upload, Brain, FileText, Users } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: "Upload X-Ray",
      description: "Upload chest X-ray images with patient information and study date.",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Our AI model analyzes the image for signs of pneumonia with confidence scoring.",
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      icon: Users,
      title: "Patient Studies",
      description: "View organized patient studies grouped by patient with chronological ordering.",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      icon: FileText,
      title: "Generate Report",
      description: "Create detailed medical reports using MedGemma AI for clinical documentation.",
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
  ]

  return (
    <Card className="mt-12">
      <CardHeader>
        <CardTitle className="text-center text-2xl">How It Works</CardTitle>
        <p className="text-center text-gray-600">
          Our AI-powered pneumonia detection system streamlines the diagnostic workflow
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${step.bgColor} flex items-center justify-center`}>
                <step.icon className={`h-8 w-8 ${step.color}`} />
              </div>
              <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
              <p className="text-sm text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
