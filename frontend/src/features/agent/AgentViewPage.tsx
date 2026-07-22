/**
 * AmEx Pulse — Agent View Page
 * ==============================
 * Support agent workspace with customer queue and AI recommendations.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Headphones, AlertTriangle, Clock, Bot, Phone, CheckCircle } from 'lucide-react';
import { customerApi, dashboardApi } from '../../lib/api';
import { getScoreColor, getRiskColor } from '../../lib/utils';
import type { Customer, DashboardStats } from '../../types';

export default function AgentViewPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [custRes, statsRes] = await Promise.all([
        customerApi.list({ sort_by: 'frustration_score', sort_order: 'desc', page_size: 20 }),
        dashboardApi.getStats(),
      ]);
      setCustomers(custRes.data.customers);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load agent data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl gradient-blue flex items-center justify-center">
          <Headphones size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Agent Workspace</h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            AI-assisted customer support queue
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card text-center">
            <AlertTriangle className="mx-auto mb-2 text-red-500" size={24} />
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {stats.high_risk_customers}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>High Risk</p>
          </div>
          <div className="stat-card text-center">
            <Clock className="mx-auto mb-2 text-blue-500" size={24} />
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {stats.open_cases}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Open Cases</p>
          </div>
          <div className="stat-card text-center">
            <Bot className="mx-auto mb-2 text-purple-500" size={24} />
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {stats.active_journeys}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Active Journeys</p>
          </div>
          <div className="stat-card text-center">
            <CheckCircle className="mx-auto mb-2 text-green-500" size={24} />
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {stats.avg_health_score.toFixed(0)}
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Avg Health</p>
          </div>
        </div>
      )}

      {/* Customer Queue */}
      <div className="stat-card">
        <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Priority Customer Queue
        </h3>
        <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
          Sorted by frustration score — highest frustration first
        </p>
        <div className="space-y-2">
          {customers.map((c, i) => (
            <div
              key={c.id}
              onClick={() => navigate(`/customers/${c.id}`)}
              className="flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all hover:scale-[1.005]"
              style={{
                background: c.frustration_score > 60 ? 'rgba(239, 68, 68, 0.05)' : 'var(--bg-hover)',
                border: `1px solid ${c.frustration_score > 60 ? 'rgba(239, 68, 68, 0.15)' : 'var(--border-color)'}`,
              }}
            >
              <span className="text-sm font-mono w-6 text-center" style={{ color: 'var(--text-muted)' }}>
                #{i + 1}
              </span>
              <div className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                style={{ background: `linear-gradient(135deg, ${getRiskColor(c.churn_risk)}, ${getRiskColor(c.churn_risk)}88)` }}>
                {c.first_name[0]}{c.last_name[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                  {c.first_name} {c.last_name}
                </p>
                <p className="text-xs capitalize" style={{ color: 'var(--text-muted)' }}>
                  {c.card_type} • {c.universal_id}
                </p>
              </div>
              <div className="flex items-center gap-8 text-center shrink-0 pl-4">
                <div className="w-16">
                  <p className="text-lg font-bold font-mono" style={{ color: c.frustration_score > 60 ? '#EF4444' : c.frustration_score > 30 ? '#F59E0B' : '#10B981' }}>
                    {c.frustration_score.toFixed(0)}
                  </p>
                  <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Frustration</p>
                </div>
                <div className="w-16">
                  <p className="text-lg font-bold font-mono" style={{ color: getScoreColor(c.health_score) }}>
                    {c.health_score.toFixed(0)}
                  </p>
                  <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Health</p>
                </div>
                <div className="w-16">
                  <p className="text-lg font-bold font-mono" style={{ color: getRiskColor(c.churn_risk) }}>
                    {(c.churn_risk * 100).toFixed(0)}%
                  </p>
                  <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Churn</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
