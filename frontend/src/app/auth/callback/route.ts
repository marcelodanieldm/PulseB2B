import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Auth Callback Route Handler
 * 
 * Handles OAuth callback from Google and email confirmation redirects
 * Exchanges authorization code for session
 * Redirects to dashboard or original destination
 * 
 * Flow:
 *   1. User completes OAuth/email confirmation
 *   2. Provider redirects to /auth/callback?code=xxx
 *   3. Exchange code for session (sets cookies)
 *   4. Redirect to /continental or next parameter
 * 
 * Error Handling:
 *   - Invalid code: Redirect to /login?error=auth_failed
 *   - Server error: Redirect to /login?error=server_error
 */

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const next = requestUrl.searchParams.get('next') || '/continental';
  const error = requestUrl.searchParams.get('error');
  const errorDescription = requestUrl.searchParams.get('error_description');

  // Handle OAuth errors from provider
  if (error) {
    console.error('OAuth error:', error, errorDescription);
    return NextResponse.redirect(
      new URL(
        `/login?error=${encodeURIComponent(error)}&message=${encodeURIComponent(errorDescription || 'Authentication failed')}`,
        requestUrl.origin
      )
    );
  }

  // Exchange code for session
  if (code) {
    try {
      const supabase = createRouteHandlerClient({ cookies });
      
      // Exchange authorization code for session
      const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

      if (exchangeError) {
        console.error('Code exchange error:', exchangeError);
        return NextResponse.redirect(
          new URL(
            `/login?error=auth_failed&message=${encodeURIComponent(exchangeError.message)}`,
            requestUrl.origin
          )
        );
      }

      // Successfully authenticated
      if (data?.session) {
        console.log('User authenticated:', data.user?.email);
        
        // Redirect to destination
        return NextResponse.redirect(new URL(next, requestUrl.origin));
      }
    } catch (err) {
      console.error('Auth callback error:', err);
      return NextResponse.redirect(
        new URL(
          `/login?error=server_error&message=${encodeURIComponent('An unexpected error occurred')}`,
          requestUrl.origin
        )
      );
    }
  }

  // No code provided - invalid callback
  console.warn('Auth callback called without code parameter');
  return NextResponse.redirect(
    new URL(
      '/login?error=invalid_request&message=Missing authentication code',
      requestUrl.origin
    )
  );
}
