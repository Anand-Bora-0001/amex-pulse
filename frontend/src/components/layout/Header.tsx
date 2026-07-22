/**
 * AmEx Pulse — Header Navigation
 * =================================
 * Main top navigation bar replacing the sidebar.
 */

import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Activity, Settings, LogOut, Headphones, Map } from 'lucide-react';
import type { User } from '../../types';

interface HeaderProps {
  user: User;
  onLogout: () => void;
}

export default function Header({ user, onLogout }: HeaderProps) {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/customers', icon: Users, label: 'Customers' },
    { to: '/journeys', icon: Map, label: 'Journeys' },
    { to: '/analytics', icon: Activity, label: 'Analytics' },
    { to: '/agent', icon: Headphones, label: 'Agent View' },
  ];

  return (
    <header className="header glass-header">
      <div className="header-container">
        {/* Brand */}
        <div className="header-brand">
          <div className="header-logo" />
          <h2 className="header-title">AmEx Pulse</h2>
        </div>

        {/* Navigation */}
        <nav className="header-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `header-nav-link ${isActive ? 'active' : ''}`}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User Actions */}
        <div className="header-actions">
          <NavLink to="/settings" className={({ isActive }) => `header-action-btn ${isActive ? 'active' : ''}`}>
            <Settings size={18} />
          </NavLink>

          <div className="header-user whitespace-nowrap">
            <div className="header-avatar">{user.full_name.charAt(0)}</div>
            <div className="header-user-info whitespace-nowrap">
              <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{user.full_name}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user.role}</p>
            </div>
          </div>

          <button onClick={onLogout} className="header-logout-btn" aria-label="Log Out">
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}
