import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Activity, BarChart3, BrainCircuit, Clock3, Layers3, ShieldCheck, Zap } from 'lucide-react';
import { DarkVeil } from '../components/AnimatedBackgrounds';

const startFreeUrl = 'https://cryptox-neuron-ai.onrender.com/login';
const loginUrl = '/login';

const featureCards = [
  { title: 'AI Segmentation', description: 'Cluster customers using intelligent models and clear visual profiles.', icon: BrainCircuit },
  { title: 'Smart Analytics', description: 'Track purchasing behavior, preferences, and actionable trends.', icon: BarChart3 },
  { title: 'Business Insights', description: 'Turn segmentation into growth opportunities with premium dashboards.', icon: Activity },
  { title: 'Secure Cloud', description: 'Built for secure, scalable, production-ready workflows.', icon: ShieldCheck },
  { title: 'Fast Predictions', description: 'Deliver real-time cluster inference with a polished interface.', icon: Zap },
  { title: 'Real-time Dashboard', description: 'Monitor live metrics, active models, and model health instantly.', icon: Layers3 },
];

const stats = [
  { label: 'Segments', value: '4 AI Clusters', icon: Layers3 },
  { label: 'Accuracy', value: '96.2%', icon: ShieldCheck },
  { label: 'Latency', value: '< 120ms', icon: Clock3 },
  { label: 'Models', value: 'Active', icon: Activity },
];

const distributionBars = [
  { label: 'Budget[25%]', widthClass: 'bar-25' },
  { label: 'Regular[20%]', widthClass: 'bar-20' },
  { label: 'Premium[40%]', widthClass: 'bar-40' },
  { label: 'Occasional[15%]', widthClass: 'bar-15' },
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
                <span className="stat-icon"><stat.icon size={16} strokeWidth={2} aria-hidden="true" /></span>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div className="dashboard-preview glass-panel" initial={{ opacity: 0, scale: 0.94, x: 20 }} animate={{ opacity: 1, scale: 1, x: 0 }} transition={{ delay: 0.14 }}>
          <div className="dashboard-header">
            <div className="dashboard-title">
              <span className="panel-icon"><BarChart3 size={16} strokeWidth={2} aria-hidden="true" /></span>
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
                {distributionBars.map((bar) => (
                  <div key={bar.label} className="distribution-row">
                    <i className={bar.widthClass} aria-hidden="true" />
                    <strong>{bar.label}</strong>
                  </div>
                ))}
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
            <div className="card-headline">
              <span className="card-icon"><feature.icon size={18} strokeWidth={2} aria-hidden="true" /></span>
              <span className="feature-index">0{index + 1}</span>
            </div>
            <h4>{feature.title}</h4>
            <p>{feature.description}</p>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
