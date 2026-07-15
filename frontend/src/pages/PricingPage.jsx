import React from 'react';
import { motion } from 'framer-motion';
import { Hyperspeed } from '../components/AnimatedBackgrounds';

const plans = [
  {
    name: 'Starter',
    price: '₹0/month',
    features: ['Basic Analytics', 'Demo Dataset', 'Community Support'],
  },
  {
    name: 'Professional',
    price: '₹999/month',
    features: ['Unlimited Customers', 'AI Predictions', 'Reports', 'API Access'],
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom Pricing',
    features: ['Dedicated AI Models', 'Custom Integrations', 'Priority Support', 'Team Management'],
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
            <ul>
              {plan.features.map((feature) => (
                <li key={feature}>✔ {feature}</li>
              ))}
            </ul>
            <button type="button" className={plan.featured ? 'primary-button full-width' : 'secondary-button full-width'}>
              {plan.featured ? 'Get Started' : 'Choose Plan'}
            </button>
          </motion.article>
        ))}
      </div>
    </section>
  );
}