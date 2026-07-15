import React from 'react';
import { NavLink } from 'react-router-dom';

const dockItems = [
  { icon: '🏠', label: 'Home', to: '/' },
  { icon: '✨', label: 'Features', to: '/features' },
  { icon: '🧠', label: 'Solutions', to: '/solutions' },
  { icon: '💰', label: 'Pricing', to: '/pricing' },
  { icon: '📚', label: 'Resources', to: '/resources' },
];

export default function BottomDock() {
  return (
    <div className="bottom-dock-wrap">
      <nav className="bottom-dock glass-panel">
        {dockItems.map((item) => (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => `dock-item ${isActive ? 'active' : ''}`} end={item.to === '/'}>
            <span className="dock-icon">{item.icon}</span>
            <span className="dock-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}