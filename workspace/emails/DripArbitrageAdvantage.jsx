import * as React from 'react';
export default function DripArbitrageAdvantage({ name, ctaUrl, unsubscribeUrl }) {
  return (
    <div style={{ background: '#0f172a', color: '#e0e7ef', padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2 style={{ color: '#6366f1' }}>The math behind PulseB2B: Why $29 is a no-brainer</h2>
      <p>Hi {name}, Hiring a Senior Dev in San Francisco: $180k/year. Hiring the same talent in LATAM via PulseB2B: $60k/year. Startups know this. They are looking for partners like you right now. PulseB2B finds them exactly when their budget is ready. Stop guessing and start closing.</p>
      <a href={ctaUrl} style={{ display: 'inline-block', marginTop: 24, background: '#6366f1', color: '#fff', padding: '1rem 2rem', borderRadius: 8, textDecoration: 'none', fontWeight: 'bold' }}>Upgrade to Pro</a>
      <p style={{ marginTop: 32, fontSize: '0.8em', color: '#64748b' }}>Unsubscribe <a href={unsubscribeUrl} style={{ color: '#6366f1' }}>here</a>.</p>
    </div>
  );
}
