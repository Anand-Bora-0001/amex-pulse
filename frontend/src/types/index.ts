/**
 * AmEx Pulse — TypeScript Type Definitions
 * ==========================================
 */

// ── Auth Types ──────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Customer Types ──────────────────────────────────────────────
export interface Customer {
  id: string;
  universal_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  card_last_four?: string;
  member_since?: string;
  card_type: string;
  health_score: number;
  frustration_score: number;
  churn_risk: number;
  created_at?: string;
}

export interface CustomerDetail extends Customer {
  journeys: Journey[];
  recent_events: EventItem[];
  recommendations: Recommendation[];
  support_cases: SupportCase[];
  predictions: Prediction[];
}

export interface CustomerListResponse {
  customers: Customer[];
  total: number;
  page: number;
  page_size: number;
}

// ── Journey Types ───────────────────────────────────────────────
export interface JourneyStep {
  id: string;
  step_order: number;
  step_name: string;
  step_status: string;
}

export interface Journey {
  id: string;
  customer_id: string;
  journey_type: string;
  status: string;
  progress: number;
  detected_intent?: string;
  intent_confidence?: number;
  started_at?: string;
  completed_at?: string;
  ai_summary?: string;
  steps: JourneyStep[];
}

export interface JourneyGraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, any>;
}

export interface JourneyGraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  animated: boolean;
}

export interface JourneyGraphResponse {
  nodes: JourneyGraphNode[];
  edges: JourneyGraphEdge[];
}

// ── Event Types ─────────────────────────────────────────────────
export interface EventItem {
  id: string;
  customer_id: string;
  channel_name?: string;
  event_type: string;
  event_name: string;
  sentiment_score?: number;
  detected_emotion?: string;
  occurred_at?: string;
}

export interface LiveEvent {
  event: EventItem;
  customer_name: string;
  channel_icon: string;
  channel_color: string;
  timestamp: string;
}

// ── Prediction Types ────────────────────────────────────────────
export interface Prediction {
  id: string;
  customer_id: string;
  prediction_type: string;
  confidence: number;
  explanation?: string;
  model_version: string;
  predicted_at?: string;
}

// ── Recommendation Types ────────────────────────────────────────
export interface Recommendation {
  id: string;
  customer_id: string;
  action_type: string;
  action_description: string;
  confidence: number;
  reasoning?: string;
  status: string;
  created_at?: string;
}

// ── Support Case Types ──────────────────────────────────────────
export interface SupportCase {
  id: string;
  customer_id: string;
  case_number: string;
  subject: string;
  description?: string;
  priority: string;
  status: string;
  created_at?: string;
}

// ── Dashboard Types ─────────────────────────────────────────────
export interface DashboardStats {
  total_customers: number;
  active_journeys: number;
  avg_health_score: number;
  avg_frustration_score: number;
  high_risk_customers: number;
  open_cases: number;
  total_events_today: number;
  channel_distribution: Record<string, number>;
  health_distribution: Record<string, number>;
  journey_status_distribution: Record<string, number>;
  recent_events: LiveEvent[];
  top_risk_customers: Customer[];
}

export interface KPI {
  name: string;
  value: number | string;
  change?: number;
  trend: string;
  icon: string;
}

export interface FunnelStage {
  stage: string;
  count: number;
  percentage: number;
  drop_off_rate: number;
}
