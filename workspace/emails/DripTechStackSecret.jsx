import * as React from 'react';
export default function DripTechStackSecret({ name, ctaUrl, unsubscribeUrl }) {
  return (
    <div style={{ background: '#0f172a', color: '#e0e7ef', padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2 style={{ color: '#6366f1' }}>Know their Tech Stack before you call</h2>
      <p>Hi {name}, A cold call is hard. A warm, technical pitch is easy. PulseB2B Pro gives you the exact tech stack of every lead. Imagine calling a CEO knowing they just switched to AWS and need React experts. That's the power of Pro Intelligence.</p>
      <a href={ctaUrl} style={{ display: 'inline-block', marginTop: 24, background: '#6366f1', color: '#fff', padding: '1rem 2rem', borderRadius: 8, textDecoration: 'none', fontWeight: 'bold' }}>Unlock Technical Dossiers</a>
      <p style={{ marginTop: 32, fontSize: '0.8em', color: '#64748b' }}>Unsubscribe <a href={unsubscribeUrl} style={{ color: '#6366f1' }}>here</a>.</p>
    </div>
  );
}
