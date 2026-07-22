/**
 * AmEx Pulse — Customer Detail/Profile Page
 * ============================================
 * 360° customer view with scores, journey, events, predictions, recommendations.
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, Phone, Mail, CreditCard, Activity, AlertTriangle, UserMinus, ShieldAlert, FileText, CheckCircle, Zap, HeartPulse, HelpCircle, Lightbulb, Gift, Bot, MessageSquare, Shield, RefreshCw, PlayCircle } from 'lucide-react';
import { customerApi, predictionApi } from '../../lib/api';
import { getScoreColor, getRiskColor, getSentimentIcon, timeAgo, channelIcons, channelColors } from '../../lib/utils';
import ScoreDial from '../../components/charts/ScoreDial';
import type { CustomerDetail } from '../../types';

const ACTION_ICONS: Record<string, any> = {
  priority_callback: Phone,
  fee_waiver: Gift,
  credit_increase: CreditCard,
  travel_support: Zap,
  fraud_review: Shield,
  special_reward: Gift,
  dedicated_agent: MessageSquare,
};

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [customer, setCustomer] = useState<CustomerDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningAI, setRunningAI] = useState(false);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [activeEventIndex, setActiveEventIndex] = useState<number | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id) loadCustomer(id);
  }, [id]);

  const loadCustomer = async (customerId: string) => {
    try {
      const res = await customerApi.get(customerId);
      setCustomer(res.data);
    } catch (err) {
      console.error('Failed to load customer:', err);
    } finally {
      setLoading(false);
    }
  };

  const runAIPipeline = async () => {
    if (!id) return;
    setRunningAI(true);
    try {
      const res = await predictionApi.run(id);
      const results = res.data;
      // Refresh customer data
      await loadCustomer(id);
      // Show summary if available
      if (results.predictions) {
        const summary = results.predictions.find((p: any) => p.type === 'summary');
        if (summary?.result?.result?.summary) {
          setAiSummary(summary.result.result.summary);
        }
      }
    } catch (err) {
      console.error('AI pipeline failed:', err);
    } finally {
      setRunningAI(false);
    }
  };

  const startReplay = () => {
    if (!customer || customer.recent_events.length === 0) return;
    setIsReplaying(true);
    setActiveEventIndex(customer.recent_events.length - 1); // Start from oldest

    let currentIndex = customer.recent_events.length - 1;
    const interval = setInterval(() => {
      currentIndex--;
      if (currentIndex < 0) {
        clearInterval(interval);
        setTimeout(() => {
          setIsReplaying(false);
          setActiveEventIndex(null);
        }, 1000);
      } else {
        setActiveEventIndex(currentIndex);
      }
    }, 1200); // 1.2s per event
  };

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-3 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="page-container text-center py-20">
        <p style={{ color: 'var(--text-muted)' }}>Customer not found</p>
      </div>
    );
  }

  return (
    <div className="page-container space-y-6">
      {/* Back button + Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="p-2 rounded-lg hover:bg-gray-500/10 transition-colors">
          <ArrowLeft size={20} style={{ color: 'var(--text-secondary)' }} />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg"
              style={{ background: 'linear-gradient(135deg, #006FCF, #3B9AE8)' }}
            >
              {customer.first_name[0]}{customer.last_name[0]}
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {customer.first_name} {customer.last_name}
              </h1>
              <div className="flex items-center gap-3 text-sm" style={{ color: 'var(--text-muted)' }}>
                <span>{customer.universal_id}</span>
                <span>•</span>
                <span className="capitalize">{customer.card_type} Member</span>
                <span>•</span>
                <span>Since {customer.member_since}</span>
              </div>
            </div>
          </div>
        </div>
        <button
          onClick={runAIPipeline}
          disabled={runningAI}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm text-white gradient-blue
            hover:opacity-90 transition-all disabled:opacity-50 shadow-lg shadow-blue-600/20"
        >
          {runningAI ? (
            <RefreshCw size={16} className="animate-spin" />
          ) : (
            <Bot size={16} />
          )}
          {runningAI ? 'Running AI...' : 'Run AI Pipeline'}
        </button>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="stat-card flex flex-col items-center py-6">
          <ScoreDial value={customer.health_score} size={140} strokeWidth={10} label="Customer Health" type="health" />
          <p className="mt-2 text-sm font-medium" style={{ color: getScoreColor(customer.health_score) }}>
            {customer.health_score >= 75 ? 'Healthy' : customer.health_score >= 50 ? 'At Risk' : customer.health_score >= 25 ? 'Unhealthy' : 'Critical'}
          </p>
        </div>
        <div className="stat-card flex flex-col items-center py-6 relative overflow-hidden">
          <ScoreDial value={customer.frustration_score} size={140} strokeWidth={10} label="Frustration Score" type="frustration" />
          <p className="mt-2 text-sm font-medium mb-4" style={{ color: customer.frustration_score >= 70 ? '#EF4444' : customer.frustration_score >= 40 ? '#F59E0B' : '#10B981' }}>
            {customer.frustration_score >= 70 ? 'Critical' : customer.frustration_score >= 40 ? 'Elevated' : 'Low'}
          </p>
          
          {/* Root Cause Engine */}
          {customer.frustration_score >= 40 && (
            <div className="w-full mt-2 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
              <div className="flex items-center gap-1.5 mb-2 justify-center text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>
                <AlertTriangle size={12} className="text-red-500" /> Root Cause Breakdown
              </div>
              <div className="space-y-1.5 px-4 w-full text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                <div className="flex justify-between items-center">
                  <span>Login Failure</span>
                  <span className="font-mono text-red-400">48%</span>
                </div>
                <div className="w-full bg-gray-500/20 h-1 rounded-full"><div className="bg-red-400 h-1 rounded-full" style={{ width: '48%' }}></div></div>
                
                <div className="flex justify-between items-center mt-2">
                  <span>Channel Switching</span>
                  <span className="font-mono text-orange-400">20%</span>
                </div>
                <div className="w-full bg-gray-500/20 h-1 rounded-full"><div className="bg-orange-400 h-1 rounded-full" style={{ width: '20%' }}></div></div>
                
                <div className="flex justify-between items-center mt-2">
                  <span>Repeated Auth</span>
                  <span className="font-mono text-yellow-500">18%</span>
                </div>
                <div className="w-full bg-gray-500/20 h-1 rounded-full"><div className="bg-yellow-500 h-1 rounded-full" style={{ width: '18%' }}></div></div>
              </div>
            </div>
          )}
        </div>
        <div className="stat-card flex flex-col items-center py-6">
          <ScoreDial value={customer.churn_risk} size={140} strokeWidth={10} label="Churn Risk" type="churn" />
          <p className="mt-2 text-sm font-medium" style={{ color: getRiskColor(customer.churn_risk) }}>
            {customer.churn_risk >= 0.6 ? 'High Risk' : customer.churn_risk >= 0.3 ? 'Medium Risk' : 'Low Risk'}
          </p>
        </div>
      </div>

      {/* AI Copilot & Journey DNA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* AI Copilot Analysis */}
        <div className="stat-card relative overflow-hidden" style={{ border: '1px solid rgba(59, 130, 246, 0.4)', boxShadow: '0 0 20px rgba(59, 130, 246, 0.1)' }}>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500" />
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 rounded-lg bg-blue-500/20">
              <Bot size={20} className="text-blue-500" />
            </div>
            <h3 className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>AI Copilot Analysis</h3>
          </div>
          <div className="text-sm leading-relaxed space-y-3 p-4 rounded-xl bg-blue-500/5 border border-blue-500/10" style={{ color: 'var(--text-secondary)' }}>
            {aiSummary ? (
              aiSummary.split('\n\n').map((paragraph, i) => (
                <p key={i} dangerouslySetInnerHTML={{ __html: paragraph.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary)">$1</strong>') }} />
              ))
            ) : (
              <>
                <p>
                  Customer attempted payment <strong>4 times</strong> across 2 devices. Authentication failed on Mobile App due to timeout. Customer then visited the FAQ for 'Account Locked' and immediately opened Web Chat.
                </p>
                <p className="text-red-400 font-medium flex items-center gap-1 mt-2">
                  <AlertTriangle size={14} /> High churn risk detected due to unresolved payment block.
                </p>
                <div className="mt-4 pt-4 border-t border-blue-500/20">
                  <span className="text-xs font-bold text-blue-500 uppercase tracking-wider">Recommended Next Action</span>
                  <div className="flex items-center gap-2 mt-2">
                    <Phone size={16} className="text-green-500" />
                    <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>Initiate Priority Callback</span>
                  </div>
                  <p className="text-xs mt-1 italic opacity-80">Bypass IVR routing. Pre-authenticate user before agent connects.</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Journey DNA */}
        <div className="stat-card">
          <div className="flex items-center gap-2 mb-4">
            <HeartPulse size={18} className="text-pink-500" />
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Customer Journey DNA</h3>
          </div>
          <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>Unique behavioral fingerprint</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg" style={{ background: 'var(--bg-hover)' }}>
              <span className="text-[10px] uppercase font-bold text-blue-400">Digital Behaviour</span>
              <p className="text-sm font-medium mt-1" style={{ color: 'var(--text-primary)' }}>Mobile-First</p>
            </div>
            <div className="p-3 rounded-lg" style={{ background: 'var(--bg-hover)' }}>
              <span className="text-[10px] uppercase font-bold text-purple-400">Channel Preference</span>
              <p className="text-sm font-medium mt-1" style={{ color: 'var(--text-primary)' }}>Self-Service to Chat</p>
            </div>
            <div className="p-3 rounded-lg" style={{ background: 'var(--bg-hover)' }}>
              <span className="text-[10px] uppercase font-bold text-orange-400">Communication Style</span>
              <p className="text-sm font-medium mt-1" style={{ color: 'var(--text-primary)' }}>Direct / Urgent</p>
            </div>
            <div className="p-3 rounded-lg" style={{ background: 'var(--bg-hover)' }}>
              <span className="text-[10px] uppercase font-bold text-red-400">Risk Pattern</span>
              <p className="text-sm font-medium mt-1" style={{ color: 'var(--text-primary)' }}>High Churn Sensitivity</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendations */}
        <div className="stat-card">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={18} className="text-amber-500" />
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              AI Recommendations ({customer.recommendations.length})
            </h3>
          </div>
          <div className="space-y-3">
            {customer.recommendations.length === 0 ? (
              <p className="text-sm py-4 text-center" style={{ color: 'var(--text-muted)' }}>
                Run AI Pipeline to generate recommendations
              </p>
            ) : (
              customer.recommendations.map((rec) => {
                const IconComponent = ACTION_ICONS[rec.action_type] || Zap;
                return (
                  <div key={rec.id} className="p-4 rounded-xl" style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)' }}>
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg gradient-blue flex items-center justify-center flex-shrink-0">
                        <IconComponent size={18} className="text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                          {rec.action_type.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                          {rec.action_description}
                        </p>
                        {rec.reasoning && (
                          <p className="text-xs mt-2 italic" style={{ color: 'var(--text-muted)' }}>
                            <Lightbulb size={14} className="inline mr-1 text-yellow-500" /> {rec.reasoning}
                          </p>
                        )}
                        <div className="flex items-center gap-3 mt-2">
                          <div className="flex-1 h-1.5 rounded-full" style={{ background: 'var(--border-color)' }}>
                            <div
                              className="h-full rounded-full gradient-blue"
                              style={{ width: `${rec.confidence * 100}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-mono" style={{ color: 'var(--text-muted)' }}>
                            {(rec.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Event Timeline */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock size={18} className="text-blue-500" />
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                Event Timeline ({customer.recent_events.length})
              </h3>
            </div>
            <button
              onClick={startReplay}
              disabled={isReplaying || customer.recent_events.length === 0}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
              style={{
                background: isReplaying ? 'var(--bg-hover)' : 'rgba(59, 130, 246, 0.1)',
                color: isReplaying ? 'var(--text-muted)' : '#3B82F6',
                border: isReplaying ? '1px solid var(--border-color)' : '1px solid rgba(59, 130, 246, 0.2)'
              }}
            >
              {isReplaying ? (
                <>
                  <RefreshCw size={14} className="animate-spin" /> Replaying...
                </>
              ) : (
                <>
                  <PlayCircle size={14} /> Replay Journey
                </>
              )}
            </button>
          </div>
          <div className="timeline max-h-[500px] overflow-y-auto pr-2">
            {customer.recent_events.slice(0, 20).map((event, index) => (
              <div
                key={event.id}
                className={`timeline-item transition-all duration-500 ${
                  activeEventIndex === index ? 'scale-105 shadow-lg z-10 p-3 rounded-xl' : ''
                } ${
                  (event.sentiment_score ?? 0) < -0.3 ? 'negative' :
                  (event.sentiment_score ?? 0) > 0.3 ? 'positive' : ''
                }`}
                style={{
                  background: activeEventIndex === index ? 'var(--bg-hover)' : 'transparent',
                  border: activeEventIndex === index ? '1px solid var(--border-color)' : '1px solid transparent',
                  opacity: isReplaying && activeEventIndex !== index ? 0.3 : 1
                }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {event.event_name}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className="channel-badge"
                        style={{
                          background: `${channelColors[event.channel_name ?? ''] ?? '#6B7280'}15`,
                          color: channelColors[event.channel_name ?? ''] ?? '#6B7280',
                        }}
                      >
                        {channelIcons[event.channel_name ?? ''] ?? <HelpCircle size={14} className="inline mr-1" />} {event.channel_name?.replace('_', ' ')}
                      </span>
                      <span className={`sentiment-badge ${
                        (event.sentiment_score ?? 0) > 0.3 ? 'positive' :
                        (event.sentiment_score ?? 0) < -0.3 ? 'negative' : 'neutral'
                      }`}>
                        {getSentimentIcon(event.sentiment_score ?? null)} {event.detected_emotion}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] flex-shrink-0" style={{ color: 'var(--text-muted)' }}>
                    {event.occurred_at ? timeAgo(event.occurred_at) : ''}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Journeys */}
      {customer.journeys.length > 0 && (
        <div className="stat-card">
          <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Customer Journeys ({customer.journeys.length})
          </h3>
          <div className="space-y-4">
            {customer.journeys.map((journey) => (
              <div key={journey.id} className="p-4 rounded-xl" style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)' }}>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                      {journey.journey_type.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                      Intent: {journey.detected_intent?.replace(/_/g, ' ')} • Confidence: {((journey.intent_confidence ?? 0) * 100).toFixed(0)}%
                    </p>
                  </div>
                  <span
                    className="px-3 py-1 rounded-full text-xs font-semibold capitalize"
                    style={{
                      background: journey.status === 'completed' ? '#10B98120' :
                                  journey.status === 'failed' ? '#EF444420' :
                                  journey.status === 'abandoned' ? '#F59E0B20' : '#3B82F620',
                      color: journey.status === 'completed' ? '#10B981' :
                             journey.status === 'failed' ? '#EF4444' :
                             journey.status === 'abandoned' ? '#F59E0B' : '#3B82F6',
                    }}
                  >
                    {journey.status.replace('_', ' ')}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 rounded-full" style={{ background: 'var(--border-color)' }}>
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{
                        width: `${journey.progress}%`,
                        background: journey.status === 'completed' ? '#10B981' :
                                    journey.status === 'failed' ? '#EF4444' : '#006FCF',
                      }}
                    />
                  </div>
                  <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                    {journey.progress.toFixed(0)}%
                  </span>
                </div>
                {/* Steps */}
                {journey.steps.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {journey.steps.map((step) => (
                      <span
                        key={step.id}
                        className="px-2 py-1 rounded text-[10px] font-medium"
                        style={{
                          background: step.step_status === 'completed' ? '#10B98115' :
                                      step.step_status === 'failed' ? '#EF444415' : 'var(--bg-primary)',
                          color: step.step_status === 'completed' ? '#10B981' :
                                 step.step_status === 'failed' ? '#EF4444' : 'var(--text-muted)',
                          border: `1px solid ${step.step_status === 'completed' ? '#10B98130' :
                                              step.step_status === 'failed' ? '#EF444430' : 'var(--border-color)'}`,
                        }}
                      >
                        {step.step_status === 'completed' ? <CheckCircle size={12} className="inline mr-1 text-green-500"/> : step.step_status === 'failed' ? <AlertTriangle size={12} className="inline mr-1 text-red-500"/> : ''}{step.step_name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Support Cases */}
      {customer.support_cases.length > 0 && (
        <div className="stat-card">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={18} className="text-orange-500" />
            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              Support Cases ({customer.support_cases.length})
            </h3>
          </div>
          <div className="space-y-3">
            {customer.support_cases.map((sc) => (
              <div key={sc.id} className="p-3 rounded-lg" style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)' }}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {sc.case_number}: {sc.subject}
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{sc.description}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${
                      sc.priority === 'critical' ? 'bg-red-500/15 text-red-500' :
                      sc.priority === 'high' ? 'bg-orange-500/15 text-orange-500' :
                      'bg-blue-500/15 text-blue-500'
                    }`}>
                      {sc.priority}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
