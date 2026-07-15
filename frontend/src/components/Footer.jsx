import React from 'react';

const links = [
  { label: 'About', href: '/' },
  { label: 'Privacy Policy', href: '/resources#documentation' },
  { label: 'Terms', href: '/resources#faqs' },
  { label: 'Contact', href: 'mailto:support@customercategorizer.ai' },
  { label: 'GitHub', href: 'https://github.com/sparkz8085/customer_catagorization_manager' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com' },
  { label: 'Email', href: 'mailto:hello@customercategorizer.ai' },
];

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner glass-panel">
        <div>
          <p className="footer-title">Customer Categorizer System</p>
          <p className="footer-copy">Premium AI SaaS for intelligent customer segmentation and analytics.</p>
        </div>
        <div className="footer-links">
          {links.map((link) => (
            <a key={link.label} href={link.href} target={link.href.startsWith('http') ? '_blank' : undefined} rel={link.href.startsWith('http') ? 'noreferrer' : undefined}>
              {link.label}
            </a>
          ))}
        </div>
        <p className="footer-copy">Copyright {new Date().getFullYear()} Customer Categorizer System. All rights reserved.</p>
      </div>
    </footer>
  );
}