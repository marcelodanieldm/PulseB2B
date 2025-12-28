// supabase/functions/unsubscribe.ts
// Handles unsubscribe requests and updates marketing_opt_in

import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)

export async function handler(event) {
  const email = event.queryStringParameters.email
  if (!email) return { statusCode: 400, body: 'Missing email' }
  await supabase.from('profiles').update({ marketing_opt_in: false }).eq('email', email)
  return { statusCode: 200, body: 'Unsubscribed' }
}
