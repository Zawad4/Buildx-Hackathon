import { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { ANALYTICS_DATA } from '../data/mockSecurityData';

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <div className="chart-tooltip-header">{label}</div>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="chart-tooltip-row">
            <span
              className="chart-tooltip-dot"
              style={{ backgroundColor: entry.color }}
            />
            <span className="chart-tooltip-label">{entry.name}:</span>
            <span className="chart-tooltip-val">
              {entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export default function SecurityAnalyticsChart() {
  const [range, setRange] = useState('7D');
  const data = ANALYTICS_DATA[range] || ANALYTICS_DATA['7D'];

  return (
    <div className="panel-card chart-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <h3 className="panel-title">Access Request Telemetry</h3>
          <span className="panel-subtitle">
            Temporal egress authorization, denial & flag volume
          </span>
        </div>
        <div className="pill-toggle-group">
          {['7D', '14D', '30D'].map((r) => (
            <button
              key={r}
              type="button"
              className={`pill-toggle-btn ${range === r ? 'active' : ''}`}
              onClick={() => setRange(r)}
            >
              {r === '7D' ? 'Last 7 Days' : r === '14D' ? '14 Days' : '30 Days'}
            </button>
          ))}
        </div>
      </div>
      <div className="panel-body">
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorDenied" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#dc2626" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#dc2626" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorFlagged" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#d97706" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#d97706" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: '#64748b' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(val) => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                align="right"
                iconType="circle"
                wrapperStyle={{ paddingBottom: '12px', fontSize: '11px', color: '#475569' }}
              />
              <Area
                type="monotone"
                dataKey="allowed"
                name="Allowed Requests"
                stroke="#2563eb"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorAllowed)"
              />
              <Area
                type="monotone"
                dataKey="flagged"
                name="Flagged Requests"
                stroke="#d97706"
                strokeWidth={1.8}
                fillOpacity={1}
                fill="url(#colorFlagged)"
              />
              <Area
                type="monotone"
                dataKey="denied"
                name="Denied Requests"
                stroke="#dc2626"
                strokeWidth={1.8}
                fillOpacity={1}
                fill="url(#colorDenied)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
