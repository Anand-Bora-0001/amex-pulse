/**
 * AmEx Pulse — Customer List Page
 * =================================
 * Searchable, filterable customer list with health/frustration/churn indicators.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ChevronRight, Users as UsersIcon } from 'lucide-react';
import { customerApi } from '../../lib/api';
import { getScoreColor, getRiskColor, getCardTypeColor } from '../../lib/utils';
import ScoreDial from '../../components/charts/ScoreDial';
import type { Customer, CustomerListResponse } from '../../types';

export default function CustomersPage() {
  const [data, setData] = useState<CustomerListResponse | null>(null);
  const [search, setSearch] = useState('');
  const [cardFilter, setCardFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCustomers();
  }, [search, cardFilter, riskFilter]);

  const loadCustomers = async () => {
    try {
      const params: Record<string, any> = { page: 1, page_size: 50 };
      if (search) params.search = search;
      if (cardFilter) params.card_type = cardFilter;
      if (riskFilter) params.risk_level = riskFilter;
      const res = await customerApi.list(params);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load customers:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Customers
          </h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {data?.total ?? 0} card members • Unified customer profiles
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
          />
        </div>
        <select
          value={cardFilter}
          onChange={(e) => setCardFilter(e.target.value)}
          className="px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
        >
          <option value="">All Card Types</option>
          <option value="platinum">Platinum</option>
          <option value="gold">Gold</option>
          <option value="green">Green</option>
          <option value="blue">Blue</option>
        </select>
        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          className="px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
        >
          <option value="">All Risk Levels</option>
          <option value="high">High Risk</option>
          <option value="medium">Medium Risk</option>
          <option value="low">Low Risk</option>
        </select>
      </div>

      {/* Customer Grid */}
      {loading ? (
        <div className="text-center py-20">
          <div className="w-10 h-10 border-3 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.customers.map((customer) => (
            <div
              key={customer.id}
              onClick={() => navigate(`/customers/${customer.id}`)}
              className="stat-card cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-sm"
                    style={{ background: `linear-gradient(135deg, ${getCardTypeColor(customer.card_type)}, ${getCardTypeColor(customer.card_type)}88)` }}
                  >
                    {customer.first_name[0]}{customer.last_name[0]}
                  </div>
                  <div>
                    <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {customer.first_name} {customer.last_name}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      {customer.universal_id}
                    </p>
                    <span
                      className="inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase mt-1"
                      style={{
                        background: `${getCardTypeColor(customer.card_type)}20`,
                        color: getCardTypeColor(customer.card_type),
                      }}
                    >
                      {customer.card_type}
                    </span>
                  </div>
                </div>
                <ChevronRight size={16} className="text-gray-400 group-hover:text-blue-500 transition-colors" />
              </div>

              {/* Score indicators */}
              <div className="flex justify-between items-end">
                <div className="flex gap-6">
                  <ScoreDial value={customer.health_score} size={60} strokeWidth={5} label="Health" type="health" />
                  <ScoreDial value={customer.frustration_score} size={60} strokeWidth={5} label="Frustration" type="frustration" />
                  <ScoreDial value={customer.churn_risk} size={60} strokeWidth={5} label="Churn" type="churn" />
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 pt-3" style={{ borderTop: '1px solid var(--border-color)' }}>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Member since {customer.member_since}
                </span>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  •••• {customer.card_last_four}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
