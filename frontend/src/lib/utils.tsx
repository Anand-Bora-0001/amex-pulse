/**
 * AmEx Pulse — Utility Functions
 * ===============================
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Smartphone, Globe, Phone, Building, Mail, Bot, BarChart2, Ticket, Smile, Meh, Frown } from 'lucide-react';
import React from 'react';

/** Merge TailwindCSS classes without conflicts */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a number with commas */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

/** Format a percentage */
export function formatPercent(value: number, decimals = 0): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/** Get color for a score (0-100) */
export function getScoreColor(score: number): string {
  if (score >= 75) return '#10B981';
  if (score >= 50) return '#F59E0B';
  if (score >= 25) return '#F97316';
  return '#EF4444';
}

/** Get color for churn risk (0-1) */
export function getRiskColor(risk: number): string {
  if (risk >= 0.6) return '#EF4444';
  if (risk >= 0.3) return '#F59E0B';
  return '#10B981';
}

/** Get sentiment icon */
export function getSentimentIcon(score: number | null): React.ReactNode {
  if (score === null) return <Meh size={14} className="inline mr-1" />;
  if (score > 0.3) return <Smile size={14} className="inline mr-1 text-green-500" />;
  if (score > 0) return <Smile size={14} className="inline mr-1 text-green-400" />;
  if (score > -0.3) return <Meh size={14} className="inline mr-1 text-gray-400" />;
  if (score > -0.6) return <Frown size={14} className="inline mr-1 text-orange-400" />;
  return <Frown size={14} className="inline mr-1 text-red-500" />;
}

/** Format relative time */
export function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

/** Get card type badge color */
export function getCardTypeColor(cardType: string): string {
  const colors: Record<string, string> = {
    platinum: '#E5E7EB',
    gold: '#F7B731',
    green: '#10B981',
    blue: '#3B82F6',
  };
  return colors[cardType] || '#6B7280';
}

/** Channel icon mapping */
export const channelIcons: Record<string, React.ReactNode> = {
  mobile: <Smartphone size={14} className="inline mr-1" />,
  web: <Globe size={14} className="inline mr-1" />,
  call_center: <Phone size={14} className="inline mr-1" />,
  branch: <Building size={14} className="inline mr-1" />,
  email: <Mail size={14} className="inline mr-1" />,
  chatbot: <Bot size={14} className="inline mr-1" />,
  crm: <BarChart2 size={14} className="inline mr-1" />,
  support_ticket: <Ticket size={14} className="inline mr-1" />,
};

/** Channel color mapping */
export const channelColors: Record<string, string> = {
  mobile: '#6366F1',
  web: '#3B82F6',
  call_center: '#F59E0B',
  branch: '#10B981',
  email: '#8B5CF6',
  chatbot: '#EC4899',
  crm: '#14B8A6',
  support_ticket: '#F97316',
};
