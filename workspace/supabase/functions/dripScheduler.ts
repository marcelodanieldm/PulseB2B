// supabase/functions/dripScheduler.ts
// Schedules and sends drip emails based on user plan_type and registration date

import { createClient } from '@supabase/supabase-js'
import { sendDripEmail } from '../../api/emails/sendDrip'

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)

export async function handler(event) {
  // 1. Get all users who are still 'free' and opted in
  const { data: users } = await supabase
    .from('profiles')
    .select('*')
    .eq('plan_type', 'free')
    .eq('marketing_opt_in', true)

  for (const user of users) {
    const daysSinceSignup = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000)
    // Day 1
    if (daysSinceSignup === 1 && !user.drip_day_1_sent) {
      await sendDripEmail(user.email, user.name, 'Discover the Value of PulseB2B', `<div style='background:#0f172a;color:#e0e7ef;padding:2rem;'>...</div>`)
      await supabase.from('profiles').update({ drip_day_1_sent: true }).eq('id', user.id)
    }
    // Day 3
    if (daysSinceSignup === 3 && !user.drip_day_3_sent) {
      await sendDripEmail(user.email, user.name, 'Don’t Miss Out – Upgrade Now', `<div style='background:#0f172a;color:#e0e7ef;padding:2rem;'>...</div>`)
      await supabase.from('profiles').update({ drip_day_3_sent: true }).eq('id', user.id)
    }
    // ...continue for days 7, 10, 14
  }
}
