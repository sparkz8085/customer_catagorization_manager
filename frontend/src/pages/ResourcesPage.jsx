import React from 'react';
import { motion } from 'framer-motion';

const resourceSections = [
  ['documentation', 'Documentation', 'Read the platform overview, setup flow, and usage notes.'],
  ['api-reference', 'API Reference', 'Inspect integration points and backend endpoints.'],
  ['blog', 'Blog', 'Explore product stories, updates, and implementation ideas.'],
  ['tutorials', 'Tutorials', 'Step-by-step guides for onboarding and operations.'],
  ['faqs', 'FAQs', 'Answers to common product and deployment questions.'],
  ['support-center', 'Support Center', 'Get help with setup, billing, and troubleshooting.'],
  ['github-repository', 'GitHub Repository', 'Track source, issues, and contribution workflows.'],
  ['downloads', 'Downloads', 'Access assets, exports, and installation bundles.'],
];

export default function ResourcesPage() {
  return (
    <section className="page-section resources-page">
      <div className="section-intro compact">
        <span className="badge">Resources</span>
        <h2>Clear documentation for teams moving fast.</h2>
        <p>A clean, premium resource center designed for product discovery, onboarding, and support.</p>
      </div>

      <div className="resources-stack">
        {resourceSections.map(([id, title, description], index) => (
          <motion.article
            id={id}
            key={title}
            className="resource-card glass-panel"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ y: -6, scale: 1.01 }}
          >
            <div>
              <span className="resource-index">0{index + 1}</span>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
            <button type="button" className="secondary-button">Open</button>
          </motion.article>
        ))}
      </div>
    </section>
  );
}