import React, { useState } from 'react';

const links = [
  { label: 'About', href: '/' },
  { label: 'Privacy Policy', href: '/resources#documentation' },
  { label: 'Terms', href: '/resources#faqs' },
  { label: 'Contact', href: 'kunalsarkar61570@gmail.com' },
  { label: 'GitHub', href: 'https://github.com/sparkz8085' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com' },
  { label: 'Email', href: 'mailto:hello@customercategorizer.ai' },
];

export default function Footer() {
  const [email, setEmail] = useState('');

  const bottomLinks = [
    { label: 'Privacy Policy', href: '/resources#documentation' },
    { label: 'Terms of Service', href: '/resources#faqs' },
  ];

  function handleSubscribe(e) {
    e.preventDefault();
    // placeholder: integrate with real subscription endpoint
    setEmail('');
    // could show a toast or success state
  }

  return (
    <footer className="footer" role="contentinfo">
      <div className="footer-inner glass-panel">
        <div className="footer-grid">
          <div className="footer-left">
            <div className="brand">
              <div className="brand-icon">📊</div>
              <div>
                <p className="footer-title">CustomerIQ</p>
                <p className="footer-copy">AI-powered customer intelligence platform that helps businesses understand, segment, and engage customers smarter.</p>
              </div>
            </div>

            <div className="footer-social">
                {(
                  [
                    { label: 'LinkedIn', href: 'https://www.linkedin.com' },
                    { label: 'Twitter', href: 'https://twitter.com' },
                    { label: 'Facebook', href: 'https://facebook.com' },
                    { label: 'Email', href: 'mailto:hello@customercategorizer.ai' },
                  ]
                ).map((s) => (
                  <a
                    key={s.label}
                    className="social-button"
                    href={s.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={s.label}
                  >
                    {renderIcon(s.label)}
                  </a>
                ))}
            </div>
          </div>

          <div className="footer-right">
            <h3 className="footer-section-title">Stay Updated</h3>
            <p className="footer-copy">Subscribe to our newsletter for the latest insights and product updates.</p>
            <form className="newsletter" onSubmit={handleSubscribe}>
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                aria-label="Email address"
                required
              />
              <button aria-label="Subscribe" type="submit">→</button>
            </form>
          </div>
        </div>

        <div className="footer-divider" />

        <div className="footer-bottom">
          <p className="footer-copy">{`© ${new Date().getFullYear()} cryptoxneuron©. All rights reserved.`}</p>
          <div className="footer-bottom-links">
            {bottomLinks.map((l, i) => (
              <a key={l.label} href={l.href} aria-label={l.label}>{l.label}</a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}

function renderIcon(label) {
  const common = { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' };
  switch (label) {
    case 'LinkedIn':
      return (
        <svg {...common} aria-hidden="true">
          <title>LinkedIn</title>
          <rect width="24" height="24" fill="none" />
          <path d="M4.98 3.5C4.98 4.604 4.06 5.5 2.99 5.5 1.92 5.5 1 4.604 1 3.5 1 2.396 1.92 1.5 2.99 1.5 4.06 1.5 4.98 2.396 4.98 3.5zM.5 8.999h4.98V23H.5V8.999zM8.5 9.001h4.78v1.91h.07c.67-1.27 2.3-2.61 4.73-2.61 5.06 0 6 3.33 6 7.66V23h-4.98v-6.16c0-1.47-.03-3.36-2.05-3.36-2.05 0-2.36 1.59-2.36 3.24V23H8.5V9.001z" fill="currentColor" />
        </svg>
      );
    case 'Twitter':
      return (
        <svg {...common} aria-hidden="true">
          <title>Twitter</title>
          <path d="M22 5.92c-.63.28-1.3.47-2 .56.72-.43 1.27-1.11 1.53-1.93-.68.4-1.44.69-2.25.85C18.9 4.5 17.95 4 16.88 4c-1.6 0-2.9 1.3-2.9 2.9 0 .23.03.45.08.66C10.1 7.44 6.2 5.2 3.6 2.1c-.25.44-.39.95-.39 1.5 0 1.03.52 1.94 1.33 2.47-.48-.02-.93-.15-1.33-.37v.04c0 1.4.99 2.57 2.31 2.84-.24.06-.5.09-.77.09-.19 0-.38-.02-.57-.05.38 1.2 1.48 2.08 2.78 2.11-1.02.8-2.31 1.28-3.72 1.28-.24 0-.48-.01-.71-.04 1.33.85 2.91 1.35 4.61 1.35 5.53 0 8.56-4.58 8.56-8.56v-.39c.58-.42 1.07-.95 1.46-1.56-.53.24-1.1.4-1.7.47z" fill="currentColor" />
        </svg>
      );
    case 'Facebook':
      return (
        <svg {...common} aria-hidden="true">
          <title>Facebook</title>
          <path d="M22 12.07C22 6.54 17.52 2 12 2S2 6.54 2 12.07C2 17.02 5.66 21.1 10.44 21.95v-6.96H8.07v-2.92h2.37V9.8c0-2.34 1.38-3.63 3.5-3.63.99 0 2.03.18 2.03.18v2.23h-1.14c-1.12 0-1.46.69-1.46 1.4v1.68h2.49l-.4 2.92h-2.09v6.96C18.34 21.1 22 17.02 22 12.07z" fill="currentColor" />
        </svg>
      );
    case 'Email':
      return (
        <svg {...common} aria-hidden="true">
          <title>Email</title>
          <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5L4 8V6l8 5 8-5v2z" fill="currentColor" />
        </svg>
      );
    default:
      return null;
  }
}