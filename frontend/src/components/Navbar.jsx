import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

const startFreeUrl = 'https://cryptox-neuron-ai.onrender.com/';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Features', to: '/features' },
  { label: 'Solutions', to: '/solutions' },
  { label: 'Pricing', to: '/pricing' },
];

const resourceItems = [
  { label: 'Documentation', to: '/resources#documentation' },
  { label: 'API Reference', to: '/resources#api-reference' },
  { label: 'Blog', to: '/resources#blog' },
  { label: 'Tutorials', to: '/resources#tutorials' },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [resourcesOpen, setResourcesOpen] = useState(false);

  return (
    <header className="navbar-wrap">
      <div className="navbar glass-panel">
        <Link to="/" className="brand" onClick={() => setOpen(false)}>
          <span className="brand-mark">CC</span>
          <span>
            <strong>Customer Categorizer</strong>
            <small>System</small>
          </span>
        </Link>

        <button className="nav-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-label="Toggle navigation">
          <span />
          <span />
          <span />
        </button>

        <nav className={`nav-center ${open ? 'open' : ''}`}>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={() => setOpen(false)} end={item.to === '/'}>
              {item.label}
            </NavLink>
          ))}

          <div className={`nav-dropdown ${resourcesOpen ? 'open' : ''}`}>
            <button type="button" className="nav-link dropdown-trigger" onClick={() => setResourcesOpen((value) => !value)}>
              Resources
              <span>▾</span>
            </button>
            <div className="dropdown-panel">
              {resourceItems.map((item) => (
                <NavLink key={item.to} to={item.to} className="dropdown-link" onClick={() => {
                  setResourcesOpen(false);
                  setOpen(false);
                }}>
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        <div className="nav-actions">
          <NavLink to="/login" className="ghost-link" onClick={() => setOpen(false)}>
            Login
          </NavLink>
          <a href={startFreeUrl} className="primary-button" onClick={() => setOpen(false)}>
            Start for Free
          </a>
        </div>
      </div>
    </header>
  );
}