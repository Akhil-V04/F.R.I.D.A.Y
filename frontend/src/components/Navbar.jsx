import React, { useState } from 'react';
import './Navbar.css';

export default function Navbar() {
  const [activeMenu, setActiveMenu] = useState('home');

  const menuItems = [
    { id: 'home', label: '◆ HOME', icon: '▲' },
    { id: 'interface', label: '▲ INTERFACE', icon: '◈' },
    { id: 'systems', label: '◈ SYSTEMS', icon: '●' },
    { id: 'network', label: '● NETWORK', icon: '○' },
    { id: 'console', label: '○ CONSOLE', icon: '◆' },
  ];

  return (
    <nav className="sci-navbar">
      {/* Animated background elements */}
      <div className="navbar-glow"></div>
      <div className="navbar-border"></div>

      {/* Logo/Brand */}
      <div className="navbar-brand">
        <div className="brand-icon">▲</div>
        <span className="brand-text">F.R.I.D.A.Y</span>
        <div className="brand-status">● ONLINE</div>
      </div>

      {/* Menu Items */}
      <div className="navbar-menu">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`menu-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => setActiveMenu(item.id)}
          >
            <span className="menu-icon">{item.icon}</span>
            <span className="menu-label">{item.label}</span>
            {activeMenu === item.id && <div className="menu-active-line"></div>}
          </button>
        ))}
      </div>

      {/* Right side - Status indicators */}
      <div className="navbar-status">
        <div className="status-item">
          <div className="pulse-dot pulse-green"></div>
          <span>SYS OK</span>
        </div>
        <div className="status-item">
          <div className="pulse-dot pulse-cyan"></div>
          <span>NET OK</span>
        </div>
        <div className="status-separator"></div>
        <div className="nav-button">▼ MENU ▼</div>
      </div>

      {/* Scan line effect */}
      <div className="scanline"></div>
    </nav>
  );
}
