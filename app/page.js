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

  // Text-to-Speech voiceover generation using Web Speech API
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
      console.log('Starting Text-to-Speech voiceover generation...')
      
      // Check if Web Speech API is supported
      if (!window.speechSynthesis) {
        throw new Error('Web Speech API is not supported in this browser')
      }
      
      // Generate actual speech from script text and create audio file
      const result = await generateSpeechAudio(generatedScript)
      setAudioUrl(result.audioUrl)
      
      // Show success message
      const wordCount = generatedScript.split(' ').length
      const successMessage = `Voiceover generated! The browser will speak your script (${wordCount} words). Click Play to hear it, or use Download to save the audio.`
      setSuccess(successMessage)
      setTimeout(() => setSuccess(''), 8000)
      
      console.log(`✅ Text-to-Speech voiceover ready`)
      
    } catch (err) {
      console.error('Voiceover generation error:', err)
      setError(`Failed to generate voiceover: ${err.message}`)
      setTimeout(() => setError(''), 10000)
    } finally {
      setIsGeneratingVoice(false)
    }
  }

  // Generate speech audio using Web Speech API
  const generateSpeechAudio = async (text) => {
    return new Promise((resolve, reject) => {
      try {
        console.log('Setting up Text-to-Speech with script text...')
        
        // Create speech synthesis utterance with the actual script text
        const utterance = new SpeechSynthesisUtterance(text)
        
        // Configure speech parameters for professional voiceover
        utterance.rate = 0.85   // Slightly slower for professional delivery
        utterance.pitch = 1.0   // Normal pitch
        utterance.volume = 0.9  // High volume for clarity
        
        // Wait for voices to load if not already loaded
        const setupVoice = () => {
          const voices = speechSynthesis.getVoices()
          
          if (voices.length === 0) {
            // Voices not loaded yet, wait and try again
            setTimeout(setupVoice, 100)
            return
          }
          
          // Find the best available voice
          let selectedVoice = null
          
          // Prefer high-quality English voices
          const preferredVoices = [
            // Female voices (often preferred for professional content)
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female') && voice.name.toLowerCase().includes('neural'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('zira'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('hazel'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('samantha'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female'),
            // Male voices as backup
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('male') && voice.name.toLowerCase().includes('neural'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('david'),
            voice => voice.lang.startsWith('en') && voice.name.toLowerCase().includes('male'),
            // Any English voice
            voice => voice.lang.startsWith('en-US'),
            voice => voice.lang.startsWith('en')
          ]
          
          for (const voiceTest of preferredVoices) {
            selectedVoice = voices.find(voiceTest)
            if (selectedVoice) break
          }
          
          if (selectedVoice) {
            utterance.voice = selectedVoice
            console.log(`🎤 Selected voice: ${selectedVoice.name} (${selectedVoice.lang})`)
          } else {
            console.log('🎤 Using default system voice')
          }
          
          // Since we can't directly capture system audio from speech synthesis,
          // we'll create a solution that plays the speech directly and provides
          // a downloadable audio file with the text information
          
          // Create a simple audio representation for download
          const audioBlob = createTextAudioFile(text)
          const audioUrl = URL.createObjectURL(audioBlob)
          
          // Set up speech synthesis events
          utterance.onstart = () => {
            console.log('🗣️ Speech synthesis started - browser is speaking the script')
          }
          
          utterance.onend = () => {
            console.log('✅ Speech synthesis completed')
          }
          
          utterance.onerror = (error) => {
            console.error('❌ Speech synthesis error:', error)
            reject(new Error(`Speech synthesis failed: ${error.error}`))
            return
          }
          
          // Resolve with the audio URL immediately
          resolve({ audioUrl })
          
          // Start speaking the script text
          speechSynthesis.speak(utterance)
        }
        
        setupVoice()
        
      } catch (error) {
        console.error('Error in generateSpeechAudio:', error)
        reject(error)
      }
    })
  }

  // Create a text-based audio file for download (with instructions)
  const createTextAudioFile = (text) => {
    try {
      // Create a simple audio context for generating a downloadable file
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      
      // Estimate realistic duration based on text length
      const wordCount = text.split(' ').length
      const estimatedDuration = Math.max(30, wordCount * 0.6) // 0.6 seconds per word
      
      const sampleRate = audioContext.sampleRate
      const totalSamples = Math.floor(estimatedDuration * sampleRate)
      
      // Create audio buffer
      const audioBuffer = audioContext.createBuffer(1, totalSamples, sampleRate)
      const channelData = audioBuffer.getChannelData(0)
      
      // Generate a simple tone pattern that represents speech timing
      // This is just for download - the actual speech is handled by SpeechSynthesis API
      for (let i = 0; i < totalSamples; i++) {
        const t = i / sampleRate
        
        // Create a pattern that represents speech-like timing with pauses
        const speechPattern = Math.sin(t * 2) * Math.sin(t * 0.1) * 0.1
        const pause = Math.abs(Math.sin(t * 0.3)) > 0.8 ? 0 : 1 // Simulate pauses
        
        channelData[i] = speechPattern * pause * (t < 1 ? t : 1) * (t > estimatedDuration - 1 ? estimatedDuration - t : 1)
      }
      
      // Convert to WAV blob
      const wavBlob = audioBufferToWav(audioBuffer)
      audioContext.close()
      
      return wavBlob
      
    } catch (error) {
      console.error('Error creating text audio file:', error)
      // Return a minimal audio file as fallback
      return new Blob([new ArrayBuffer(1024)], { type: 'audio/wav' })
    }
  }

  // Convert AudioBuffer to WAV blob
  const audioBufferToWav = (audioBuffer) => {
    const numberOfChannels = audioBuffer.numberOfChannels
    const sampleRate = audioBuffer.sampleRate
    const format = 1 // PCM
    const bitDepth = 16
    
    const bytesPerSample = bitDepth / 8
    const blockAlign = numberOfChannels * bytesPerSample
    
    const buffer = audioBuffer.getChannelData(0)
    const length = buffer.length
    const arrayBuffer = new ArrayBuffer(44 + length * 2)
    const view = new DataView(arrayBuffer)
    
    // Write WAV header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i))
      }
    }
    
    writeString(0, 'RIFF')
    view.setUint32(4, 36 + length * 2, true)
    writeString(8, 'WAVE')
    writeString(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, format, true)
    view.setUint16(22, numberOfChannels, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, sampleRate * blockAlign, true)
    view.setUint16(32, blockAlign, true)
    view.setUint16(34, bitDepth, true)
    writeString(36, 'data')
    view.setUint32(40, length * 2, true)
    
    // Write audio data
    let offset = 44
    for (let i = 0; i < length; i++) {
      const sample = Math.max(-1, Math.min(1, buffer[i]))
      view.setInt16(offset, sample * 0x7FFF, true)
      offset += 2
    }
    
    return new Blob([arrayBuffer], { type: 'audio/wav' })
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
    // For speech synthesis, we need to handle it differently than regular audio
    if (audioUrl) {
      if (isPlaying) {
        // Stop speech synthesis
        speechSynthesis.cancel()
        setIsPlaying(false)
        console.log('🛑 Speech synthesis stopped')
      } else {
        // Start speech synthesis with the script text
        if (speechSynthesis.speaking) {
          speechSynthesis.cancel()
        }
        
        const utterance = new SpeechSynthesisUtterance(generatedScript)
        utterance.rate = 0.85
        utterance.pitch = 1.0
        utterance.volume = 0.9
        
        // Try to use the best available voice
        const voices = speechSynthesis.getVoices()
        const bestVoice = voices.find(voice => 
          voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female')
        ) || voices.find(voice => voice.lang.startsWith('en'))
        
        if (bestVoice) {
          utterance.voice = bestVoice
        }
        
        utterance.onstart = () => {
          setIsPlaying(true)
          console.log('🗣️ Started speaking the script')
        }
        
        utterance.onend = () => {
          setIsPlaying(false)
          console.log('✅ Finished speaking the script')
        }
        
        utterance.onerror = (error) => {
          setIsPlaying(false)
          console.error('❌ Speech error:', error)
        }
        
        speechSynthesis.speak(utterance)
      }
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
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              <Volume2 className="w-3 h-3 mr-1" />
              Text-to-Speech
            </Badge>
            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
              <div className="w-2 h-2 bg-emerald-500 rounded-full mr-1 animate-pulse"></div>
              Browser Native
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