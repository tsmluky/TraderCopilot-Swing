import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Minimal route-guarding for the MVP UI.
// We store the JWT in a readable cookie (tc_token) so middleware can redirect.
// For higher security, move token storage to HttpOnly cookies and do server-side session.

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Protect dashboard routes
  if (pathname.startsWith("/dashboard")) {
    const token = request.cookies.get("tc_token")?.value;
    if (!token) {
      const url = request.nextUrl.clone();
      url.pathname = "/auth/login";
      url.searchParams.set("next", pathname);
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
