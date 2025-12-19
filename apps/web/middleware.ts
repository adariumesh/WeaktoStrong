import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // For now, let's not enforce authentication in middleware
  // We'll handle it in individual pages
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     * - api routes (handled separately)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
