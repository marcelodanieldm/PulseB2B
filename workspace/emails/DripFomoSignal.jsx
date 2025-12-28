import * as React from 'react';
export default function DripFomoSignal({ name, ctaUrl, unsubscribeUrl }) {
  return (
    <div style={{ background: '#0f172a', color: '#e0e7ef', padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2 style={{ color: '#6366f1' }}>5 Startups just raised $10M+. Do you have their CTO's email?</h2>
      <p>Hi {name}, The market moves fast. In the last 48 hours, our radar detected 5 new Series A rounds in your target region. Your competitors are already reaching out. Are you? Upgrade to Pro today to get verified emails and direct phones for every lead we find.</p>
      <a href={ctaUrl} style={{ display: 'inline-block', marginTop: 24, background: '#6366f1', color: '#fff', padding: '1rem 2rem', borderRadius: 8, textDecoration: 'none', fontWeight: 'bold' }}>Get Pro Access Now</a>
      <p style={{ marginTop: 32, fontSize: '0.8em', color: '#64748b' }}>Unsubscribe <a href={unsubscribeUrl} style={{ color: '#6366f1' }}>here</a>.</p>
    </div>
  );
}
