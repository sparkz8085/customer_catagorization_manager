import React from 'react';
import { motion } from 'framer-motion';
import { PrismaticBurst } from '../components/AnimatedBackgrounds';

const features = [
  ['AI Categorization', 'Convert raw customer data into meaningful, revenue-focused clusters.', '01'],
  ['Dashboard Analytics', 'Interactive visual panels for tracking performance and behavior.', '02'],
  ['Machine Learning Models', 'Reliable inference flow with clear prediction states.', '03'],
  ['Business Intelligence', 'See the commercial impact of customer behavior at a glance.', '04'],
  ['Customer Insights', 'Understand spending, loyalty, and channel preferences.', '05'],
  ['Security', 'Preserve data integrity and a trust-first user experience.', '06'],
  ['Cloud Storage', 'Ready for scalable cloud workflows and persistence.', '07'],
  ['Export Reports', 'Package insights for teams and stakeholders in one click.', '08'],
];

export default function FeaturesPage() {
  return (
    <section className="page-section page-with-bg">
      <PrismaticBurst />
      <div className="section-intro">
        <span className="badge">Platform Capabilities</span>
        <h2>Feature-rich AI operations for modern customer intelligence.</h2>
        <p>Every capability is designed as a polished SaaS experience with elegant motion and enterprise-grade clarity.</p>
      </div>
      <div className="feature-detail-grid">
        {features.map(([title, description, index], position) => (
          <motion.article
            key={title}
            className="detail-card glass-panel"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: position * 0.05 }}
            whileHover={{ y: -8, scale: 1.01 }}
          >
            <div className="detail-card-top">
              <span className="detail-icon">✦</span>
              <span className="detail-number">{index}</span>
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
            <div className="detail-illustration">
              <div className="illus-core" />
              <div className="illus-line" />
              <div className="illus-chip" />
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  );
}