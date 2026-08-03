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
        <p>Sign in to your account or create a new session to continue.</p>

        <a href="https://cryptox-neuron-ai.onrender.com/" className="primary-button full-width" style={{display: 'inline-block', textAlign: 'center'}}>Continue to CryptoX Neuron AI</a>

        <Link to="/" className="back-link">Back to home</Link>
      </motion.div>
    </section>
  );
}
