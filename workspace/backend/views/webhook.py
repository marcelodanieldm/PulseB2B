from flask import Blueprint, request, jsonify, session

import stripe
import os
import uuid
from models.user import User

webhook = Blueprint('webhook', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...')

# Simulación de base de datos de usuarios (en producción, usar DB real)
USER_DB = {}

def update_user_subscription(user_id, customer_id=None, subscription_id=None, plan_type=None, api_client_id=None):
    # Actualiza el usuario en la "base de datos"
    user = USER_DB.get(user_id) or {}
    if customer_id:
        user['stripe_customer_id'] = customer_id
    if subscription_id:
        user['stripe_subscription_id'] = subscription_id
    if plan_type:
        user['plan_type'] = plan_type
    if api_client_id:
        user['api_client_id'] = api_client_id
    USER_DB[user_id] = user

@webhook.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Manejo de eventos relevantes
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        user_id = session_obj.get('client_reference_id')
        customer_id = session_obj.get('customer')
        subscription_id = session_obj.get('subscription')
        # --- UPGRADE LOGIC ---
        # Check for Enterprise price (mock: price_id == 'price_enterprise')
        line_items = session_obj.get('display_items', []) or session_obj.get('line_items', [])
        is_enterprise = False
        for item in line_items:
            price_id = item.get('price', {}).get('id') or item.get('price', {}).get('price')
            if price_id == 'price_enterprise':
                is_enterprise = True
        if is_enterprise:
            api_client_id = str(uuid.uuid4())
            update_user_subscription(user_id, customer_id, subscription_id, plan_type='enterprise', api_client_id=api_client_id)
            # Trigger onboarding email (mock call)
            try:
                import subprocess
                subprocess.Popen([
                    'node',
                    'api/emails/sendTransactional.js',
                    USER_DB[user_id].get('email', 'test@pulseb2b.com'),
                    USER_DB[user_id].get('name', 'User'),
                    'https://pulseb2b.com/docs/api'
                ])
            except Exception as e:
                print('Failed to send onboarding email:', e)
        else:
            update_user_subscription(user_id, customer_id, subscription_id, plan_type='pro')
    elif event['type'] == 'customer.subscription.deleted':
        sub = event['data']['object']
        # Buscar usuario por subscription_id
        for uid, u in USER_DB.items():
            if u.get('stripe_subscription_id') == sub['id']:
                update_user_subscription(uid, plan_type='free')
    # Puedes manejar más eventos según necesidad
    return '', 200
