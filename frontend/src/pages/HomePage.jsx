import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { DarkVeil } from '../components/AnimatedBackgrounds';

const startFreeUrl = 'https://cryptox-neuron-ai.onrender.com/';
const loginUrl = '/login';

const featureCards = [
  { title: 'AI Segmentation', description: 'Cluster customers using intelligent models and clear visual profiles.' },
  { title: 'Smart Analytics', description: 'Track purchasing behavior, preferences, and actionable trends.' },
  { title: 'Business Insights', description: 'Turn segmentation into growth opportunities with premium dashboards.' },
  { title: 'Secure Cloud', description: 'Built for secure, scalable, production-ready workflows.' },
  { title: 'Fast Predictions', description: 'Deliver real-time cluster inference with a polished interface.' },
  { title: 'Real-time Dashboard', description: 'Monitor live metrics, active models, and model health instantly.' },
];

const stats = [
  { label: 'Segments', value: '4 AI Clusters' },
  { label: 'Accuracy', value: '96.2%' },
  { label: 'Latency', value: '< 120ms' },
  { label: 'Models', value: 'Active' },
];

export default function HomePage() {
  return (
    <section className="page-section home-page">
      <DarkVeil />
      <div className="hero-grid">
        <div className="hero-copy">
          <motion.span className="badge" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            Powered by Machine Learning
          </motion.span>
          <motion.h1 initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }}>
            AI-Powered Customer Categorization
          </motion.h1>
          <motion.p className="hero-subtitle" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
            Segment, classify and analyze customers using intelligent machine learning algorithms with beautiful analytics.
          </motion.p>
          <motion.div className="hero-actions" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }}>
            <a href={startFreeUrl} className="primary-button large">Start for Free</a>
            <Link to={loginUrl} className="secondary-button large">Start Demo</Link>
          </motion.div>
          <div className="hero-stats">
            {stats.map((stat) => (
              <motion.div key={stat.label} className="stat-card glass-panel" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div className="dashboard-preview glass-panel" initial={{ opacity: 0, scale: 0.94, x: 20 }} animate={{ opacity: 1, scale: 1, x: 0 }} transition={{ delay: 0.14 }}>
          <div className="dashboard-header">
            <div>
              <p>Premium AI Dashboard</p>
              <h3>Customer Intelligence</h3>
            </div>
            <span className="live-pill">Live</span>
          </div>
          <div className="dashboard-grid">
            <div className="mini-card accent-card">
              <span>Customer Segmentation</span> 
              <strong>Budget / Regular / Premium / Occasional</strong>
            </div>
            <div className="mini-card">
              <span>AI Predictions</span>
              <strong>Cluster: Premium</strong>
            </div>
            <div className="mini-card wide">
              <span>Customer Distribution</span>
              <div className="distribution-bars">
                <i style={{ width: '25%' }} /><strong style={{ width: '25%' }}>Budget[25%]</strong>
                <i style={{ width: '20%' }} /><strong style={{ width: '20%' }}>Regular[20%]</strong>
                <i style={{ width: '40%' }} /><strong style={{ width: '40%' }}>Premium[40%]</strong>
                <i style={{ width: '15%' }} /><strong style={{ width: '15%' }}>Occasional[15%]</strong>
              </div>
            </div>
            <div className="mini-card">
              <span>Active Models</span>
              <strong>Training + Prediction</strong>
            </div>
            <div className="mini-card">
              <span>Customer Distribution</span>
              <strong>25% / 20% / 40% / 15%</strong>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="feature-grid stagger-grid">
        {featureCards.map((feature, index) => (
          <motion.article
            key={feature.title}
            className="feature-card glass-panel"
            initial={{ opacity: 0, y: 22, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.08 + index * 0.04 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <span className="feature-index">0{index + 1}</span>
            <h4>{feature.title}</h4>
            <p>{feature.description}</p>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
