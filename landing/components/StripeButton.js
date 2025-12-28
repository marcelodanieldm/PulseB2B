import { loadStripe } from '@stripe/stripe-js';
import { useState } from 'react';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

export default function StripeButton({ priceId }) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);
    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceId }),
    });
    const { sessionId } = await res.json();
    const stripe = await stripePromise;
    await stripe.redirectToCheckout({ sessionId });
    setLoading(false);
  };

  return (
    <button
      onClick={handleCheckout}
      disabled={loading}
      className="px-8 py-3 bg-indigo-500 text-white rounded-full font-semibold shadow-lg hover:bg-indigo-600 transition mt-4"
    >
      {loading ? 'Redirecting...' : 'Start for $29/mo'}
    </button>
  );
}
