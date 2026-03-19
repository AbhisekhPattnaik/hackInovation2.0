import React from 'react';
import './ChartComponents.css';

/**
 * Simple Line Chart Component
 * Displays data as a line graph
 */
export const LineChart = ({ data, title, xLabel, yLabel, height = 300 }) => {
  if (!data || data.length === 0) {
    return <div className="chart-placeholder">No data to display</div>;
  }

  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const range = maxValue - minValue || 1;

  const points = data.map((d, idx) => {
    const x = (idx / (data.length - 1)) * 100;
    const y = ((d.value - minValue) / range) * 100;
    return { ...d, x, y };
  });

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" className="chart-svg">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map(val => (
          <line
            key={`grid-${val}`}
            x1="0"
            y1={100 - val}
            x2="100"
            y2={100 - val}
            className="grid-line"
          />
        ))}

        {/* Line path */}
        <polyline
          points={points.map(p => `${p.x},${100 - p.y}`).join(' ')}
          className="chart-line"
          fill="none"
        />

        {/* Data points */}
        {points.map((point, idx) => (
          <circle
            key={`point-${idx}`}
            cx={point.x}
            cy={100 - point.y}
            r="2"
            className="chart-point"
          />
        ))}
      </svg>

      {/* Legend */}
      <div className="chart-legend">
        {data.map((d, idx) => (
          <div key={idx} className="legend-item">
            <span className="legend-label">{d.label}</span>
            <span className="legend-value">{d.value.toFixed(1)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Bar Chart Component
 * Displays data as vertical bars
 */
export const BarChart = ({ data, title, xLabel, yLabel }) => {
  if (!data || data.length === 0) {
    return <div className="chart-placeholder">No data to display</div>;
  }

  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <div className="bar-chart">
        {data.map((item, idx) => (
          <div key={idx} className="bar-group">
            <div className="bar-container">
              <div
                className="bar"
                style={{
                  height: `${(item.value / maxValue) * 100}%`,
                  backgroundColor: item.color || '#06b6d4'
                }}
                title={`${item.label}: ${item.value}`}
              />
            </div>
            <div className="bar-label">{item.label}</div>
            <div className="bar-value">{item.value.toFixed(1)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Pie Chart Component
 * Displays data as a pie/donut chart
 */
export const PieChart = ({ data, title, variant = 'pie' }) => {
  if (!data || data.length === 0) {
    return <div className="chart-placeholder">No data to display</div>;
  }

  const total = data.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -90;

  const slices = data.map((item, idx) => {
    const sliceAngle = (item.value / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + sliceAngle;
    currentAngle = endAngle;

    const startRad = (startAngle * Math.PI) / 180;
    const endRad = (endAngle * Math.PI) / 180;
    const r = 50;
    const innerR = variant === 'donut' ? 35 : 0;

    const x1 = 50 + r * Math.cos(startRad);
    const y1 = 50 + r * Math.sin(startRad);
    const x2 = 50 + r * Math.cos(endRad);
    const y2 = 50 + r * Math.sin(endRad);

    const largeArc = sliceAngle > 180 ? 1 : 0;

    let path = `M ${50} ${50} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    if (variant === 'donut') {
      const ix1 = 50 + innerR * Math.cos(startRad);
      const iy1 = 50 + innerR * Math.sin(startRad);
      const ix2 = 50 + innerR * Math.cos(endRad);
      const iy2 = 50 + innerR * Math.sin(endRad);
      path = `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} L ${ix2} ${iy2} A ${innerR} ${innerR} 0 ${largeArc} 0 ${ix1} ${iy1} Z`;
    }

    return { ...item, path, percentage: (item.value / total) * 100 };
  });

  const colors = [
    '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'
  ];

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <svg viewBox="0 0 100 100" className="pie-chart">
        {slices.map((slice, idx) => (
          <path
            key={idx}
            d={slice.path}
            fill={slice.color || colors[idx % colors.length]}
            stroke="#0a0e27"
            strokeWidth="1"
          />
        ))}
      </svg>

      {/* Legend */}
      <div className="pie-legend">
        {slices.map((slice, idx) => (
          <div key={idx} className="pie-legend-item">
            <span
              className="pie-color"
              style={{ backgroundColor: slice.color || colors[idx % colors.length] }}
            />
            <span className="pie-label">{slice.label}</span>
            <span className="pie-percentage">{slice.percentage.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Progress Ring Component
 * Displays single metric as a circular progress indicator
 */
export const ProgressRing = ({ value, max = 100, label, unit = '' }) => {
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (value / max) * circumference;

  return (
    <div className="progress-ring-container">
      <svg viewBox="0 0 100 100" className="progress-ring-svg">
        <circle
          cx="50"
          cy="50"
          r="45"
          className="progress-ring-bg"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          className="progress-ring-fill"
          style={{ strokeDashoffset }}
        />
      </svg>
      <div className="progress-content">
        <div className="progress-value">
          {value.toFixed(1)}<span className="progress-unit">{unit}</span>
        </div>
        <div className="progress-label">{label}</div>
      </div>
    </div>
  );
};

/**
 * Heat Map Component
 * Displays 2D data as a color-coded grid
 */
export const HeatMap = ({ data, title, xLabels, yLabels }) => {
  const maxValue = Math.max(...data.flat());
  const minValue = Math.min(...data.flat());
  const range = maxValue - minValue || 1;

  const getColor = (value) => {
    const normalized = (value - minValue) / range;
    if (normalized < 0.25) return '#0a0e27';
    if (normalized < 0.5) return '#10b981';
    if (normalized < 0.75) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <div className="heatmap">
        {data.map((row, rowIdx) => (
          <div key={rowIdx} className="heatmap-row">
            {row.map((value, colIdx) => (
              <div
                key={`${rowIdx}-${colIdx}`}
                className="heatmap-cell"
                style={{ backgroundColor: getColor(value) }}
                title={`${value.toFixed(1)}`}
              >
                {value.toFixed(0)}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Labels */}
      {(xLabels || yLabels) && (
        <div className="heatmap-labels">
          {yLabels && (
            <div className="heatmap-y-labels">
              {yLabels.map((label, idx) => (
                <div key={idx} className="heatmap-label">{label}</div>
              ))}
            </div>
          )}
          {xLabels && (
            <div className="heatmap-x-labels">
              {xLabels.map((label, idx) => (
                <div key={idx} className="heatmap-label">{label}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * Timeline Component
 * Displays events in chronological order
 */
export const Timeline = ({ events, title }) => {
  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <div className="timeline">
        {events.map((event, idx) => (
          <div key={idx} className="timeline-event">
            <div className="timeline-marker" />
            <div className="timeline-content">
              <div className="timeline-time">{event.time}</div>
              <div className="timeline-title">{event.title}</div>
              {event.description && (
                <div className="timeline-description">{event.description}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default {
  LineChart,
  BarChart,
  PieChart,
  ProgressRing,
  HeatMap,
  Timeline
};
