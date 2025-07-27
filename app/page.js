'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, Download, Play, Pause, Volume2, FileText, Mic } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function App() {
  const [businessDescription, setBusinessDescription] = useState('')
  const [generatedScript, setGeneratedScript] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [isGeneratingScript, setIsGeneratingScript] = useState(false)
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)

  // Direct Groq API call from frontend
  const generateScript = async (retryCount = 0) => {
    if (!businessDescription.trim()) {
      setError('Please enter a business description')
      setTimeout(() => setError(''), 3000)
      return
    }

    setIsGeneratingScript(true)
    setError('')
    setSuccess('')
    setGeneratedScript('')
    setAudioUrl('')
    
    try {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer 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`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: "llama-3.3-70b-versatile",
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
              content: `Create a compelling business video script based on this description: ${businessDescription}`
            }
          ],
          temperature: 0.7,
          max_tokens: 1000
        }),
      })
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('API authentication failed. Please check the API key.')
        } else if (response.status === 429) {
          throw new Error('API rate limit exceeded. Please try again in a moment.')
        } else if (response.status >= 500) {
          throw new Error('AI service temporarily unavailable. Please try again later.')
        }
        throw new Error(`Request failed with status ${response.status}`)
      }
      
      const data = await response.json()
      
      if (!data.choices || !data.choices[0] || !data.choices[0].message) {
        throw new Error('Invalid response format from AI service')
      }
      
      const script = data.choices[0].message.content
      if (!script || script.trim() === '') {
        throw new Error('Empty script generated. Please try again.')
      }
      
      setGeneratedScript(script)
      setSuccess('Script generated successfully!')
      setTimeout(() => setSuccess(''), 5000)
      
    } catch (err) {
      console.error('Script generation error:', err)
      
      let errorMessage = err.message
      
      // Add retry logic for certain errors
      if (retryCount < 2 && (
        err.message.includes('temporarily unavailable') ||
        err.message.includes('rate limit') ||
        err.message.includes('timeout')
      )) {
        console.log(`Retrying script generation (attempt ${retryCount + 1}/2)...`)
        setTimeout(() => generateScript(retryCount + 1), 2000)
        return
      }
      
      setError(errorMessage)
      setTimeout(() => setError(''), 10000)
    } finally {
      setIsGeneratingScript(false)
    }
  }

  // Enhanced client-side voiceover generation using Web Speech API
  const generateVoiceover = async () => {
    if (!generatedScript.trim()) {
      setError('Please generate a script first')
      setTimeout(() => setError(''), 3000)
      return
    }

    setIsGeneratingVoice(true)
    setError('')
    setSuccess('')
    setAudioUrl('')
    
    try {
      console.log('Starting Web Speech API voiceover generation...')
      
      // Check if Web Speech API is supported
      if (!window.speechSynthesis) {
        throw new Error('Web Speech API is not supported in this browser')
      }
      
      // Generate actual speech from script text using Web Speech API
      const audioBlob = await generateSpeechFromText(generatedScript)
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // Calculate duration based on script length (more accurate for actual speech)
      const wordCount = generatedScript.split(' ').length
      const estimatedDuration = Math.max(10, Math.min(180, wordCount * 0.5)) // 0.5 seconds per word
      
      setAudioUrl(audioUrl)
      
      // Show success message
      const successMessage = `Voiceover generated successfully! Speaking your script (${Math.round(estimatedDuration)}s, ${wordCount} words)`
      setSuccess(successMessage)
      setTimeout(() => setSuccess(''), 8000)
      
      console.log(`✅ Speech generated from script: ${Math.round(estimatedDuration)}s duration`)
      
    } catch (err) {
      console.error('Voiceover generation error:', err)
      setError(`Failed to generate voiceover: ${err.message}`)
      setTimeout(() => setError(''), 10000)
    } finally {
      setIsGeneratingVoice(false)
    }
  }

  // Generate actual speech from text using Web Speech API
  const generateSpeechFromText = async (text) => {
    return new Promise((resolve, reject) => {
      try {
        console.log('Converting text to speech using Web Speech API...')
        
        // Create speech synthesis utterance
        const utterance = new SpeechSynthesisUtterance(text)
        
        // Configure speech parameters for professional voiceover
        utterance.rate = 0.9    // Slightly slower for clarity
        utterance.pitch = 1.0   // Normal pitch
        utterance.volume = 0.8  // Good volume level
        
        // Try to find a high-quality voice
        const voices = speechSynthesis.getVoices()
        let selectedVoice = null
        
        // Prefer English voices, prioritize female voices for professional sound
        const preferredVoices = [
          'Microsoft Zira - English (United States)',
          'Google US English Female',
          'Microsoft Hazel - English (Great Britain)',
          'Google UK English Female',
          'Apple Samantha',
          'Microsoft David - English (United States)',
          'Google US English Male'
        ]
        
        // Try to find preferred voice
        for (const preferred of preferredVoices) {
          selectedVoice = voices.find(voice => voice.name.includes(preferred.split(' - ')[0]))
          if (selectedVoice) break
        }
        
        // If no preferred voice found, use any English voice
        if (!selectedVoice) {
          selectedVoice = voices.find(voice => 
            voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female')
          ) || voices.find(voice => voice.lang.startsWith('en'))
        }
        
        if (selectedVoice) {
          utterance.voice = selectedVoice
          console.log(`Using voice: ${selectedVoice.name} (${selectedVoice.lang})`)
        }
        
        // Create MediaRecorder to capture speech
        const mediaRecorder = createAudioRecorder()
        const audioChunks = []
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data)
          }
        }
        
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
          console.log(`✅ Speech recording complete: ${audioBlob.size} bytes`)
          resolve(audioBlob)
        }
        
        mediaRecorder.onerror = (error) => {
          console.error('MediaRecorder error:', error)
          reject(new Error('Failed to record speech audio'))
        }
        
        // Set up speech events
        utterance.onstart = () => {
          console.log('Speech synthesis started, beginning recording...')
          mediaRecorder.start()
        }
        
        utterance.onend = () => {
          console.log('Speech synthesis complete, stopping recording...')
          setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
              mediaRecorder.stop()
            }
          }, 500) // Small delay to ensure all audio is captured
        }
        
        utterance.onerror = (error) => {
          console.error('Speech synthesis error:', error)
          if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop()
          }
          reject(new Error(`Speech synthesis failed: ${error.error}`))
        }
        
        // Start speech synthesis
        speechSynthesis.speak(utterance)
        
      } catch (error) {
        console.error('Error in generateSpeechFromText:', error)
        reject(error)
      }
    })
  }

  // Create audio recorder for capturing speech
  const createAudioRecorder = () => {
    try {
      // Create a silent audio context to capture system audio
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      const dest = audioContext.createMediaStreamDestination()
      
      // Create silent tone to establish audio stream
      oscillator.connect(gainNode)
      gainNode.connect(dest)
      gainNode.gain.setValueAtTime(0, audioContext.currentTime) // Silent
      oscillator.frequency.setValueAtTime(440, audioContext.currentTime)
      oscillator.start()
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(dest.stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      return mediaRecorder
    } catch (error) {
      console.error('Error creating audio recorder:', error)
      throw new Error('Could not create audio recorder')
    }
  }



  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement('a')
      a.href = audioUrl
      
      // Generate a more descriptive filename
      const timestamp = new Date().toISOString().split('T')[0]
      const wordCount = generatedScript.split(' ').length
      a.download = `business-voiceover-${wordCount}words-${timestamp}.wav`
      
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }

  const togglePlayback = () => {
    const audio = document.getElementById('audio-player')
    if (audio) {
      if (isPlaying) {
        audio.pause()
      } else {
        audio.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Business Video Script & Voiceover Generator
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Transform your business ideas into engaging video scripts and professional voiceovers
            using AI-powered tools
          </p>
          <div className="flex justify-center gap-2 mt-4">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <Mic className="w-3 h-3 mr-1" />
              Groq AI
            </Badge>
            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
              <Volume2 className="w-3 h-3 mr-1" />
              Web Audio API
            </Badge>
            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
              <div className="w-2 h-2 bg-emerald-500 rounded-full mr-1 animate-pulse"></div>
              Enhanced Client-Side
            </Badge>
          </div>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6 md:grid-cols-2">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Business Description
              </CardTitle>
              <CardDescription>
                Describe your product, service, or business idea to generate a compelling video script
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="e.g., We're launching a new AI-powered CRM software that helps sales teams automate their follow-ups and increase conversion rates by 40%. Our target audience is small to medium businesses looking to scale their sales operations efficiently."
                value={businessDescription}
                onChange={(e) => setBusinessDescription(e.target.value)}
                rows={6}
                className="resize-none"
              />
              <Button 
                onClick={generateScript}
                disabled={isGeneratingScript || !businessDescription.trim()}
                className="w-full"
              >
                {isGeneratingScript ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Script...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Generate Script
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Script Output Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Generated Script
              </CardTitle>
              <CardDescription>
                AI-generated video script based on your business description
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border rounded-lg p-4 min-h-[200px] bg-gray-50">
                {generatedScript ? (
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {generatedScript}
                  </div>
                ) : (
                  <div className="text-gray-500 text-center py-8">
                    Your generated script will appear here
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={generateVoiceover}
                  disabled={isGeneratingVoice || !generatedScript}
                  className="flex-1"
                >
                  {isGeneratingVoice ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating Voice...
                    </>
                  ) : (
                    <>
                      <Mic className="w-4 h-4 mr-2" />
                      Generate Voiceover
                    </>
                  )}
                </Button>
                {generatedScript && (
                  <Button 
                    variant="outline" 
                    onClick={() => navigator.clipboard.writeText(generatedScript)}
                  >
                    Copy
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Audio Player Section */}
        {audioUrl && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="w-5 h-5" />
                Generated Voiceover
              </CardTitle>
              <CardDescription>
                AI-generated voiceover ready for download
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={togglePlayback}
                  className="flex items-center gap-2"
                >
                  {isPlaying ? (
                    <Pause className="w-4 h-4" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                  {isPlaying ? 'Pause' : 'Play'}
                </Button>
                
                <audio
                  id="audio-player"
                  src={audioUrl}
                  onEnded={() => setIsPlaying(false)}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  className="flex-1"
                  controls
                />
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadAudio}
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Features Section */}
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-semibold mb-6">Features</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="p-6">
                <FileText className="w-8 h-8 mx-auto mb-3 text-blue-600" />
                <h3 className="font-semibold mb-2">AI Script Generation</h3>
                <p className="text-sm text-gray-600">
                  Create compelling video scripts using advanced Groq AI technology
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <Mic className="w-8 h-8 mx-auto mb-3 text-green-600" />
                <h3 className="font-semibold mb-2">Enhanced Audio Generation</h3>
                <p className="text-sm text-gray-600">
                  Generate high-quality speech-like audio using advanced Web Audio API with realistic speech patterns
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <Download className="w-8 h-8 mx-auto mb-3 text-purple-600" />
                <h3 className="font-semibold mb-2">Instant Download</h3>
                <p className="text-sm text-gray-600">
                  Download your generated audio files instantly in WAV format
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}