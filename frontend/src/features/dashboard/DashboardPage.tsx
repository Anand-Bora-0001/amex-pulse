/**
 * AmEx Pulse — Dashboard Page
 * =============================
 * Real-time command center with KPIs, live events, charts, and risk indicators.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, Activity, AlertTriangle, HeartPulse, Map,
  Headphones, TrendingUp, TrendingDown, Minus, Zap, Bot
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  AreaChart, Area, Legend,
} from 'recharts';
import { dashboardApi } from '../../lib/api';
import { getScoreColor, getRiskColor, getSentimentIcon, timeAgo, channelColors } from '../../lib/utils';
import ScoreDial from '../../components/charts/ScoreDial';
import type { DashboardStats, KPI, LiveEvent, Customer } from '../../types';

const CHART_COLORS = ['#F97316', '#FB923C', '#FACC15', '#10B981', '#EF4444', '#8B5CF6', '#EC4899', '#FDBA74'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, kpisRes] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getKPIs(),
      ]);
      setStats(statsRes.data);
      setKpis(kpisRes.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: 'var(--text-secondary)' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const channelData = Object.entries(stats.channel_distribution).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
    color: channelColors[name] || '#6B7280',
  }));

  const healthData = Object.entries(stats.health_distribution).map(([name, value]) => ({
    name,
    value,
  }));

  const journeyData = Object.entries(stats.journey_status_distribution).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }));

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return <TrendingUp size={14} className="text-green-500" />;
    if (trend === 'down') return <TrendingDown size={14} className="text-red-500" />;
    return <Minus size={14} className="text-gray-400" />;
  };

  return (
    <div className="page-container space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Command Center
          </h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Real-time customer journey intelligence
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
          <div className="pulse-dot" />
          <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Live</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="dashboard-grid">
        {kpis.slice(0, 4).map((kpi, i) => (
          <div key={kpi.name} className={`stat-card animate-slide-up stagger-${i + 1}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{kpi.icon}</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(kpi.trend)}
                <span className={`text-xs font-medium ${
                  kpi.trend === 'up' ? 'text-green-500' :
                  kpi.trend === 'down' ? 'text-red-500' : 'text-gray-400'
                }`}>
                  {kpi.change !== null && kpi.change !== undefined ? `${kpi.change > 0 ? '+' : ''}${kpi.change}%` : ''}
                </span>
              </div>
            </div>
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {kpi.value}
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              {kpi.name}
            </p>
          </div>
        ))}
      </div>

      {/* Second KPI row */}
      <div className="dashboard-grid">
        {kpis.slice(4, 8).map((kpi, i) => (
          <div key={kpi.name} className={`stat-card animate-slide-up stagger-${i + 1}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-2xl">{kpi.icon}</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(kpi.trend)}
                <span className={`text-xs font-medium ${
                  kpi.trend === 'up' ? 'text-green-500' :
                  kpi.trend === 'down' ? 'text-red-500' : 'text-gray-400'
                }`}>
                  {kpi.change !== null && kpi.change !== undefined ? `${kpi.change > 0 ? '+' : ''}${kpi.change}%` : ''}
                </span>
              </div>
            </div>
            <p className="text-2xl font-bold" style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {kpi.value}
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              {kpi.name}
            </p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="dashboard-grid-wide">
        {/* Channel Distribution */}
        <div className="stat-card">
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Channel Distribution
          </h3>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width="50%" height={220}>
              <PieChart>
                <Pie
                  data={channelData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {channelData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    color: 'var(--text-primary)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 flex-1">
              {channelData.map((ch) => (
                <div key={ch.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ background: ch.color }} />
                    <span className="text-sm capitalize" style={{ color: 'var(--text-secondary)' }}>{ch.name}</span>
                  </div>
                  <span className="text-sm font-mono font-medium" style={{ color: 'var(--text-primary)' }}>{ch.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Health Distribution */}
        <div className="stat-card">
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Customer Health Distribution
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={healthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {healthData.map((_, index) => (
                  <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Live Feed + Risk Customers */}
      <div className="dashboard-grid-wide">
        {/* Live Event Feed */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity size={18} className="text-green-500" />
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                Live Event Feed
              </h3>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="pulse-dot" />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {stats.total_events_today} events today
              </span>
            </div>
          </div>
          <div className="live-feed">
            {stats.recent_events.map((event, i) => (
              <div key={i} className="live-feed-item">
                <span className="text-lg">{event.channel_icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                    {event.customer_name}
                  </p>
                  <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                    {event.event.event_name}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className={`sentiment-badge ${
                    (event.event.sentiment_score ?? 0) > 0.3 ? 'positive' :
                    (event.event.sentiment_score ?? 0) < -0.3 ? 'negative' : 'neutral'
                  }`}>
                    {getSentimentIcon(event.event.sentiment_score ?? null)}
                  </span>
                  <p className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>
                    {event.timestamp ? timeAgo(event.timestamp) : ''}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Customers */}
        <div className="stat-card">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={18} className="text-red-500" />
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              High-Risk Customers
            </h3>
          </div>
          <div className="space-y-3">
            {stats.top_risk_customers.map((customer) => (
              <div
                key={customer.id}
                onClick={() => navigate(`/customers/${customer.id}`)}
                className="p-3 rounded-lg cursor-pointer transition-all hover:scale-[1.01]"
                style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)' }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                      style={{ background: getRiskColor(customer.churn_risk) }}
                    >
                      {customer.first_name[0]}{customer.last_name[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                        {customer.first_name} {customer.last_name}
                      </p>
                      <p className="text-[10px] capitalize" style={{ color: 'var(--text-muted)' }}>
                        {customer.card_type} member
                      </p>
                    </div>
                  </div>
                  <span
                    className="text-sm font-mono font-bold"
                    style={{ color: getRiskColor(customer.churn_risk) }}
                  >
                    {(customer.churn_risk * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex gap-4 text-[11px]">
                  <span style={{ color: 'var(--text-muted)' }}>
                    Health: <b style={{ color: getScoreColor(customer.health_score) }}>{customer.health_score.toFixed(0)}</b>
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>
                    Frustration: <b style={{ color: customer.frustration_score > 50 ? '#EF4444' : '#10B981' }}>{customer.frustration_score.toFixed(0)}</b>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Journey Status */}
      <div className="stat-card">
        <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Journey Status Distribution
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={journeyData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
            <YAxis dataKey="name" type="category" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} width={100} />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
              }}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]}>
              {journeyData.map((_, index) => (
                <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
