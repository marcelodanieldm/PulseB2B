// supabase/functions/dripScheduler.ts
// Schedules and sends drip emails based on user plan_type and registration date

import { createClient } from '@supabase/supabase-js'

import { sendDripEmail } from '../../api/emails/sendDrip'
import DripValueReminder from '../../emails/DripValueReminder.jsx'
import DripFomoSignal from '../../emails/DripFomoSignal.jsx'
import DripArbitrageAdvantage from '../../emails/DripArbitrageAdvantage.jsx'
import DripTechStackSecret from '../../emails/DripTechStackSecret.jsx'
import DripLastChance from '../../emails/DripLastChance.jsx'

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
    const ctaUrl = 'https://pulseb2b.com/upgrade?utm_source=email&utm_campaign=drip_series';
    const unsubscribeUrl = `https://pulseb2b.com/unsubscribe?email=${encodeURIComponent(user.email)}`;
    // Day 1
    if (daysSinceSignup === 1 && !user.drip_day_1_sent) {
      await sendDripEmail(
        user.email,
        user.name,
        'Don’t let today’s $100k opportunity slip away',
        DripValueReminder({ name: user.name, unlockUrl: ctaUrl, unsubscribeUrl })
      );
      await supabase.from('profiles').update({ drip_day_1_sent: true }).eq('id', user.id)
    }
    // Day 3
    if (daysSinceSignup === 3 && !user.drip_day_3_sent) {
      await sendDripEmail(
        user.email,
        user.name,
        '5 Startups just raised $10M+. Do you have their CTO\'s email?',
        DripFomoSignal({ name: user.name, ctaUrl, unsubscribeUrl })
      );
      await supabase.from('profiles').update({ drip_day_3_sent: true }).eq('id', user.id)
    }
    // Day 7
    if (daysSinceSignup === 7 && !user.drip_day_7_sent) {
      await sendDripEmail(
        user.email,
        user.name,
        'The math behind PulseB2B: Why $29 is a no-brainer',
        DripArbitrageAdvantage({ name: user.name, ctaUrl, unsubscribeUrl })
      );
      await supabase.from('profiles').update({ drip_day_7_sent: true }).eq('id', user.id)
    }
    // Day 10
    if (daysSinceSignup === 10 && !user.drip_day_10_sent) {
      await sendDripEmail(
        user.email,
        user.name,
        'Know their Tech Stack before you call',
        DripTechStackSecret({ name: user.name, ctaUrl, unsubscribeUrl })
      );
      await supabase.from('profiles').update({ drip_day_10_sent: true }).eq('id', user.id)
    }
    // Day 14
    if (daysSinceSignup === 14 && !user.drip_day_14_sent) {
      await sendDripEmail(
        user.email,
        user.name,
        'Is your $29 Founding Member discount expiring?',
        DripLastChance({ name: user.name, ctaUrl, unsubscribeUrl })
      );
      await supabase.from('profiles').update({ drip_day_14_sent: true }).eq('id', user.id)
    }
  }
}
