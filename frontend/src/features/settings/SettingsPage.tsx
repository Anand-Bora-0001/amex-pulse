/**
 * AmEx Pulse — Settings Page
 * ============================
 * Theme toggle, user preferences, system info.
 */

import { Info, Shield, Palette, CheckCircle2 } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="page-container space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Settings</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Configure your dashboard experience</p>
      </div>

      {/* Appearance */}
      <div className="stat-card">
        <div className="flex items-center gap-3 mb-4">
          <Palette size={20} className="text-purple-500" />
          <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Appearance</h3>
        </div>
        <div className="flex items-center justify-between p-4 rounded-xl" style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)' }}>
          <div>
            <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>Theme</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Switch between light and dark mode</p>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="stat-card">
        <div className="flex items-center gap-3 mb-4">
          <Info size={20} className="text-blue-500" />
          <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>System Information</h3>
        </div>
        <div className="space-y-3">
          {[
            { label: 'Application', value: 'AmEx Pulse v1.0.0' },
            { label: 'Platform', value: 'AI-Powered Customer Journey Intelligence' },
            { label: 'Backend', value: 'FastAPI + Python 3.12' },
            { label: 'Frontend', value: 'React 18 + TypeScript + Vite' },
            { label: 'AI Engine', value: '8 ML Modules (Intent, Frustration, Health, Churn, NBA, Summary)' },
            { label: 'Database', value: 'SQLite (Demo) / PostgreSQL (Production)' },
            { label: 'Hackathon', value: 'American Express CodeStreet 2026' },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border-color)' }}>
              <span className="text-sm" style={{ color: 'var(--text-muted)' }}>{item.label}</span>
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Security */}
      <div className="stat-card">
        <div className="flex items-center gap-3 mb-4">
          <Shield size={20} className="text-green-500" />
          <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Security</h3>
        </div>
        <div className="space-y-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          <p className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-500" /> JWT Authentication with RBAC</p>
          <p className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-500" /> Bcrypt Password Hashing</p>
          <p className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-500" /> Audit Logging Enabled</p>
          <p className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-500" /> CORS Policy Configured</p>
          <p className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-500" /> Input Validation (Pydantic)</p>
        </div>
      </div>
    </div>
  );
}
