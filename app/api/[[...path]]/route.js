import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import axios from 'axios'

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

// Import Coqui TTS integration
import { spawn } from 'child_process'
import fs from 'fs'
import path from 'path'

// Coqui TTS integration with fallback to mock audio
async function generateVoiceover(text, voiceModel = 'tacotron2_ljspeech', audioFormat = 'wav') {
  try {
    console.log(`Generating voiceover with model: ${voiceModel}, format: ${audioFormat}`)
    
    // Call Python TTS script
    const result = await callCoquiTTS(text, voiceModel, audioFormat)
    
    if (result.success && result.audio_data) {
      console.log(`✅ TTS generation successful: ${result.audio_data.length} bytes, fallback: ${result.fallback_used}`)
      return {
        audioBuffer: Buffer.from(result.audio_data, 'base64'),
        success: true,
        fallback_used: result.fallback_used,
        model_used: result.model_used,
        format: result.format,
        mime_type: result.mime_type,
        duration_estimate: result.duration_estimate,
        error: result.error
      }
    } else {
      throw new Error(result.error || 'TTS generation failed')
    }
  } catch (error) {
    console.error('Error in generateVoiceover:', error)
    
    // Fallback to mock audio
    console.log('Using fallback mock audio generation')
    const mockAudioBuffer = generateMockAudio(text)
    
    return {
      audioBuffer: mockAudioBuffer,
      success: true,
      fallback_used: true,
      model_used: 'mock_audio',
      format: 'wav',
      mime_type: 'audio/wav',
      duration_estimate: Math.max(3, Math.min(30, text.split(' ').length * 0.4)),
      error: error.message
    }
  }
}

// Call Coqui TTS Python script
function callCoquiTTS(text, voiceModel, audioFormat) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
import json
import base64
sys.path.append('/app/lib')
from coqui_tts import generate_coqui_voice

try:
    text = sys.argv[1]
    voice_model = sys.argv[2] if len(sys.argv) > 2 else 'tacotron2_ljspeech'
    audio_format = sys.argv[3] if len(sys.argv) > 3 else 'wav'
    
    result = generate_coqui_voice(text, voice_model, audio_format)
    
    # Convert binary data to base64 for JSON transport
    if result['audio_data']:
        result['audio_data'] = base64.b64encode(result['audio_data']).decode('utf-8')
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`
    
    const pythonProcess = spawn('python', ['-c', pythonScript, text, voiceModel, audioFormat])
    
    let stdout = ''
    let stderr = ''
    
    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })
    
    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout.trim())
          resolve(result)
        } catch (e) {
          reject(new Error(`Failed to parse TTS result: ${e.message}`))
        }
      } else {
        reject(new Error(`Python TTS process failed with code ${code}: ${stderr}`))
      }
    })
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to spawn Python process: ${error.message}`))
    })
  })
}

// Enhanced mock audio generation (fallback)
function generateMockAudio(text) {
  try {
    // Estimate duration based on text length
    const wordCount = text.split(' ').length
    const durationSeconds = Math.max(3, Math.min(30, wordCount * 0.4))
    const sampleRate = 22050
    const samples = Math.floor(durationSeconds * sampleRate)
    
    // Create WAV header
    const wavHeader = Buffer.alloc(44)
    
    // RIFF header
    wavHeader.write('RIFF', 0, 'ascii')
    wavHeader.writeUInt32LE(36 + samples * 2, 4)
    wavHeader.write('WAVE', 8, 'ascii')
    
    // fmt chunk
    wavHeader.write('fmt ', 12, 'ascii')
    wavHeader.writeUInt32LE(16, 16)  // chunk size
    wavHeader.writeUInt16LE(1, 20)   // audio format (PCM)
    wavHeader.writeUInt16LE(1, 22)   // num channels
    wavHeader.writeUInt32LE(sampleRate, 24)
    wavHeader.writeUInt32LE(sampleRate * 2, 28)  // byte rate
    wavHeader.writeUInt16LE(2, 32)   // block align
    wavHeader.writeUInt16LE(16, 34)  // bits per sample
    
    // data chunk
    wavHeader.write('data', 36, 'ascii')
    wavHeader.writeUInt32LE(samples * 2, 40)
    
    // Generate audio data with multiple frequencies
    const audioData = Buffer.alloc(samples * 2)
    for (let i = 0; i < samples; i++) {
      const t = i / sampleRate
      const freq1 = 220 // A3
      const freq2 = 330 // E4
      const freq3 = 440 // A4
      
      const sample = (
        0.3 * Math.sin(2 * Math.PI * freq1 * t) +
        0.2 * Math.sin(2 * Math.PI * freq2 * t) +
        0.1 * Math.sin(2 * Math.PI * freq3 * t)
      )
      
      // Apply fade in/out
      const fadeLength = Math.floor(0.1 * sampleRate)
      let amplitude = 1
      if (i < fadeLength) {
        amplitude = i / fadeLength
      } else if (i > samples - fadeLength) {
        amplitude = (samples - i) / fadeLength
      }
      
      const value = Math.round(sample * amplitude * 16000)
      audioData.writeInt16LE(Math.max(-32768, Math.min(32767, value)), i * 2)
    }
    
    return Buffer.concat([wavHeader, audioData])
  } catch (error) {
    console.error('Error generating mock audio:', error)
    // Return minimal WAV as absolute fallback
    return Buffer.from([
      0x52, 0x49, 0x46, 0x46, 0x44, 0x10, 0x00, 0x00,
      0x57, 0x41, 0x56, 0x45, 0x66, 0x6d, 0x74, 0x20,
      0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
      0x44, 0xac, 0x00, 0x00, 0x88, 0x58, 0x01, 0x00,
      0x02, 0x00, 0x10, 0x00, 0x64, 0x61, 0x74, 0x61,
      0x00, 0x10, 0x00, 0x00, ...Buffer.alloc(4096, 0)
    ])
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

  console.log(`[API] ${method} ${route} - params:`, params, 'path:', path)

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
        const voiceModel = body.voice_model || 'tacotron2_ljspeech'
        const audioFormat = body.audio_format || 'wav'
        
        const result = await generateVoiceover(body.text, voiceModel, audioFormat)
        
        // Save to database for history
        const voiceoverRecord = {
          id: uuidv4(),
          text: body.text,
          voice_model: voiceModel,
          audio_format: audioFormat,
          fallback_used: result.fallback_used,
          model_used: result.model_used,
          duration_estimate: result.duration_estimate,
          created_at: new Date()
        }
        
        await db.collection('voiceovers').insertOne(voiceoverRecord)
        
        // Return audio as response
        return new NextResponse(result.audioBuffer, {
          status: 200,
          headers: {
            'Content-Type': result.mime_type,
            'Content-Length': result.audioBuffer.length.toString(),
            'X-TTS-Model-Used': result.model_used,
            'X-TTS-Fallback-Used': result.fallback_used.toString(),
            'X-TTS-Format': result.format,
            'X-TTS-Duration': result.duration_estimate.toString(),
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Expose-Headers': 'X-TTS-Model-Used, X-TTS-Fallback-Used, X-TTS-Format, X-TTS-Duration'
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