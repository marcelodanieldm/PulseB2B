# Enterprise Success Journey Automation

This document describes the backend and frontend automation for the post-payment flow when a user upgrades to the Enterprise plan ($199/mo).

## Workflow Overview

1. **Stripe Webhook**
   - Listens for `checkout.session.completed` events.
   - Checks if the purchased item matches the Enterprise price ID.
   - Updates the user's `plan_type` to `enterprise` and generates a unique `API_CLIENT_ID`.

2. **Redirect Logic**
   - After successful payment, the user is redirected to `/dashboard/settings/api?status=unlocked`.

3. **In-App Notification**
   - Triggers a confetti animation and a personalized toast: "Welcome to Enterprise. Your API Documentation and Webhooks are now live."

4. **Email Trigger (Resend)**
   - Sends an 'Enterprise Onboarding' email with a direct, authenticated link to the unlocked documentation.

## Implementation Details

### Stripe Webhook (`backend/views/webhook.py`)
- Handles `checkout.session.completed` events.
- Checks for the Enterprise price ID in the session's line items.
- Updates the user record and generates an `API_CLIENT_ID`.
- Triggers downstream effects (notification, email).

### User Model (`backend/models/user.py`)
- Stores `plan_type`, `API_CLIENT_ID`, and Stripe metadata.

### Frontend
- On redirect, shows confetti and toast notification.
- Documentation and webhooks become accessible immediately.

### Email (Resend)
- Sends onboarding email with a secure link to `/docs/api`.

---

**Note:** Replace mock values and logic with production-ready database and secure API integrations as needed.
