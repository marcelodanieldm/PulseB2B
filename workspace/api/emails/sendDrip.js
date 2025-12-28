// api/emails/sendDrip.js
// Sends drip marketing emails via Resend

const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

/**
 * Send a drip email to a user
 * @param {string} to - recipient email
 * @param {string} name - recipient name
 * @param {string} subject - email subject
 * @param {string} html - email HTML content
 */
async function sendDripEmail(to, name, subject, html) {
  return resend.emails.send({
    from: 'PulseB2B <noreply@pulseb2b.com>',
    to,
    subject,
    html,
  });
}

module.exports = { sendDripEmail };
