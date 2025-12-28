from flask import Blueprint, request, jsonify, session
import stripe
import os
from models.user import User

webhook = Blueprint('webhook', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...')

# Simulación de base de datos de usuarios (en producción, usar DB real)
USER_DB = {}

def update_user_subscription(user_id, customer_id=None, subscription_id=None, plan_type=None):
    # Actualiza el usuario en la "base de datos"
    user = USER_DB.get(user_id) or {}
    if customer_id:
        user['stripe_customer_id'] = customer_id
    if subscription_id:
        user['stripe_subscription_id'] = subscription_id
    if plan_type:
        user['plan_type'] = plan_type
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
        update_user_subscription(user_id, customer_id, subscription_id, plan_type='pro')
    elif event['type'] == 'customer.subscription.deleted':
        sub = event['data']['object']
        # Buscar usuario por subscription_id
        for uid, u in USER_DB.items():
            if u.get('stripe_subscription_id') == sub['id']:
                update_user_subscription(uid, plan_type='free')
    # Puedes manejar más eventos según necesidad
    return '', 200
