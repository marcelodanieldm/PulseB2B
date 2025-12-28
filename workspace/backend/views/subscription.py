from flask import Blueprint, request, jsonify, session
import stripe
import os

subscription = Blueprint('subscription', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

@subscription.route('/api/billing/create-customer-portal', methods=['POST'])
def create_customer_portal():
    user = session.get('user')
    if not user or not user.get('id'):
        return jsonify({'error': 'Not authenticated'}), 401
    customer_id = user.get('stripe_customer_id')
    if not customer_id:
        return jsonify({'error': 'No Stripe customer ID found'}), 400
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=os.environ.get('STRIPE_PORTAL_RETURN_URL', 'http://localhost:5000/dashboard')
        )
        return jsonify({'url': portal_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription.route('/api/billing/cancel-subscription', methods=['POST'])
def cancel_subscription():
    user = session.get('user')
    if not user or not user.get('id'):
        return jsonify({'error': 'Not authenticated'}), 401
    subscription_id = user.get('stripe_subscription_id')
    if not subscription_id:
        return jsonify({'error': 'No Stripe subscription ID found'}), 400
    try:
        stripe.Subscription.delete(subscription_id)
        return jsonify({'status': 'cancelled'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
