import { NextResponse } from 'next/server'

// Helper function to handle CORS
function handleCORS(response) {
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  return response
}

// OPTIONS handler for CORS
export async function OPTIONS() {
  return handleCORS(new NextResponse(null, { status: 200 }))
}

// GET handler for root API endpoint
export async function GET() {
  return handleCORS(NextResponse.json({ message: "AI Business Video Script & Voiceover Generator API" }))
}

// POST handler for root API endpoint
export async function POST() {
  return handleCORS(NextResponse.json({ message: "AI Business Video Script & Voiceover Generator API" }))
}