'use client'

import { useState, useEffect } from 'react'
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
  const [connectionStatus, setConnectionStatus] = useState('checking') // checking, connected, disconnected

  // Check API connection status on component mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('/api/', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          setConnectionStatus('connected')
        } else {
          setConnectionStatus('disconnected')
        }
      } catch (error) {
        console.error('Connection check failed:', error)
        setConnectionStatus('disconnected')
      }
    }
    
    checkConnection()
    
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])

  const generateScript = async (retryCount = 0) => {
    if (!businessDescription.trim()) {
      setError('Please enter a business description')
      setTimeout(() => setError(''), 3000) // Clear error after 3 seconds
      return
    }

    setIsGeneratingScript(true)
    setError('')
    setSuccess('')
    setGeneratedScript('') // Clear previous script
    setAudioUrl('') // Clear previous audio
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout

      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: businessDescription,
          options: {
            model: "llama-3.3-70b-versatile",
            temperature: 0.7,
            max_tokens: 1000
          }
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      // Handle different HTTP status codes
      if (!response.ok) {
        let errorMessage = 'Unknown error occurred'
        
        // Handle specific error codes
        if (response.status === 502) {
          errorMessage = 'The service is temporarily unavailable due to server routing issues. This may be an infrastructure problem with the external URL.'
        } else if (response.status === 503) {
          errorMessage = 'Service temporarily unavailable. Please try again in a moment.'
        } else if (response.status === 504) {
          errorMessage = 'Request timeout. The server took too long to respond.'
        } else if (response.status >= 500) {
          errorMessage = 'Internal server error. Please try again later.'
        } else if (response.status === 404) {
          errorMessage = 'API endpoint not found. Please check the service configuration.'
        } else if (response.status === 400) {
          errorMessage = 'Bad request. Please check your input and try again.'
        } else if (response.status === 401) {
          errorMessage = 'Unauthorized. Please check API credentials.'
        } else if (response.status === 429) {
          errorMessage = 'Too many requests. Please wait a moment and try again.'
        }
        
        // Try to get more detailed error message from response
        try {
          const contentType = response.headers.get('content-type')
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json()
            if (errorData.error) {
              errorMessage = errorData.error
            }
          }
        } catch (jsonError) {
          // If we can't parse the error response, use the status-based message
          console.warn('Could not parse error response:', jsonError)
        }
        
        throw new Error(errorMessage)
      }
      
      // Check if response has content before parsing JSON
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned invalid content type. Expected JSON response.')
      }
      
      const responseText = await response.text()
      if (!responseText || responseText.trim() === '') {
        throw new Error('Server returned empty response. Please try again.')
      }
      
      let data
      try {
        data = JSON.parse(responseText)
      } catch (jsonError) {
        console.error('JSON Parse Error:', jsonError)
        console.error('Response Text:', responseText)
        console.error('Response Headers:', Object.fromEntries(response.headers.entries()))
        throw new Error('Server returned invalid JSON response. This may indicate a routing or configuration issue.')
      }
      
      if (!data || typeof data !== 'object') {
        throw new Error('Server returned invalid data structure.')
      }
      
      if (!data.script) {
        throw new Error('No script generated in response. Please try again.')
      }
      
      setGeneratedScript(data.script)
      setSuccess('Script generated successfully!')
      setTimeout(() => setSuccess(''), 5000) // Clear success after 5 seconds
      
    } catch (err) {
      console.error('Script generation error:', err)
      
      let errorMessage = err.message
      
      // Handle specific error types
      if (err.name === 'AbortError') {
        errorMessage = 'Request timed out. The server took too long to respond.'
      } else if (err.name === 'TypeError' && err.message.includes('Failed to fetch')) {
        errorMessage = 'Network error. Please check your internet connection and try again.'
      }
      
      // Add retry logic for certain errors
      if (retryCount < 2 && (
        err.message.includes('502') || 
        err.message.includes('503') || 
        err.message.includes('temporarily unavailable') ||
        err.message.includes('timeout')
      )) {
        console.log(`Retrying script generation (attempt ${retryCount + 1}/2)...`)
        setTimeout(() => generateScript(retryCount + 1), 2000) // Retry after 2 seconds
        return
      }
      
      setError(errorMessage)
      setTimeout(() => setError(''), 10000) // Clear error after 10 seconds for longer messages
    } finally {
      setIsGeneratingScript(false)
    }
  }

  const generateVoiceover = async (retryCount = 0) => {
    if (!generatedScript.trim()) {
      setError('Please generate a script first')
      setTimeout(() => setError(''), 3000) // Clear error after 3 seconds
      return
    }

    setIsGeneratingVoice(true)
    setError('')
    setSuccess('')
    setAudioUrl('') // Clear previous audio
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout

      const response = await fetch('/api/generate-voiceover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: generatedScript,
          voice_style: 'professional'
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      // Handle different HTTP status codes
      if (!response.ok) {
        let errorMessage = 'Unknown error occurred'
        
        // Handle specific error codes
        if (response.status === 502) {
          errorMessage = 'The service is temporarily unavailable due to server routing issues. This may be an infrastructure problem with the external URL.'
        } else if (response.status === 503) {
          errorMessage = 'Voiceover service temporarily unavailable. Please try again in a moment.'
        } else if (response.status === 504) {
          errorMessage = 'Request timeout. The voiceover generation took too long.'
        } else if (response.status >= 500) {
          errorMessage = 'Internal server error during voiceover generation. Please try again later.'
        } else if (response.status === 404) {
          errorMessage = 'Voiceover API endpoint not found. Please check the service configuration.'
        } else if (response.status === 400) {
          errorMessage = 'Bad request. Please check your script and try again.'
        } else if (response.status === 429) {
          errorMessage = 'Too many requests. Please wait a moment and try again.'
        }
        
        // Try to get more detailed error message from response
        try {
          const contentType = response.headers.get('content-type')
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json()
            if (errorData.error) {
              errorMessage = errorData.error
            }
          }
        } catch (jsonError) {
          // If we can't parse the error response, use the status-based message
          console.warn('Could not parse error response:', jsonError)
        }
        
        throw new Error(errorMessage)
      }
      
      // Check content type for audio response
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('audio/')) {
        throw new Error('Server returned invalid content type. Expected audio response.')
      }
      
      const audioBlob = await response.blob()
      if (!audioBlob || audioBlob.size === 0) {
        throw new Error('Server returned empty audio response. Please try again.')
      }
      
      const audioUrl = URL.createObjectURL(audioBlob)
      setAudioUrl(audioUrl)
      setSuccess('Voiceover generated successfully!')
      setTimeout(() => setSuccess(''), 5000) // Clear success after 5 seconds
      
    } catch (err) {
      console.error('Voiceover generation error:', err)
      
      let errorMessage = err.message
      
      // Handle specific error types
      if (err.name === 'AbortError') {
        errorMessage = 'Voiceover generation timed out. The server took too long to respond.'
      } else if (err.name === 'TypeError' && err.message.includes('Failed to fetch')) {
        errorMessage = 'Network error during voiceover generation. Please check your internet connection and try again.'
      }
      
      // Add retry logic for certain errors
      if (retryCount < 2 && (
        err.message.includes('502') || 
        err.message.includes('503') || 
        err.message.includes('temporarily unavailable') ||
        err.message.includes('timeout')
      )) {
        console.log(`Retrying voiceover generation (attempt ${retryCount + 1}/2)...`)
        setTimeout(() => generateVoiceover(retryCount + 1), 2000) // Retry after 2 seconds
        return
      }
      
      setError(errorMessage)
      setTimeout(() => setError(''), 10000) // Clear error after 10 seconds for longer messages
    } finally {
      setIsGeneratingVoice(false)
    }
  }

  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement('a')
      a.href = audioUrl
      a.download = 'business-voiceover.wav'
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
              Mixtral AI
            </Badge>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              <Volume2 className="w-3 h-3 mr-1" />
              Bark TTS
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
                Professional AI-generated voiceover ready for download
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
                  Create compelling video scripts using advanced Mixtral AI technology
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <Mic className="w-8 h-8 mx-auto mb-3 text-green-600" />
                <h3 className="font-semibold mb-2">Professional Voiceover</h3>
                <p className="text-sm text-gray-600">
                  Generate high-quality voiceovers with Bark TTS technology
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