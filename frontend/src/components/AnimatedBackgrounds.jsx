import React from 'react';

export function DarkVeil() {
  return (
    <div className="animated-bg dark-veil">
      <span className="veil-orb orb-a" />
      <span className="veil-orb orb-b" />
      <span className="veil-orb orb-c" />
      <span className="veil-grid" />
    </div>
  );
}

export function PrismaticBurst() {
  return (
    <div className="animated-bg prismatic-burst">
      <span className="burst-ring ring-a" />
      <span className="burst-ring ring-b" />
      <span className="burst-ring ring-c" />
      <span className="burst-sheen" />
    </div>
  );
}

export function Hyperspeed() {
  return (
    <div className="animated-bg hyperspeed">
      <span className="speed-line line-a" />
      <span className="speed-line line-b" />
      <span className="speed-line line-c" />
      <span className="speed-line line-d" />
    </div>
  );
}