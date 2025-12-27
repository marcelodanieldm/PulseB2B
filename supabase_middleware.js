// Supabase Edge Function Middleware for Protected Routes
import { serve } from 'std/server'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

serve(async (req) => {
  const authHeader = req.headers.get('authorization')
  if (!authHeader) return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 })
  const token = authHeader.replace('Bearer ', '')
  const { data: { user }, error } = await supabase.auth.getUser(token)
  if (error || !user) return new Response(JSON.stringify({ error: 'Invalid session' }), { status: 401 })
  const { data: profile } = await supabase.from('profiles').select('plan_type').eq('id', user.id).single()
  if (!profile || profile.plan_type !== 'pro') {
    return new Response(JSON.stringify({ error: 'Upgrade required' }), { status: 403 })
  }
  // Si pasa, continúa con la lógica de la ruta protegida
  // Ejemplo: return new Response(JSON.stringify({ message: 'Access granted', user }), { status: 200 })
  return new Response(JSON.stringify({ message: 'Access granted', user }), { status: 200 })
})
