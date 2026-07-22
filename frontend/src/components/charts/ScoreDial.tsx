/**
 * AmEx Pulse — Score Dial Component
 * ===================================
 * Animated circular gauge for health/frustration/churn scores.
 */

import { useEffect, useState } from 'react';
import { getScoreColor, getRiskColor } from '../../lib/utils';

interface ScoreDialProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  label: string;
  type?: 'health' | 'frustration' | 'churn';
  showLabel?: boolean;
}

export default function ScoreDial({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  label,
  type = 'health',
  showLabel = true,
}: ScoreDialProps) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const normalizedValue = type === 'churn' ? value * 100 : value;
  const progress = (animatedValue / max) * circumference;
  const offset = circumference - progress;

  const getColor = () => {
    if (type === 'churn') return getRiskColor(value);
    if (type === 'frustration') {
      if (value >= 70) return '#EF4444';
      if (value >= 40) return '#F59E0B';
      return '#10B981';
    }
    return getScoreColor(value);
  };

  const displayValue = type === 'churn' 
    ? `${(value * 100).toFixed(0)}%`
    : value.toFixed(0);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="score-dial" style={{ width: size, height: size }}>
        <svg className="score-dial__circle" width={size} height={size}>
          {/* Track */}
          <circle
            className="score-dial__track"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
          />
          {/* Progress */}
          <circle
            className="score-dial__progress"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            stroke={getColor()}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 6px ${getColor()}40)` }}
          />
        </svg>
        <div className="score-dial__value" style={{ color: getColor() }}>
          {displayValue}
        </div>
      </div>
      {showLabel && (
        <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
          {label}
        </span>
      )}
    </div>
  );
}
