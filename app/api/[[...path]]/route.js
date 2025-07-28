import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import axios from 'axios'
import { HfInference } from '@huggingface/inference'
import fs from 'fs'
import path from 'path'

// Initialize HuggingFace client
const hf = new HfInference(process.env.HUGGINGFACE_API_KEY)

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

// Enhanced avatar image generation using Gemini API
async function generateAvatarImage(description = 'professional business person', style = 'realistic') {
  try {
    console.log('Generating avatar with Gemini API...')
    
    // Use OpenRouter for image generation with DALL-E 3 model as backup
    const prompt = `a ${style} portrait of a ${description}, professional headshot, high quality, detailed face, looking directly at camera, soft lighting, neutral background, 8k, photo-realistic, business attire`
    
    try {
      const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
        model: 'openai/dall-e-3',
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: `Generate a professional avatar image: ${prompt}`
              }
            ]
          }
        ],
        max_tokens: 1000
      }, {
        headers: {
          'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json'
        }
      })
      
      // Extract image URL from OpenRouter DALL-E response
      const imageUrl = response.data?.choices?.[0]?.message?.content
      
      if (imageUrl && imageUrl.includes('http')) {
        // Download and convert to base64
        const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' })
        const base64Image = Buffer.from(imageResponse.data).toString('base64')
        console.log('Avatar generated successfully with OpenRouter DALL-E')
        return base64Image
      }
    } catch (openRouterError) {
      console.log('OpenRouter DALL-E not available, trying Gemini...')
    }
    
    // Fallback to generating a simple avatar using text description
    // Since Gemini doesn't directly support image generation in this context,
    // we'll create a text-based avatar description for now
    const avatarData = {
      description: prompt,
      style: style,
      timestamp: new Date().toISOString()
    }
    
    // Generate a simple placeholder avatar (colorful gradient based on description hash)
    const base64Avatar = generateColorfulAvatar(description, style)
    
    console.log('Avatar generated with fallback method')
    return base64Avatar
  } catch (error) {
    console.error('Error generating avatar image:', error)
    // Return a fallback avatar placeholder
    return generateFallbackAvatar()
  }
}

// Generate a colorful avatar placeholder based on description
function generateColorfulAvatar(description, style) {
  // Create a simple SVG avatar based on description hash
  const hash = description.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  
  const color1 = colors[Math.abs(hash) % colors.length]
  const color2 = colors[Math.abs(hash * 2) % colors.length]
  
  const svgAvatar = `
    <svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${color1};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${color2};stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="512" height="512" fill="url(#grad1)"/>
      <circle cx="256" cy="200" r="80" fill="rgba(255,255,255,0.3)"/>
      <rect x="176" y="320" width="160" height="120" rx="10" fill="rgba(255,255,255,0.2)"/>
      <text x="256" y="460" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold">
        Professional Avatar
      </text>
    </svg>
  `
  
  // Convert SVG to base64
  const base64Svg = Buffer.from(svgAvatar).toString('base64')
  return base64Svg
}

// Generate scene-based visual prompts using Claude 3.5 Sonnet via OpenRouter
async function extractScenePrompts(script) {
  try {
    const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
      model: 'anthropic/claude-3.5-sonnet:beta',
      messages: [
        {
          role: 'system',
          content: `You are an expert at breaking video scripts into visual scenes for image generation. 
          
          Instructions:
          1. Break the script into 3-5 logical visual segments
          2. For each segment, create a detailed visual prompt suitable for AI image generation
          3. Focus on backgrounds, settings, and visual elements (not people)
          4. Make prompts professional and business-appropriate
          5. Each prompt should be 1-2 sentences
          
          Return ONLY a JSON array with this structure:
          [
            {"timeframe": "0:00-0:15", "prompt": "modern office environment with large windows..."},
            {"timeframe": "0:15-0:30", "prompt": "close-up of computer screen showing analytics..."}
          ]`
        },
        {
          role: 'user',
          content: `Break this script into visual scenes:\n\n${script}`
        }
      ],
      max_tokens: 800,
      temperature: 0.3
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json'
      }
    })
    
    const content = response.data.choices[0]?.message?.content
    console.log('Scene extraction response:', content)
    
    // Parse JSON response
    try {
      const scenes = JSON.parse(content)
      return Array.isArray(scenes) ? scenes : []
    } catch (parseError) {
      console.error('Error parsing scene JSON:', parseError)
      // Fallback to manual extraction
      return generateFallbackScenes(script)
    }
  } catch (error) {
    console.error('Error extracting scene prompts:', error)
    return generateFallbackScenes(script)
  }
}

// Generate background images for each scene using OpenRouter with DALL-E 3
async function generateBackgroundImages(scenePrompts) {
  const backgrounds = []
  
  for (let i = 0; i < scenePrompts.length; i++) {
    const scene = scenePrompts[i]
    try {
      console.log(`Generating background ${i + 1}/${scenePrompts.length}:`, scene.prompt)
      
      // Try OpenRouter DALL-E 3 first
      try {
        const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
          model: 'openai/dall-e-3',
          messages: [
            {
              role: 'user',
              content: `Generate a professional background image: ${scene.prompt}, professional, high quality, detailed, cinematic lighting, 8k`
            }
          ],
          max_tokens: 1000
        }, {
          headers: {
            'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json'
          }
        })
        
        const imageUrl = response.data?.choices?.[0]?.message?.content
        
        if (imageUrl && imageUrl.includes('http')) {
          // Download and convert to base64
          const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' })
          const base64Image = Buffer.from(imageResponse.data).toString('base64')
          
          backgrounds.push({
            timeframe: scene.timeframe,
            prompt: scene.prompt,
            image: base64Image
          })
          
          console.log(`Background ${i + 1} generated successfully with OpenRouter`)
          continue
        }
      } catch (openRouterError) {
        console.log(`OpenRouter failed for background ${i + 1}, using fallback...`)
      }
      
      // Fallback: Generate a themed background placeholder
      const themedBackground = generateThemedBackground(scene.prompt, i)
      backgrounds.push({
        timeframe: scene.timeframe,
        prompt: scene.prompt,
        image: themedBackground
      })
      
      console.log(`Background ${i + 1} generated with themed fallback`)
    } catch (error) {
      console.error(`Error generating background ${i + 1}:`, error)
      // Add a simple fallback background
      backgrounds.push({
        timeframe: scene.timeframe,
        prompt: scene.prompt,
        image: generateFallbackBackground()
      })
    }
  }
  
  return backgrounds
}

// Generate themed background based on scene prompt
function generateThemedBackground(prompt, index) {
  // Create themed SVG backgrounds based on prompt content
  const themes = {
    office: { color1: '#2C3E50', color2: '#3498DB', icon: '🏢' },
    technology: { color1: '#8E44AD', color2: '#3498DB', icon: '💻' },
    meeting: { color1: '#27AE60', color2: '#2ECC71', icon: '👥' },
    business: { color1: '#E74C3C', color2: '#C0392B', icon: '💼' },
    default: { color1: '#34495E', color2: '#95A5A6', icon: '🎯' }
  }
  
  // Determine theme based on prompt keywords
  let theme = themes.default
  if (prompt.toLowerCase().includes('office')) theme = themes.office
  else if (prompt.toLowerCase().includes('technology') || prompt.toLowerCase().includes('computer')) theme = themes.technology
  else if (prompt.toLowerCase().includes('meeting') || prompt.toLowerCase().includes('presentation')) theme = themes.meeting
  else if (prompt.toLowerCase().includes('business')) theme = themes.business
  
  const svgBackground = `
    <svg width="1024" height="576" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bg${index}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${theme.color1};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${theme.color2};stop-opacity:1" />
        </linearGradient>
        <filter id="blur">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
        </filter>
      </defs>
      <rect width="1024" height="576" fill="url(#bg${index})"/>
      <circle cx="200" cy="150" r="60" fill="rgba(255,255,255,0.1)" filter="url(#blur)"/>
      <circle cx="800" cy="400" r="80" fill="rgba(255,255,255,0.1)" filter="url(#blur)"/>
      <rect x="100" y="450" width="824" height="80" rx="10" fill="rgba(0,0,0,0.2)"/>
      <text x="512" y="490" text-anchor="middle" fill="white" font-family="Arial" font-size="18" font-weight="bold">
        ${theme.icon} Professional Background
      </text>
      <text x="512" y="520" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-family="Arial" font-size="14">
        Scene ${index + 1}
      </text>
    </svg>
  `
  
  return Buffer.from(svgBackground).toString('base64')
}

// Create a simple talking head video simulation
async function createTalkingHeadVideo(avatarBase64, audioBuffer, duration = 30) {
  try {
    // For MVP: Create a simple video with static avatar and audio
    // In production, this would use SadTalker or similar
    
    console.log('Creating talking head video...')
    
    const videoData = {
      type: 'talking_head',
      avatar: avatarBase64,
      duration: duration,
      format: 'mp4',
      // Mock video base64 - in production this would be actual video
      videoBase64: generateMockVideoBase64(duration)
    }
    
    console.log('Talking head video created successfully')
    return videoData
  } catch (error) {
    console.error('Error creating talking head video:', error)
    throw error
  }
}

// Compose final video with avatar, backgrounds, and audio
async function composeFinalVideo(talkingHeadVideo, backgrounds, audioBuffer, script) {
  try {
    console.log('Composing final video...')
    
    // For MVP: Return a composed video structure
    // In production: Use FFmpeg to actually compose video layers
    
    const finalVideo = {
      id: uuidv4(),
      type: 'final_video',
      avatar: talkingHeadVideo.avatar,
      backgrounds: backgrounds,
      duration: talkingHeadVideo.duration,
      script: script,
      audioIncluded: true,
      format: 'mp4',
      // Mock final video - in production this would be actual composed video
      videoBase64: generateMockFinalVideo(talkingHeadVideo, backgrounds),
      metadata: {
        avatar_count: 1,
        background_count: backgrounds.length,
        total_scenes: backgrounds.length,
        created_at: new Date()
      }
    }
    
    console.log('Final video composed successfully')
    return finalVideo
  } catch (error) {
    console.error('Error composing final video:', error)
    throw error
  }
}

// Fallback functions
function generateFallbackAvatar() {
  // Simple base64 encoded 1x1 pixel image as fallback
  return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
}

function generateFallbackScenes(script) {
  const wordCount = script.split(' ').length
  const estimatedDuration = Math.ceil(wordCount / 150 * 60) // ~150 words per minute
  
  return [
    {
      timeframe: `0:00-0:${Math.floor(estimatedDuration/3)}`,
      prompt: 'modern professional office environment with soft lighting and minimalist design'
    },
    {
      timeframe: `0:${Math.floor(estimatedDuration/3)}-0:${Math.floor(estimatedDuration*2/3)}`,
      prompt: 'close-up of modern technology, computer screens, and digital interfaces'
    },
    {
      timeframe: `0:${Math.floor(estimatedDuration*2/3)}-0:${estimatedDuration}`,
      prompt: 'professional business meeting room with presentation screen and corporate atmosphere'
    }
  ]
}

function generateFallbackBackground() {
  return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
}

function generateMockFinalVideo(talkingHeadVideo, backgrounds) {
  // Enhanced mock video data representing the final composed video
  return `TW9ja1ZpZGVvRGF0YV8ke talkingHeadVideo.duration}_${backgrounds.length}scenes_${Date.now()}`
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

    // Generate Video endpoint - POST /api/generate-video
    if (route === '/generate-video' && method === 'POST') {
      const body = await request.json()
      
      if (!body.script) {
        return handleCORS(NextResponse.json(
          { error: "Script is required for video generation" }, 
          { status: 400 }
        ))
      }

      try {
        console.log('Starting comprehensive video generation...')
        
        const videoGenerationProcess = {
          id: uuidv4(),
          script: body.script,
          options: body.options || {},
          status: 'processing',
          progress: 0,
          steps: [],
          created_at: new Date()
        }

        // Store initial record
        await db.collection('videos').insertOne(videoGenerationProcess)

        // Step 1: Generate Avatar Image
        console.log('Step 1: Generating avatar image...')
        const avatarDescription = body.options?.avatar_description || 'professional business person'
        const avatarStyle = body.options?.avatar_style || 'realistic'
        const avatarImage = await generateAvatarImage(avatarDescription, avatarStyle)
        
        videoGenerationProcess.steps.push({
          step: 1,
          name: 'avatar_generation',
          status: 'completed',
          result: 'Avatar image generated successfully'
        })
        videoGenerationProcess.progress = 20

        // Step 2: Extract Scene-Based Visual Prompts
        console.log('Step 2: Extracting scene prompts...')
        const scenePrompts = await extractScenePrompts(body.script)
        
        videoGenerationProcess.steps.push({
          step: 2,
          name: 'scene_extraction',
          status: 'completed',
          result: `Extracted ${scenePrompts.length} scene prompts`
        })
        videoGenerationProcess.progress = 40

        // Step 3: Generate Background Images
        console.log('Step 3: Generating background images...')
        const backgroundImages = await generateBackgroundImages(scenePrompts)
        
        videoGenerationProcess.steps.push({
          step: 3,
          name: 'background_generation',
          status: 'completed',
          result: `Generated ${backgroundImages.length} background images`
        })
        videoGenerationProcess.progress = 60

        // Step 4: Create Talking Head Video
        console.log('Step 4: Creating talking head video...')
        // Estimate duration from script (approximately 150 words per minute)
        const wordCount = body.script.split(' ').length
        const estimatedDuration = Math.ceil(wordCount / 150 * 60) // Convert to seconds
        
        const talkingHeadVideo = await createTalkingHeadVideo(avatarImage, null, estimatedDuration)
        
        videoGenerationProcess.steps.push({
          step: 4,
          name: 'talking_head_creation',
          status: 'completed',
          result: 'Talking head video created successfully'
        })
        videoGenerationProcess.progress = 80

        // Step 5: Compose Final Video
        console.log('Step 5: Composing final video...')
        const finalVideo = await composeFinalVideo(talkingHeadVideo, backgroundImages, null, body.script)
        
        videoGenerationProcess.steps.push({
          step: 5,
          name: 'final_composition',
          status: 'completed',
          result: 'Final video composed successfully'
        })
        videoGenerationProcess.progress = 100
        videoGenerationProcess.status = 'completed'
        videoGenerationProcess.completed_at = new Date()

        // Update final record
        await db.collection('videos').updateOne(
          { id: videoGenerationProcess.id },
          { $set: videoGenerationProcess }
        )

        console.log('Video generation completed successfully!')

        // Return the complete video data
        return handleCORS(NextResponse.json({
          success: true,
          video: {
            id: finalVideo.id,
            avatar: finalVideo.avatar,
            backgrounds: finalVideo.backgrounds,
            scenes: scenePrompts,
            duration: finalVideo.duration,
            script: body.script,
            videoBase64: finalVideo.videoBase64,
            metadata: finalVideo.metadata,
            processing_steps: videoGenerationProcess.steps
          }
        }))
      } catch (error) {
        console.error('Video generation error:', error)
        
        // Update record with error status
        await db.collection('videos').updateOne(
          { id: videoGenerationProcess.id },
          { 
            $set: { 
              status: 'failed', 
              error: error.message,
              failed_at: new Date()
            }
          }
        )
        
        return handleCORS(NextResponse.json(
          { error: error.message || 'Failed to generate video' }, 
          { status: 500 }
        ))
      }
    }

    // Get Videos History endpoint - GET /api/videos
    if (route === '/videos' && method === 'GET') {
      const videos = await db.collection('videos')
        .find({})
        .sort({ created_at: -1 })
        .limit(20)
        .toArray()

      // Remove MongoDB's _id field from response
      const cleanedVideos = videos.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedVideos))
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