from flask import Blueprint, request, jsonify, session
import stripe
import os

billing = Blueprint('billing', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

@billing.route('/api/billing/create-checkout-session', methods=['POST'])
def create_checkout_session():
    user = session.get('user')
    if not user or not user.get('id'):
        return jsonify({'error': 'Not authenticated'}), 401
    # Prevent multiple sessions (simple demo: could use a DB or cache in prod)
    if session.get('checkout_in_progress'):
        return jsonify({'error': 'Checkout already in progress'}), 429
    session['checkout_in_progress'] = True
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': os.environ.get('STRIPE_PRO_PRICE_ID', 'price_123'),
                'quantity': 1,
            }],
            client_reference_id=str(user['id']),
            customer_email=user.get('email'),
            allow_promotion_codes=True,
            success_url=os.environ.get('STRIPE_SUCCESS_URL', 'http://localhost:5000/payment-success'),
            cancel_url=os.environ.get('STRIPE_CANCEL_URL', 'http://localhost:5000/dashboard'),
            metadata={'user_id': user['id']}
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.pop('checkout_in_progress', None)
