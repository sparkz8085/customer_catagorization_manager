import React from 'react';
import { motion } from 'framer-motion';
import { PrismaticBurst } from '../components/AnimatedBackgrounds';

const solutions = [
  ['Retail', 'Track shopping behavior, basket preferences, and retention opportunities.', ['Loyalty segmentation', 'Promotion planning'], 'Merchandising'],
  ['Healthcare', 'Personalize patient engagement and service programs responsibly.', ['Risk-based outreach', 'Patient profiling'], 'Clinical Ops'],
  ['Banking', 'Improve customer value analysis and targeted financial services.', ['Portfolio planning', 'Upsell detection'], 'Finance Growth'],
  ['Insurance', 'Reveal policyholder patterns and premium opportunities.', ['Retention workflows', 'Cross-sell prioritization'], 'Claims Intelligence'],
  ['E-Commerce', 'Optimize campaigns using buying frequency and category affinity.', ['Cart recovery', 'Offer targeting'], 'Conversion Lift'],
  ['Education', 'Identify learner segments and personalize student journeys.', ['Engagement scoring', 'Course personalization'], 'Academic Success'],
  ['Marketing', 'Align campaigns with high-value customer groups and channels.', ['Audience building', 'Creative planning'], 'Campaign Studio'],
  ['Enterprise CRM', 'Unify customer intelligence across sales, success, and support.', ['Account scoring', 'Lifecycle automation'], 'Revenue OS'],
];

export default function SolutionsPage() {
  return (
    <section className="page-section page-with-bg">
      <PrismaticBurst />
      <div className="section-intro">
        <span className="badge">Industry Solutions</span>
        <h2>Operationalize customer categorization across every growth team.</h2>
        <p>Built to feel like a premium AI SaaS while staying adaptable to multiple business contexts and workflows.</p>
      </div>

      <div className="solutions-grid">
        {solutions.map(([name, description, benefits, useCase], index) => (
          <motion.article
            key={name}
            className="solution-card glass-panel"
            initial={{ opacity: 0, y: 22, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: index * 0.04 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <div className="solution-top">
              <span className="solution-icon">{name.slice(0, 1)}</span>
              <div>
                <h3>{name}</h3>
                <p>{description}</p>
              </div>
            </div>
            <div className="solution-list">
              <h4>Benefits</h4>
              <ul>
                {benefits.map((benefit) => (
                  <li key={benefit}>{benefit}</li>
                ))}
              </ul>
            </div>
            <div className="solution-list">
              <h4>Use Cases</h4>
              <p>{useCase}</p>
            </div>
            <a href="https://cryptox-neuron-ai.onrender.com/" className="secondary-button full-width" style={{display: 'inline-block', textAlign: 'center'}}>Explore {name}</a>
          </motion.article>
        ))}
      </div>
    </section>
  );
}