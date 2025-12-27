// Supabase Edge Function (Node.js) - Trigger Service for Webhooks
import { serve } from 'std/server'

serve(async (req) => {
  const { lead } = await req.json();
  // Fetch all active webhooks
  const resp = await fetch(`${Deno.env.get('SUPABASE_URL')}/rest/v1/webhooks?active=eq.true`, {
    headers: {
      apikey: Deno.env.get('SUPABASE_KEY'),
      Authorization: `Bearer ${Deno.env.get('SUPABASE_KEY')}`
    }
  });
  const webhooks = await resp.json();
  for (const hook of webhooks) {
    // Simple filter match (expand as needed)
    const filters = hook.filters || {};
    let match = true;
    for (const key in filters) {
      if (lead[key] !== filters[key]) match = false;
    }
    if (match) {
      // Async POST to customer endpoint
      fetch(hook.endpoint_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lead)
      });
    }
  }
  return new Response(JSON.stringify({ status: 'ok' }), { headers: { 'Content-Type': 'application/json' } });
});
