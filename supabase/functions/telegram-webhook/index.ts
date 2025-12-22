// =====================================================
// TELEGRAM BOT WEBHOOK HANDLER
// =====================================================
// Purpose: Serverless Telegram bot using Telegraf.js
// Cost: $0 (Supabase Edge Functions free tier)
// Author: Senior Backend Developer
// Date: December 22, 2025
// =====================================================

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";
import { Telegraf } from "https://esm.sh/telegraf@4.15.0";

// =====================================================
// ENVIRONMENT VARIABLES
// =====================================================

const TELEGRAM_BOT_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN") || "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const FRONTEND_URL = Deno.env.get("FRONTEND_URL") || "https://pulseb2b.com";

if (!TELEGRAM_BOT_TOKEN) {
  throw new Error("TELEGRAM_BOT_TOKEN is required");
}
if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error("Supabase credentials are required");
}

// =====================================================
// INITIALIZE CLIENTS
// =====================================================

const bot = new Telegraf(TELEGRAM_BOT_TOKEN);
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

// =====================================================
// HELPER FUNCTIONS
// =====================================================

/**
 * Format lead data as a beautiful Telegram message
 * Uses NLP-generated daily_teaser if available
 */
function formatLeadMessage(lead: any): string {
  // Check if NLP-generated teaser exists (from Senior Data Scientist)
  if (lead.daily_teaser) {
    return `
${lead.daily_teaser}

━━━━━━━━━━━━━━━━━━━━
👉 [View Full Details](${FRONTEND_URL}/continental?lead_id=${lead.lead_id}&utm_source=telegram&utm_medium=bot&utm_campaign=latest_command)

_Premium: See contact info + exact funding 💎_
    `.trim();
  }
  
  // Fallback to standard format if no teaser
  const { 
    company_name, 
    desperation_score, 
    company_insight, 
    tech_stack, 
    country, 
    funding_range,
    hiring_velocity,
    lead_id
  } = lead;

  const scoreEmoji = desperation_score >= 90 ? "🔥🔥🔥" : 
                     desperation_score >= 80 ? "🔥🔥" : "🔥";
  
  const countryFlag = getCountryFlag(country);

  return `
${scoreEmoji} *${company_name}* ${countryFlag}
━━━━━━━━━━━━━━━━━━━━

📊 *Desperation Score:* ${desperation_score}/100

💡 *Intelligence:*
${company_insight || "High-value B2B prospect detected"}

💰 *Funding:* ${funding_range}
📈 *Hiring:* ${hiring_velocity}
🛠 *Tech Stack:* ${tech_stack?.slice(0, 5).join(", ") || "N/A"}

━━━━━━━━━━━━━━━━━━━━
👉 [View Full Details](${FRONTEND_URL}/continental?lead_id=${lead_id}&utm_source=telegram&utm_medium=bot&utm_campaign=latest_command)
  `.trim();
}

/**
 * Get country flag emoji
 */
function getCountryFlag(countryCode: string): string {
  const flagMap: Record<string, string> = {
    "US": "🇺🇸",
    "GB": "🇬🇧",
    "DE": "🇩🇪",
    "FR": "🇫🇷",
    "CA": "🇨🇦",
    "AU": "🇦🇺",
    "NL": "🇳🇱",
    "SE": "🇸🇪",
    "SG": "🇸🇬",
    "IN": "🇮🇳",
    "BR": "🇧🇷",
    "MX": "🇲🇽",
    "ES": "🇪🇸",
    "IT": "🇮🇹",
    "JP": "🇯🇵",
    "KR": "🇰🇷",
    "CN": "🇨🇳",
    "IL": "🇮🇱",
    "CH": "🇨🇭",
  };
  return flagMap[countryCode] || "🌍";
}

/**
 * Format welcome message
 */
function formatWelcomeMessage(firstName?: string): string {
  const name = firstName || "there";
  return `
👋 *Welcome to PulseB2B, ${name}!*

I'm your personal B2B intelligence assistant. I'll send you the hottest leads based on real-time signals from across the web.

🎯 *What I can do:*
• Daily Signal: Get the top lead every day at 8 AM UTC
• /latest - Get the highest-scoring lead right now
• /help - See all commands

📊 *Our Intelligence Sources:*
• Funding announcements (Crunchbase, TechCrunch)
• Hiring velocity (LinkedIn, job boards)
• Tech stack changes (GitHub, job postings)
• Cost arbitrage signals (salary data)
• Multi-region expansion patterns

🔥 *Why PulseB2B?*
We track 19 countries and analyze 100,000+ signals daily to find companies that are:
1. Well-funded (Series A+)
2. Hiring aggressively
3. Using modern tech stacks
4. Showing desperation signals

━━━━━━━━━━━━━━━━━━━━
Get started: /latest
  `.trim();
}

// =====================================================
// BOT COMMANDS
// =====================================================

/**
 * /start command - Register user
 */
bot.command("start", async (ctx) => {
  const startTime = Date.now();
  
  try {
    const chatId = ctx.chat.id;
    const username = ctx.from.username || null;
    const firstName = ctx.from.first_name || null;
    const lastName = ctx.from.last_name || null;
    const languageCode = ctx.from.language_code || "en";

    console.log(`[/start] Registering user ${chatId} (${username})`);

    // Register subscriber in database
    const { data: subscriber, error: regError } = await supabase.rpc(
      "register_telegram_subscriber",
      {
        p_chat_id: chatId,
        p_username: username,
        p_first_name: firstName,
        p_last_name: lastName,
        p_language_code: languageCode,
      }
    );

    if (regError) {
      console.error("[/start] Registration error:", regError);
      throw regError;
    }

    console.log(`[/start] Subscriber registered: ${subscriber}`);

    // Send welcome message
    await ctx.replyWithMarkdown(formatWelcomeMessage(firstName));

    // Log command
    const processingTime = Date.now() - startTime;
    await supabase.rpc("log_telegram_command", {
      p_chat_id: chatId,
      p_command: "/start",
      p_processing_time_ms: processingTime,
      p_success: true,
    });

    // Log message delivery
    await supabase.rpc("log_telegram_message", {
      p_chat_id: chatId,
      p_message_type: "welcome",
      p_message_text: "Welcome message",
      p_was_delivered: true,
    });

    console.log(`[/start] Welcome sent to ${chatId} (${processingTime}ms)`);

  } catch (error) {
    console.error("[/start] Error:", error);
    
    // Log failure
    await supabase.rpc("log_telegram_command", {
      p_chat_id: ctx.chat.id,
      p_command: "/start",
      p_processing_time_ms: Date.now() - startTime,
      p_success: false,
      p_error_message: error.message,
    });

    await ctx.reply("Sorry, something went wrong. Please try again later.");
  }
});

/**
 * /latest command - Get highest-scoring lead from last 24h
 */
bot.command("latest", async (ctx) => {
  const startTime = Date.now();
  
  try {
    const chatId = ctx.chat.id;
    console.log(`[/latest] Fetching lead for user ${chatId}`);

    // Check if user is registered
    const { data: subscriber, error: subError } = await supabase
      .from("telegram_subscribers")
      .select("id, is_active")
      .eq("chat_id", chatId)
      .single();

    if (subError || !subscriber) {
      console.log(`[/latest] User not registered: ${chatId}`);
      await ctx.reply("Please use /start first to register!");
      return;
    }

    if (!subscriber.is_active) {
      console.log(`[/latest] User inactive: ${chatId}`);
      await ctx.reply("Your subscription is inactive. Use /start to reactivate!");
      return;
    }

    // Get latest lead (with NLP-generated teaser if available)
    const { data: leads, error: leadError } = await supabase.rpc(
      "get_latest_daily_teaser"
    );

    // Fallback to standard query if no teaser available
    if (leadError || !leads || leads.length === 0) {
      console.log("[/latest] No daily teaser found, trying standard query...");
      
      const { data: fallbackLeads, error: fallbackError } = await supabase.rpc(
        "get_latest_telegram_lead"
      );
      
      if (fallbackError) {
        console.error("[/latest] Fallback query error:", fallbackError);
        throw fallbackError;
      }
      
      if (!fallbackLeads || fallbackLeads.length === 0) {
        await ctx.reply(
          "🤷 No high-scoring leads found in the last 24 hours.\n" +
          "Check back later or lower your standards! 😉"
        );
        
        // Log command
        await supabase.rpc("log_telegram_command", {
          p_chat_id: chatId,
          p_command: "/latest",
          p_command_args: "no_results",
          p_processing_time_ms: Date.now() - startTime,
          p_success: true,
        });
        
        return;
      }
      
      leads = fallbackLeads;
    }

    const lead = leads[0];
    const message = formatLeadMessage(lead);

    // Send lead message
    await ctx.replyWithMarkdown(message, {
      disable_web_page_preview: false,
    });

    // Log command
    const processingTime = Date.now() - startTime;
    await supabase.rpc("log_telegram_command", {
      p_chat_id: chatId,
      p_command: "/latest",
      p_command_args: lead.lead_id,
      p_processing_time_ms: processingTime,
      p_success: true,
    });

    // Log message delivery
    await supabase.rpc("log_telegram_message", {
      p_chat_id: chatId,
      p_message_type: "latest_command",
      p_lead_id: lead.lead_id,
      p_message_text: message,
      p_was_delivered: true,
    });

    console.log(`[/latest] Lead sent to ${chatId}: ${lead.company_name} (${processingTime}ms)`);

  } catch (error) {
    console.error("[/latest] Error:", error);
    
    // Log failure
    await supabase.rpc("log_telegram_command", {
      p_chat_id: ctx.chat.id,
      p_command: "/latest",
      p_processing_time_ms: Date.now() - startTime,
      p_success: false,
      p_error_message: error.message,
    });

    await ctx.reply("Sorry, I couldn't fetch the latest lead. Please try again later.");
  }
});

/**
 * /help command - Show available commands
 */
bot.command("help", async (ctx) => {
  const helpMessage = `
🤖 *PulseB2B Bot Commands*

/start - Register and get welcome message
/latest - Get the hottest lead right now
/stats - See your engagement stats
/help - Show this message

📊 *What you'll receive:*
• Daily Signal at 8 AM UTC (automatic)
• High desperation scores (70+)
• Real-time intelligence
• UTM-tracked links

💡 *Pro tip:* Click "View Full Details" to see contact info (Premium feature)

Need help? Contact support@pulseb2b.com
  `.trim();

  await ctx.replyWithMarkdown(helpMessage);
});

/**
 * /stats command - Show user engagement stats
 */
bot.command("stats", async (ctx) => {
  try {
    const chatId = ctx.chat.id;

    const { data: subscriber, error } = await supabase
      .from("telegram_subscribers")
      .select("created_at, total_commands_sent, last_interaction_at")
      .eq("chat_id", chatId)
      .single();

    if (error || !subscriber) {
      await ctx.reply("Use /start to register first!");
      return;
    }

    const daysSinceJoined = Math.floor(
      (Date.now() - new Date(subscriber.created_at).getTime()) / (1000 * 60 * 60 * 24)
    );

    const statsMessage = `
📊 *Your PulseB2B Stats*

🎯 Commands sent: ${subscriber.total_commands_sent}
📅 Member since: ${daysSinceJoined} days ago
🕐 Last active: ${new Date(subscriber.last_interaction_at).toLocaleDateString()}

Keep using /latest to stay ahead of your competition! 🚀
    `.trim();

    await ctx.replyWithMarkdown(statsMessage);

  } catch (error) {
    console.error("[/stats] Error:", error);
    await ctx.reply("Couldn't fetch stats. Please try again.");
  }
});

/**
 * Handle unknown commands
 */
bot.on("text", async (ctx) => {
  const text = ctx.message.text;
  
  if (!text.startsWith("/")) {
    return; // Ignore non-command messages
  }

  await ctx.reply(
    "Unknown command. Use /help to see available commands."
  );
});

// =====================================================
// WEBHOOK HANDLER
// =====================================================

serve(async (req) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  };

  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const startTime = Date.now();
    console.log(`[Webhook] Received ${req.method} request`);

    // Parse webhook update
    const update = await req.json();
    console.log("[Webhook] Update:", JSON.stringify(update, null, 2));

    // Process update with Telegraf
    await bot.handleUpdate(update);

    const processingTime = Date.now() - startTime;
    console.log(`[Webhook] Processed in ${processingTime}ms`);

    return new Response(
      JSON.stringify({ 
        success: true, 
        processing_time_ms: processingTime 
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      }
    );

  } catch (error) {
    console.error("[Webhook] Error:", error);
    
    // Log error but return 200 to prevent Telegram from retrying
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message 
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200, // Return 200 to prevent webhook retry storms
      }
    );
  }
});

// =====================================================
// DEPLOYMENT NOTES
// =====================================================
// 1. Deploy: supabase functions deploy telegram-webhook --no-verify-jwt
// 2. Set secrets:
//    supabase secrets set TELEGRAM_BOT_TOKEN=your_token
//    supabase secrets set FRONTEND_URL=https://pulseb2b.com
// 3. Configure webhook:
//    curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
//      -H "Content-Type: application/json" \
//      -d '{"url": "https://<project-ref>.supabase.co/functions/v1/telegram-webhook"}'
// 4. Test: Send /start to your bot on Telegram
// =====================================================
