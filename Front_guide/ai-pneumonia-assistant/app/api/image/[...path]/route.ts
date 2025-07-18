// Proxy route to serve images from the backend
import { type NextRequest, NextResponse } from "next/server"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001"

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  try {
    const imagePath = params.path.join("/")
    const imageUrl = `${API_BASE_URL}/uploads/${imagePath}`

    const response = await fetch(imageUrl)

    if (!response.ok) {
      return new NextResponse("Image not found", { status: 404 })
    }

    const imageBuffer = await response.arrayBuffer()
    const contentType = response.headers.get("content-type") || "image/jpeg"

    return new NextResponse(imageBuffer, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=3600",
      },
    })
  } catch (error) {
    console.error("Error serving image:", error)
    return new NextResponse("Internal Server Error", { status: 500 })
  }
}
