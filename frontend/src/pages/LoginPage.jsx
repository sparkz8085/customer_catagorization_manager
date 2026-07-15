import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

export default function LoginPage() {
  return (
    <section className="page-section login-page">
      <motion.div
        className="login-panel glass-panel"
        initial={{ opacity: 0, y: 18, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.35 }}
      >
        <span className="badge">Secure Access</span>
        <h2>Welcome back</h2>
        <p>Use the existing backend login flow while enjoying the new premium SaaS experience.</p>

        <div className="login-actions">
          <a className="oauth-button google" href="/login/google">Continue with Google</a>
        </div>

        <div className="login-divider">or</div>

        <form className="login-form" action="/login/email" method="post">
          <label>
            Full Name
            <input type="text" name="name" placeholder="Enter your name" required />
          </label>
          <label>
            Email
            <input type="email" name="email" placeholder="name@company.com" required />
          </label>
          <label>
            Nickname
            <input type="text" name="nickname" placeholder="Your display name" />
          </label>
          <label>
            Password
            <input type="password" name="password" placeholder="Create a password" />
          </label>
          <button type="submit" className="primary-button full-width">Create Session</button>
        </form>

        <Link to="/" className="back-link">Back to home</Link>
      </motion.div>
    </section>
  );
}