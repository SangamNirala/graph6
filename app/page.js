'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, Download, Play, Pause, Volume2, FileText, Mic, Video, Settings, User, Image } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function App() {
  const [businessDescription, setBusinessDescription] = useState('')
  const [generatedScript, setGeneratedScript] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [videoData, setVideoData] = useState(null)
  const [isGeneratingScript, setIsGeneratingScript] = useState(false)
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false)
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [showVideoOptions, setShowVideoOptions] = useState(false)
  const [selectedVideoType, setSelectedVideoType] = useState('') // 'with_avatar' or 'without_avatar'
  const [selectedQuality, setSelectedQuality] = useState('basic') // 'basic', 'enhanced', 'ultra'

  const generateScript = async () => {
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
      })
      
      // Check if the response is ok before trying to parse JSON
      if (!response.ok) {
        // Handle different types of errors
        if (response.status === 502) {
          throw new Error('Server temporarily unavailable. Please try again in a moment.')
        } else if (response.status >= 500) {
          throw new Error('Server error. Please try again later.')
        } else if (response.status === 404) {
          throw new Error('API endpoint not found.')
        }
        
        // Try to get error message from response if possible
        try {
          const errorData = await response.json()
          throw new Error(errorData.error || `Request failed with status ${response.status}`)
        } catch (jsonError) {
          throw new Error(`Request failed with status ${response.status}`)
        }
      }
      
      // Check if response has content before parsing JSON
      const responseText = await response.text()
      if (!responseText) {
        throw new Error('Empty response from server')
      }
      
      let data
      try {
        data = JSON.parse(responseText)
      } catch (jsonError) {
        console.error('JSON Parse Error:', jsonError)
        console.error('Response Text:', responseText)
        throw new Error('Invalid response format from server')
      }
      
      if (!data.script) {
        throw new Error('No script generated. Please try again.')
      }
      
      setGeneratedScript(data.script)
      setSuccess('Script generated successfully!')
      setTimeout(() => setSuccess(''), 5000) // Clear success after 5 seconds
    } catch (err) {
      setError(err.message)
    } finally {
      setIsGeneratingScript(false)
    }
  }

  const generateVoiceover = async () => {
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
      const response = await fetch('/api/generate-voiceover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: generatedScript,
          voice_style: 'professional'
        }),
      })
      
      // Check if the response is ok before processing
      if (!response.ok) {
        // Handle different types of errors
        if (response.status === 502) {
          throw new Error('Server temporarily unavailable. Please try again in a moment.')
        } else if (response.status >= 500) {
          throw new Error('Server error. Please try again later.')
        }
        
        try {
          const errorData = await response.json()
          throw new Error(errorData.error || `Request failed with status ${response.status}`)
        } catch (jsonError) {
          throw new Error(`Request failed with status ${response.status}`)
        }
      }
      
      const audioBlob = await response.blob()
      if (audioBlob.size === 0) {
        throw new Error('Empty audio response from server')
      }
      
      const audioUrl = URL.createObjectURL(audioBlob)
      setAudioUrl(audioUrl)
      setSuccess('Voiceover generated successfully!')
      setTimeout(() => setSuccess(''), 5000) // Clear success after 5 seconds
    } catch (err) {
      setError(err.message)
    } finally {
      setIsGeneratingVoice(false)
    }
  }

  const generateVideo = async (videoType, quality) => {
    if (!generatedScript.trim()) {
      setError('Please generate a script first')
      setTimeout(() => setError(''), 3000)
      return
    }

    setIsGeneratingVideo(true)
    setError('')
    setSuccess('')
    setVideoData(null)
    
    try {
      let endpoint = ''
      
      if (videoType === 'without_avatar') {
        endpoint = '/api/generate-video-without-avatar'
      } else {
        // with_avatar endpoints based on quality
        switch (quality) {
          case 'basic':
            endpoint = '/api/generate-avatar-video'
            break
          case 'enhanced':
            endpoint = '/api/generate-enhanced-avatar-video'
            break
          case 'ultra':
            endpoint = '/api/generate-ultra-realistic-avatar-video'
            break
          default:
            endpoint = '/api/generate-avatar-video'
        }
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          script: generatedScript,
          quality: quality
        }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Request failed with status ${response.status}`)
      }
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error('Video generation failed')
      }
      
      setVideoData(data.video)
      setSuccess(`${videoType === 'with_avatar' ? 'Avatar' : 'Scene'} video generated successfully!`)
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsGeneratingVideo(false)
    }
  }

  const downloadVideo = () => {
    if (videoData && videoData.videoUrl) {
      const a = document.createElement('a')
      a.href = videoData.videoUrl
      a.download = `business-video-${videoData.type}-${videoData.quality}.mp4`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
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

        {/* Video Generation Section */}
        {(generatedScript && audioUrl) && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="w-5 h-5" />
                Generate Professional Video
              </CardTitle>
              <CardDescription>
                Create a professional business video with your script and voiceover
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!showVideoOptions ? (
                <Button 
                  onClick={() => setShowVideoOptions(true)}
                  className="w-full"
                  size="lg"
                >
                  <Video className="w-4 h-4 mr-2" />
                  Generate Video
                </Button>
              ) : (
                <div className="space-y-4">
                  {/* Video Type Selection */}
                  <div className="space-y-3">
                    <h4 className="font-medium">Choose Video Style:</h4>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <Button
                        variant={selectedVideoType === 'without_avatar' ? 'default' : 'outline'}
                        onClick={() => setSelectedVideoType('without_avatar')}
                        className="p-4 h-auto flex-col gap-2"
                      >
                        <Image className="w-6 h-6" />
                        <div className="text-center">
                          <div className="font-medium">Scene-Based Video</div>
                          <div className="text-xs text-muted-foreground">
                            Images change with scenes + voiceover
                          </div>
                        </div>
                      </Button>
                      
                      <Button
                        variant={selectedVideoType === 'with_avatar' ? 'default' : 'outline'}
                        onClick={() => setSelectedVideoType('with_avatar')}
                        className="p-4 h-auto flex-col gap-2"
                      >
                        <User className="w-6 h-6" />
                        <div className="text-center">
                          <div className="font-medium">Avatar Video</div>
                          <div className="text-xs text-muted-foreground">
                            Talking avatar + scene images
                          </div>
                        </div>
                      </Button>
                    </div>
                  </div>

                  {/* Quality Selection */}
                  {selectedVideoType && (
                    <div className="space-y-3">
                      <h4 className="font-medium">Select Quality:</h4>
                      <div className="grid gap-2 sm:grid-cols-3">
                        <Button
                          variant={selectedQuality === 'basic' ? 'default' : 'outline'}
                          onClick={() => setSelectedQuality('basic')}
                          size="sm"
                        >
                          Basic
                        </Button>
                        <Button
                          variant={selectedQuality === 'enhanced' ? 'default' : 'outline'}
                          onClick={() => setSelectedQuality('enhanced')}
                          size="sm"
                        >
                          Enhanced
                        </Button>
                        <Button
                          variant={selectedQuality === 'ultra' ? 'default' : 'outline'}
                          onClick={() => setSelectedQuality('ultra')}
                          size="sm"
                        >
                          Ultra-Realistic
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Generate Button */}
                  {selectedVideoType && (
                    <div className="flex gap-2">
                      <Button
                        onClick={() => generateVideo(selectedVideoType, selectedQuality)}
                        disabled={isGeneratingVideo}
                        className="flex-1"
                      >
                        {isGeneratingVideo ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Generating Video...
                          </>
                        ) : (
                          <>
                            <Video className="w-4 h-4 mr-2" />
                            Generate {selectedVideoType === 'with_avatar' ? 'Avatar' : 'Scene'} Video
                          </>
                        )}
                      </Button>
                      
                      <Button
                        variant="outline"
                        onClick={() => {
                          setShowVideoOptions(false)
                          setSelectedVideoType('')
                          setSelectedQuality('basic')
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Video Player Section */}
        {videoData && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="w-5 h-5" />
                Generated Video
              </CardTitle>
              <CardDescription>
                Professional {videoData.type === 'with_avatar' ? 'avatar' : 'scene-based'} video ({videoData.quality} quality)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="w-full">
                <video
                  src={videoData.videoUrl}
                  controls
                  className="w-full rounded-lg bg-black"
                  style={{ maxHeight: '400px' }}
                >
                  Your browser does not support the video tag.
                </video>
              </div>
              
              {/* Video Details */}
              <div className="grid gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration:</span>
                  <span>{videoData.duration}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Scenes:</span>
                  <span>{videoData.scenes?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Type:</span>
                  <span className="capitalize">{videoData.type.replace('_', ' ')}</span>
                </div>
              </div>

              {/* Scene Preview */}
              {videoData.scenes && videoData.scenes.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium">Scene Preview:</h4>
                  <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {videoData.scenes.slice(0, 6).map((scene, index) => (
                      <div key={index} className="relative">
                        <img
                          src={`data:image/png;base64,${scene.imageBase64}`}
                          alt={`Scene ${index + 1}`}
                          className="w-full h-20 object-cover rounded"
                        />
                        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b">
                          Scene {index + 1} ({scene.duration}s)
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Button
                onClick={downloadVideo}
                className="w-full"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Video
              </Button>
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