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

export default function AccessDistributionDonut({ data }) {
  const chartData = data && data.length > 0 ? data : ACCESS_DISTRIBUTION;

  const totalRequests = chartData.reduce(
    (acc, curr) => acc + curr.value,
    0
  );

  return (
    <div className="panel-card donut-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <h3 className="panel-title">Access Distribution</h3>
          <span className="panel-subtitle">Live enforcement split (Approved / Denied / Throttled)</span>
        </div>
      </div>
      <div className="panel-body donut-body">
        <div className="donut-chart-wrapper">
          <ResponsiveContainer width="100%" height={210}>
            <PieChart>
              <Tooltip content={<DonutTooltip />} />
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={88}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="donut-center-metric">
            <span className="donut-center-value">
              {totalRequests.toLocaleString()}
            </span>
            <span className="donut-center-label">Evaluations</span>
          </div>
        </div>

        <div className="donut-legend">
          {chartData.map((item, idx) => {
            const pct =
              totalRequests > 0
                ? ((item.value / totalRequests) * 100).toFixed(1)
                : 0;
            return (
              <div key={idx} className="legend-row">
                <div className="legend-indicator">
                  <span
                    className="legend-color-dot"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="legend-name">{item.name}</span>
                </div>
                <div className="legend-values">
                  <span className="legend-count">
                    {item.value.toLocaleString()}
                  </span>
                  <span className="legend-percent">{pct}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
