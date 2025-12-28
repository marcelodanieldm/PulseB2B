// api/emails/sendTransactional.js
// Sends transactional onboarding email via Resend

const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

/**
 * Send onboarding email to new Enterprise user
 * @param {string} to - recipient email
 * @param {string} name - recipient name
 * @param {string} docsUrl - direct, authenticated docs link
 */
async function sendEnterpriseOnboarding(to, name, docsUrl) {
  const html = `
    <div style="background:#0f172a;padding:2rem;font-family:sans-serif;color:#e0e7ef">
      <h1 style="color:#6366f1;">Welcome to Enterprise, ${name}!</h1>
      <p>Your API Documentation and Webhooks are now live.</p>
      <a href="${docsUrl}?utm_source=email&utm_campaign=onboarding" style="display:inline-block;margin-top:1.5rem;padding:1rem 2rem;background:#6366f1;color:#fff;border-radius:8px;text-decoration:none;font-weight:bold;">Access API Docs</a>
      <p style="margin-top:2rem;font-size:0.9em;color:#64748b;">If you did not request this, please ignore this email.</p>
      <p style="margin-top:2rem;font-size:0.8em;color:#64748b;">Unsubscribe <a href="${process.env.UNSUBSCRIBE_URL}?email=${encodeURIComponent(to)}" style="color:#6366f1;">here</a>.</p>
    </div>
  `;
  return resend.emails.send({
    from: 'PulseB2B <noreply@pulseb2b.com>',
    to,
    subject: 'Welcome to Enterprise – Your API is Live',
    html,
  });
}

module.exports = { sendEnterpriseOnboarding };
