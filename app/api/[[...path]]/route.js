import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import axios from 'axios'
import { HfInference } from '@huggingface/inference'
import { GoogleGenerativeAI } from '@google/genai'

// Initialize clients
const hf = new HfInference(process.env.HUGGINGFACE_API_KEY)
const genai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

// MongoDB connection
let client
let db

async function connectToMongo() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    db = client.db(process.env.DB_NAME)
  }
  return db
}

// Helper function to handle CORS
function handleCORS(response) {
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  return response
}

// Generate avatar image using HuggingFace
async function generateAvatarImage(description, style = 'realistic') {
  try {
    const prompt = `A ${style} portrait of ${description}, professional headshot, high quality, detailed face, looking at camera, neutral background`
    
    const response = await hf.textToImage({
      model: 'runwayml/stable-diffusion-v1-5',
      inputs: prompt,
      parameters: {
        width: 512,
        height: 512,
        guidance_scale: 7.5,
        num_inference_steps: 50
      }
    })
    
    // Convert blob to buffer
    const arrayBuffer = await response.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    
    // Convert to base64 for storage
    const base64Image = buffer.toString('base64')
    
    return base64Image
  } catch (error) {
    console.error('Error generating avatar image:', error)
    throw new Error('Failed to generate avatar image')
  }
}

// Generate talking head video using HuggingFace SadTalker
async function generateTalkingVideo(imageBase64, audioText, quality = 'basic') {
  try {
    // For basic quality, we'll use a simpler approach with HuggingFace Spaces
    let modelEndpoint
    
    switch (quality) {
      case 'basic':
        // Use free SadTalker model
        modelEndpoint = 'vinthony/SadTalker'
        break
      case 'enhanced':
        // Use Wav2Lip model for better lip sync
        modelEndpoint = 'freddyaboulton/wav2lip-GFPGAN'
        break
      case 'ultra':
        // Use combination of models for best quality
        modelEndpoint = 'KwaiVGI/LivePortrait'
        break
      default:
        modelEndpoint = 'vinthony/SadTalker'
    }
    
    // First generate audio from text using a TTS model
    const audioResponse = await hf.textToSpeech({
      model: 'microsoft/speecht5_tts',
      inputs: audioText
    })
    
    const audioBuffer = await audioResponse.arrayBuffer()
    const audioBase64 = Buffer.from(audioBuffer).toString('base64')
    
    // For now, we'll return a mock video response as HuggingFace Spaces integration
    // requires more complex setup. In a production environment, you would:
    // 1. Upload image and audio to HuggingFace Space
    // 2. Process through the SadTalker/Wav2Lip pipeline
    // 3. Retrieve the generated video
    
    // Mock video data (in production, this would be the actual generated video)
    const mockVideoData = {
      videoUrl: `data:video/mp4;base64,${generateMockVideoBase64()}`,
      duration: Math.floor(audioText.length / 10), // Estimate duration
      quality: quality,
      audioBase64: audioBase64
    }
    
    return mockVideoData
  } catch (error) {
    console.error('Error generating talking video:', error)
    throw new Error('Failed to generate talking video')
  }
}

// Generate background image using OpenRouter API
async function generateBackground(description, style = 'professional') {
  try {
    const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
      model: 'meta-llama/llama-3.1-8b-instruct:free', // Free model
      messages: [
        {
          role: 'system',
          content: 'You are an expert at creating detailed prompts for image generation. Create a detailed prompt for generating a background image.'
        },
        {
          role: 'user',
          content: `Create a detailed prompt for generating a ${style} background for ${description}`
        }
      ],
      max_tokens: 200
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json'
      }
    })
    
    const backgroundPrompt = response.data.choices[0]?.message?.content || `${style} background for ${description}`
    
    // Generate background image using HuggingFace
    const backgroundResponse = await hf.textToImage({
      model: 'runwayml/stable-diffusion-v1-5',
      inputs: backgroundPrompt,
      parameters: {
        width: 1024,
        height: 576,
        guidance_scale: 7.5
      }
    })
    
    const arrayBuffer = await backgroundResponse.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    return buffer.toString('base64')
  } catch (error) {
    console.error('Error generating background:', error)
    // Return a simple gradient background as fallback
    return generateSimpleBackground()
  }
}

// Generate simple gradient background as fallback  
function generateSimpleBackground() {
  // This would generate a simple gradient background
  // For now, returning a placeholder
  return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
}

// Generate mock video base64 (placeholder)
function generateMockVideoBase64() {
  // This is a placeholder. In production, this would be the actual video data
  return 'UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSmIn/vr5ZIYCRxxtdbjqHsQC0yfzt+2lxgKF2mxzty1rJ2wlzP8ek='
}

// Groq API client
async function generateScript(prompt, options = {}) {
  const defaultOptions = {
    model: "llama-3.3-70b-versatile",
    temperature: 0.7,
    max_tokens: 1000
  }
  
  const config = { ...defaultOptions, ...options }
  
  try {
    const response = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
      model: config.model,
      messages: [
        {
          role: "system",
          content: `You are a professional business video script writer. Create engaging, concise, and compelling scripts for business videos that are perfect for voiceover. 

Guidelines:
- Keep scripts between 60-90 seconds when spoken
- Use clear, professional language
- Include a strong hook at the beginning
- Structure: Hook → Problem → Solution → Benefits → Call to Action
- Write in a conversational tone suitable for voiceover
- Include natural pauses and emphasis markers where appropriate
- Make it engaging and persuasive for business audiences`
        },
        {
          role: "user",
          content: `Create a compelling business video script based on this description: ${prompt}`
        }
      ],
      temperature: config.temperature,
      max_tokens: config.max_tokens
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      }
    })
    
    return response.data.choices[0]?.message?.content
  } catch (error) {
    console.error('Error generating script:', error.response?.data || error.message)
    throw new Error('Failed to generate script')
  }
}

// Bark TTS integration (Mock for now - will need Docker setup)
async function generateVoiceover(text, voiceStyle = 'professional') {
  try {
    // For MVP, we'll create a mock audio response
    // In production, this would call the Bark TTS Docker container
    
    // Mock audio generation - creating a simple WAV header for testing
    const mockAudioBuffer = Buffer.alloc(1024, 0) // Empty buffer for now
    
    // Add WAV header (simplified)
    const wavHeader = Buffer.from([
      0x52, 0x49, 0x46, 0x46, // "RIFF"
      0x00, 0x04, 0x00, 0x00, // File size (placeholder)
      0x57, 0x41, 0x56, 0x45, // "WAVE"
      0x66, 0x6d, 0x74, 0x20, // "fmt "
      0x10, 0x00, 0x00, 0x00, // Subchunk size
      0x01, 0x00,             // Audio format (PCM)
      0x01, 0x00,             // Number of channels
      0x44, 0xac, 0x00, 0x00, // Sample rate (44100)
      0x88, 0x58, 0x01, 0x00, // Byte rate
      0x02, 0x00,             // Block align
      0x10, 0x00,             // Bits per sample
      0x64, 0x61, 0x74, 0x61, // "data"
      0x00, 0x04, 0x00, 0x00  // Data size
    ])
    
    return Buffer.concat([wavHeader, mockAudioBuffer])
  } catch (error) {
    console.error('Error generating voiceover:', error)
    throw new Error('Failed to generate voiceover')
  }
}

// OPTIONS handler for CORS
export async function OPTIONS() {
  return handleCORS(new NextResponse(null, { status: 200 }))
}

// Route handler function
async function handleRoute(request, { params }) {
  const { path = [] } = params
  const route = `/${path.join('/')}`
  const method = request.method

  try {
    const db = await connectToMongo()

    // Root endpoint - GET /api/
    if (route === '/' && method === 'GET') {
      return handleCORS(NextResponse.json({ message: "AI Business Video Script & Voiceover Generator API" }))
    }

    // Generate Script endpoint - POST /api/generate-script
    if (route === '/generate-script' && method === 'POST') {
      const body = await request.json()
      
      if (!body.prompt) {
        return handleCORS(NextResponse.json(
          { error: "Prompt is required" }, 
          { status: 400 }
        ))
      }

      try {
        const script = await generateScript(body.prompt, body.options)
        
        // Save to database for history
        const scriptRecord = {
          id: uuidv4(),
          prompt: body.prompt,
          script: script,
          created_at: new Date(),
          options: body.options || {}
        }
        
        await db.collection('scripts').insertOne(scriptRecord)
        
        return handleCORS(NextResponse.json({ script }))
      } catch (error) {
        console.error('Script generation error:', error)
        return handleCORS(NextResponse.json(
          { error: error.message || 'Failed to generate script' }, 
          { status: 500 }
        ))
      }
    }

    // Generate Voiceover endpoint - POST /api/generate-voiceover
    if (route === '/generate-voiceover' && method === 'POST') {
      const body = await request.json()
      
      if (!body.text) {
        return handleCORS(NextResponse.json(
          { error: "Text is required" }, 
          { status: 400 }
        ))
      }

      try {
        const audioBuffer = await generateVoiceover(body.text, body.voice_style)
        
        // Save to database for history
        const voiceoverRecord = {
          id: uuidv4(),
          text: body.text,
          voice_style: body.voice_style || 'professional',
          created_at: new Date()
        }
        
        await db.collection('voiceovers').insertOne(voiceoverRecord)
        
        // Return audio as response
        return new NextResponse(audioBuffer, {
          status: 200,
          headers: {
            'Content-Type': 'audio/wav',
            'Content-Length': audioBuffer.length.toString(),
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          }
        })
      } catch (error) {
        console.error('Voiceover generation error:', error)
        return handleCORS(NextResponse.json(
          { error: error.message || 'Failed to generate voiceover' }, 
          { status: 500 }
        ))
      }
    }

    // Get Scripts History endpoint - GET /api/scripts
    if (route === '/scripts' && method === 'GET') {
      const scripts = await db.collection('scripts')
        .find({})
        .sort({ created_at: -1 })
        .limit(50)
        .toArray()

      // Remove MongoDB's _id field from response
      const cleanedScripts = scripts.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedScripts))
    }

    // Get Voiceovers History endpoint - GET /api/voiceovers
    if (route === '/voiceovers' && method === 'GET') {
      const voiceovers = await db.collection('voiceovers')
        .find({})
        .sort({ created_at: -1 })
        .limit(50)
        .toArray()

      // Remove MongoDB's _id field from response
      const cleanedVoiceovers = voiceovers.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedVoiceovers))
    }

    // Status endpoints - POST /api/status (keeping existing functionality)
    if (route === '/status' && method === 'POST') {
      const body = await request.json()
      
      if (!body.client_name) {
        return handleCORS(NextResponse.json(
          { error: "client_name is required" }, 
          { status: 400 }
        ))
      }

      const statusObj = {
        id: uuidv4(),
        client_name: body.client_name,
        timestamp: new Date()
      }

      await db.collection('status_checks').insertOne(statusObj)
      return handleCORS(NextResponse.json(statusObj))
    }

    // Status endpoints - GET /api/status (keeping existing functionality)
    if (route === '/status' && method === 'GET') {
      const statusChecks = await db.collection('status_checks')
        .find({})
        .limit(1000)
        .toArray()

      // Remove MongoDB's _id field from response
      const cleanedStatusChecks = statusChecks.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedStatusChecks))
    }

    // Route not found
    return handleCORS(NextResponse.json(
      { error: `Route ${route} not found` }, 
      { status: 404 }
    ))

  } catch (error) {
    console.error('API Error:', error)
    return handleCORS(NextResponse.json(
      { error: "Internal server error" }, 
      { status: 500 }
    ))
  }
}

// Export all HTTP methods
export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute