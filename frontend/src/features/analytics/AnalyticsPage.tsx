/**
 * AmEx Pulse — Analytics Page
 * =============================
 * Business intelligence with funnel, channel analytics, and frustration heatmap.
 */

import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell, ComposedChart, Line
} from 'recharts';
import { BarChart3, Filter } from 'lucide-react';
import { analyticsApi, dashboardApi } from '../../lib/api';
import type { FunnelStage, KPI } from '../../types';

const FUNNEL_COLORS = ['#F97316', '#FB923C', '#FDBA74', '#FACC15', '#F59E0B', '#EF4444', '#10B981'];

export default function AnalyticsPage() {
  const [funnel, setFunnel] = useState<FunnelStage[]>([]);
  const [channels, setChannels] = useState<any[]>([]);
  const [heatmap, setHeatmap] = useState<any[]>([]);
  const [journeyType, setJourneyType] = useState('card_activation');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [journeyType]);

  const loadAnalytics = async () => {
    try {
      const [funnelRes, channelsRes, heatmapRes] = await Promise.all([
        analyticsApi.getFunnel(journeyType),
        analyticsApi.getChannels(),
        analyticsApi.getHeatmap(),
      ]);
      setFunnel(funnelRes.data);
      setChannels(channelsRes.data);
      setHeatmap(heatmapRes.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const getHeatmapColor = (value: number): string => {
    if (value >= 60) return '#EF4444';
    if (value >= 45) return '#F97316';
    if (value >= 30) return '#F59E0B';
    if (value >= 15) return '#FCD34D';
    return '#10B981';
  };

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Analytics</h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Business intelligence & journey analytics
          </p>
        </div>
      </div>

      {/* Journey Funnel */}
      <div className="stat-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
            Journey Conversion Funnel
          </h3>
          <select
            value={journeyType}
            onChange={(e) => setJourneyType(e.target.value)}
            className="px-3 py-1.5 rounded-lg text-sm"
            style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
          >
            <option value="card_activation">Card Activation</option>
            <option value="dispute">Dispute</option>
            <option value="credit_limit">Credit Limit</option>
            <option value="rewards">Rewards</option>
            <option value="payment">Payment</option>
            <option value="travel">Travel</option>
          </select>
        </div>

        {/* Funnel visualization */}
        <div className="mt-6">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={funnel} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" opacity={0.5} />
              <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
              <YAxis 
                dataKey="stage" 
                type="category" 
                width={160} 
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} 
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: 'var(--bg-hover)' }}
                content={({ active, payload, label }: any) => {
                  if (active && payload && payload.length) {
                    const p = payload[0].payload;
                    return (
                      <div className="p-3 rounded-xl shadow-md border" style={{ background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
                        <p className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>{label}</p>
                        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          Volume: <span className="font-mono font-bold" style={{ color: 'var(--text-primary)' }}>{payload[0].value}</span> ({p.percentage.toFixed(1)}%)
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[0, 8, 8, 0]} barSize={28}>
                {funnel.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={FUNNEL_COLORS[index % FUNNEL_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Channel Performance + Heatmap */}
      <div className="dashboard-grid-wide">
        {/* Channel Performance */}
        <div className="stat-card">
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Channel Performance
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={channels} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" opacity={0.5} />
              <XAxis dataKey="display_name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: 'transparent' }}
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  boxShadow: 'var(--shadow-md)',
                  color: 'var(--text-primary)',
                }}
              />
              <Bar dataKey="event_count" name="Events" radius={[8, 8, 0, 0]} barSize={40}>
                {channels.map((ch, index) => (
                  <Cell key={index} fill={FUNNEL_COLORS[index % FUNNEL_COLORS.length]} />
                ))}
              </Bar>
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Frustration Heatmap */}
        <div className="stat-card">
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Frustration Heatmap
          </h3>
          <p className="text-xs mb-3" style={{ color: 'var(--text-muted)' }}>
            Day of week × Hour — When are customers most frustrated?
          </p>
          <div className="flex justify-center mt-6">
            <div className="inline-flex flex-col gap-1">
              {/* Hour labels */}
              <div className="flex gap-1 pl-10 mb-1">
                {hours.map((h) => (
                  <div key={h} className="w-4 text-[9px] text-center" style={{ color: 'var(--text-muted)' }}>
                    {h % 4 === 0 ? `${h}` : ''}
                  </div>
                ))}
              </div>
              {/* Grid */}
              {days.map((day) => (
                <div key={day} className="flex items-center gap-1">
                  <span className="w-10 text-[10px] text-right pr-2 font-medium" style={{ color: 'var(--text-muted)' }}>
                    {day}
                  </span>
                  {hours.map((hour) => {
                    const cell = heatmap.find((h) => h.day === day && h.hour === hour);
                    const value = cell?.value ?? 0;
                    return (
                      <div
                        key={hour}
                        className="w-4 h-4 rounded-sm cursor-pointer transition-transform hover:scale-125"
                        style={{ background: getHeatmapColor(value), opacity: 0.2 + (value / 100) * 0.8 }}
                        title={`${day} ${hour}:00 — Frustration: ${value}`}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
          {/* Legend */}
          <div className="flex items-center justify-end gap-1 mt-5">
            <span className="text-[9px]" style={{ color: 'var(--text-muted)' }}>Low</span>
            {['#10B981', '#FCD34D', '#F59E0B', '#F97316', '#EF4444'].map((c) => (
              <div key={c} className="w-4 h-3 rounded-sm" style={{ background: c }} />
            ))}
            <span className="text-[9px]" style={{ color: 'var(--text-muted)' }}>High</span>
          </div>
        </div>
      </div>
    </div>
  );
}
