import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { ACCESS_DISTRIBUTION } from '../data/mockSecurityData';

function DonutTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="chart-tooltip">
        <div className="chart-tooltip-row">
          <span
            className="chart-tooltip-dot"
            style={{ backgroundColor: data.payload.color }}
          />
          <span className="chart-tooltip-label">{data.name}:</span>
          <span className="chart-tooltip-val">
            {data.value.toLocaleString()}
          </span>
        </div>
      </div>
    );
  }
  return null;
}

export default function AccessDistributionDonut() {
  const totalRequests = ACCESS_DISTRIBUTION.reduce(
    (acc, curr) => acc + curr.value,
    0
  );

  return (
    <div className="panel-card donut-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <h3 className="panel-title">Access Distribution</h3>
          <span className="panel-subtitle">Current enforcement split</span>
        </div>
      </div>
      <div className="panel-body donut-body">
        <div className="donut-chart-wrapper">
          <ResponsiveContainer width="100%" height={210}>
            <PieChart>
              <Tooltip content={<DonutTooltip />} />
              <Pie
                data={ACCESS_DISTRIBUTION}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={88}
                paddingAngle={3}
                dataKey="value"
              >
                {ACCESS_DISTRIBUTION.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="donut-center-stat">
            <span className="donut-center-val">
              {totalRequests.toLocaleString()}
            </span>
            <span className="donut-center-lbl">Total Requests</span>
          </div>
        </div>

        <div className="donut-legend-list">
          {ACCESS_DISTRIBUTION.map((item) => {
            const pct = ((item.value / totalRequests) * 100).toFixed(1);
            return (
              <div key={item.name} className="donut-legend-item">
                <div className="donut-legend-left">
                  <span
                    className="donut-legend-indicator"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="donut-legend-name">{item.name}</span>
                </div>
                <div className="donut-legend-right">
                  <span className="donut-legend-count">
                    {item.value.toLocaleString()}
                  </span>
                  <span className="donut-legend-pct">({pct}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
