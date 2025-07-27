import './globals.css'

export const metadata = {
  title: 'AI Business Video Script & Voiceover Generator',
  description: 'Transform your business ideas into engaging video scripts and professional voiceovers using AI-powered tools',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}