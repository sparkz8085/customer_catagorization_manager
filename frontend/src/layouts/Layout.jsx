import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import BottomDock from '../components/BottomDock';
import Footer from '../components/Footer';

export default function Layout() {
  return (
    <div className="app-shell">
      <div className="app-backdrop" />
      <Navbar />
      <main className="app-main">
        <Outlet />
      </main>
      <Footer />
      <BottomDock />
    </div>
  );
}