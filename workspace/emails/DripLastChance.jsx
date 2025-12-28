import * as React from 'react';
export default function DripLastChance({ name, ctaUrl, unsubscribeUrl }) {
  return (
    <div style={{ background: '#0f172a', color: '#e0e7ef', padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2 style={{ color: '#6366f1' }}>Is your $29 Founding Member discount expiring?</h2>
      <p>Hi {name}, We launched PulseB2B with a special $29/mo price for our first 50 members. We are almost at capacity. This is your last chance to lock in this price forever. After this, the price returns to $49/mo. Secure your advantage now and never miss a signal again.</p>
      <a href={ctaUrl} style={{ display: 'inline-block', marginTop: 24, background: '#6366f1', color: '#fff', padding: '1rem 2rem', borderRadius: 8, textDecoration: 'none', fontWeight: 'bold' }}>Lock in $29/mo Forever</a>
      <p style={{ marginTop: 32, fontSize: '0.8em', color: '#64748b' }}>Unsubscribe <a href={unsubscribeUrl} style={{ color: '#6366f1' }}>here</a>.</p>
    </div>
  );
}
