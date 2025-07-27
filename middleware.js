import { NextResponse } from 'next/server'

export function middleware(request) {
  const url = request.nextUrl.clone()
  
  // Log all requests for debugging
  console.log(`[MIDDLEWARE] ${request.method} ${url.pathname}`)
  
  // Handle API routes
  if (url.pathname.startsWith('/api/')) {
    console.log(`[MIDDLEWARE] API route detected: ${url.pathname}`)
    // Let Next.js handle API routes normally
    return NextResponse.next()
  }
  
  // Handle all other routes normally
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}