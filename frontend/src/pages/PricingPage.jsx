import React from 'react';
import { motion } from 'framer-motion';
import { Hyperspeed } from '../components/AnimatedBackgrounds';

const plans = [
  {
    name: 'Starter',
    price: 'Free',
    audience: 'For individuals getting a customer workspace running.',
    features: ['Customer management', 'Basic AI analysis', 'Basic history', 'Basic reports'],
    cta: 'Start for Free',
  },
  {
    name: 'Professional',
    price: 'Contact sales',
    audience: 'For teams that need repeatable analysis and bulk workflows.',
    features: ['Everything in Starter', 'Bulk analysis', 'Complete history', 'Advanced reports'],
    featured: true,
    cta: 'Request upgrade',
  },
  {
    name: 'Enterprise',
    price: 'Tailored plan',
    audience: 'For organizations with shared intelligence and reporting needs.',
    features: ['Everything in Professional', 'Organization features', 'Enterprise reporting', 'Higher usage capacity'],
    cta: 'Contact sales',
  },
];

export default function PricingPage() {
  return (
    <section className="page-section page-with-bg pricing-page">
      <Hyperspeed />
      <div className="section-intro">
        <span className="badge">Pricing</span>
        <h2>Flexible plans for modern teams scaling customer intelligence.</h2>
        <p>Choose the right plan for your growth stage with a polished, conversion-friendly layout.</p>
      </div>
      <div className="pricing-grid">
        {plans.map((plan, index) => (
          <motion.article
            key={plan.name}
            className={`pricing-card glass-panel ${plan.featured ? 'featured' : ''}`}
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            {plan.featured && <span className="featured-tag">Most Popular</span>}
            <h3>{plan.name}</h3>
            <div className="plan-price">{plan.price}</div>
            <p>{plan.audience}</p>
            <ul>
              {plan.features.map((feature) => (
                <li key={feature}>✔ {feature}</li>
              ))}
            </ul>
            <a href="https://cryptox-neuron-ai.onrender.com/" className={plan.featured ? 'primary-button full-width' : 'secondary-button full-width'} style={{display: 'inline-block', textAlign: 'center'}}>
              {plan.cta}
            </a>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
