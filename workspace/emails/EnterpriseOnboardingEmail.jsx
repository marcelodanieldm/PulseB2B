import * as React from 'react';

export default function EnterpriseOnboardingEmail({ name, docsUrl, unsubscribeUrl }) {
  return (
    <div style={{ background: '#0f172a', padding: '2rem', fontFamily: 'sans-serif', color: '#e0e7ef' }}>
      <h1 style={{ color: '#6366f1' }}>Welcome to Enterprise, {name}!</h1>
      <p>Your API Documentation and Webhooks are now live.</p>
      <a href={`${docsUrl}?utm_source=email&utm_campaign=onboarding`} style={{ display: 'inline-block', marginTop: '1.5rem', padding: '1rem 2rem', background: '#6366f1', color: '#fff', borderRadius: 8, textDecoration: 'none', fontWeight: 'bold' }}>
        Access API Docs
      </a>
      <p style={{ marginTop: '2rem', fontSize: '0.9em', color: '#64748b' }}>If you did not request this, please ignore this email.</p>
      <p style={{ marginTop: '2rem', fontSize: '0.8em', color: '#64748b' }}>
        Unsubscribe <a href={unsubscribeUrl} style={{ color: '#6366f1' }}>here</a>.
      </p>
    </div>
  );
}
