import React from 'react';

/**
 * Performance Metrics Card Component
 * Displays doctor performance statistics
 */
export const PerformanceCard = ({ data }) => {
  if (!data) return <div className="loading">Loading...</div>;

  const metrics = data.metrics || {};
  const timing = data.timing_metrics || {};
  const efficiency = data.efficiency_metrics || {};
  const qualityScore = data.quality_score || 0;

  return (
    <div className="performance-card">
      <div className="card-header">
        <h3>30-Day Performance</h3>
        <span className="quality-badge" style={{
          backgroundColor: qualityScore > 75 ? '#10b981' : qualityScore > 50 ? '#f59e0b' : '#ef4444'
        }}>
          Quality: {qualityScore.toFixed(1)}/100
        </span>
      </div>

      <div className="metrics-grid">
        <div className="metric-item">
          <div className="metric-label">Total Appointments</div>
          <div className="metric-value">{metrics.total_appointments || 0}</div>
        </div>
        <div className="metric-item">
          <div className="metric-label">Show Rate</div>
          <div className="metric-value success">{metrics.show_rate_percent || 0}%</div>
        </div>
        <div className="metric-item">
          <div className="metric-label">No-Show Rate</div>
          <div className="metric-value warning">{metrics.no_show_rate_percent || 0}%</div>
        </div>
        <div className="metric-item">
          <div className="metric-label">Avg Consultation</div>
          <div className="metric-value">{timing.avg_consultation_minutes || 0} min</div>
        </div>
        <div className="metric-item">
          <div className="metric-label">Utilization</div>
          <div className="metric-value">{efficiency.utilization_percent || 0}%</div>
        </div>
        <div className="metric-item">
          <div className="metric-label">Patients/Day</div>
          <div className="metric-value">{efficiency.appointments_per_day || 0}</div>
        </div>
      </div>
    </div>
  );
};

/**
 * Utilization Forecast Chart
 * Displays 7-day utilization prediction
 */
export const UtilizationForecast = ({ data }) => {
  if (!data) return <div className="loading">Loading...</div>;

  const forecast = data.forecast || [];
  const maxUtilization = Math.max(...(forecast.map(f => f.utilization) || [0]));

  return (
    <div className="forecast-chart-container">
      <h4>7-Day Utilization Forecast</h4>
      <div className="forecast-grid">
        {forecast.map((day, idx) => (
          <div key={idx} className="forecast-day">
            <div className="forecast-bar-container">
              <div
                className="forecast-bar"
                style={{
                  height: `${(day.utilization / maxUtilization) * 100}%`,
                  backgroundColor: day.utilization > 80 ? '#ef4444' : day.utilization > 60 ? '#f59e0b' : '#10b981'
                }}
              />
            </div>
            <div className="forecast-label">{day.utilization.toFixed(0)}%</div>
            <div className="forecast-date">Day {idx + 1}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Queue Status Card
 * Real-time queue information
 */
export const QueueStatusCard = ({ data }) => {
  if (!data) return <div className="loading">Loading...</div>;

  const queueSize = data.current_queue_size || 0;
  const avgWaitTime = data.average_wait_time || 0;
  const highPriority = data.high_priority_count || 0;

  return (
    <div className="queue-status-card">
      <div className="card-header">
        <h3>Queue Status</h3>
        <span className={`status-badge ${queueSize > 5 ? 'danger' : queueSize > 3 ? 'warning' : 'success'}`}>
          {queueSize > 5 ? 'High' : queueSize > 3 ? 'Medium' : 'Low'} Load
        </span>
      </div>

      <div className="queue-metrics">
        <div className="queue-item">
          <div className="queue-icon">👥</div>
          <div className="queue-info">
            <div className="queue-label">In Queue</div>
            <div className="queue-value">{queueSize} patients</div>
          </div>
        </div>
        <div className="queue-item">
          <div className="queue-icon">⏱️</div>
          <div className="queue-info">
            <div className="queue-label">Avg Wait</div>
            <div className="queue-value">{avgWaitTime} min</div>
          </div>
        </div>
        <div className="queue-item">
          <div className="queue-icon">🔴</div>
          <div className="queue-info">
            <div className="queue-label">High Priority</div>
            <div className="queue-value">{highPriority} patients</div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Delay Risk Indicator
 * Shows probability doctor is running behind
 */
export const DelayRiskIndicator = ({ data }) => {
  if (!data) return <div className="loading">Loading...</div>;

  const delayProb = data.delay_probability || 0;
  const estimatedDelay = data.estimated_delay_minutes || 0;
  const riskLevel = delayProb > 0.7 ? 'high' : delayProb > 0.4 ? 'medium' : 'low';

  return (
    <div className={`delay-risk-card ${riskLevel}`}>
      <div className="risk-header">Delay Risk</div>
      <div className="risk-meter">
        <div class="risk-bar">
          <div className="risk-fill" style={{width: `${delayProb * 100}%`}} />
        </div>
        <div className="risk-percentage">{(delayProb * 100).toFixed(0)}%</div>
      </div>
      <div className="risk-details">
        <span className="risk-label">Est. Delay:</span>
        <span className="risk-value">{estimatedDelay} min</span>
      </div>
    </div>
  );
};

/**
 * Insight Card Component
 * Displays AI-generated insights with recommendations
 */
export const InsightCard = ({ insight, recommendation }) => {
  const getTypeIcon = (type) => {
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'alert': return '❌';
      case 'info': return 'ℹ';
      default: return '•';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'success': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'alert': return '#ef4444';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  return (
    <div className="insight-card-item" style={{borderLeftColor: getTypeColor(insight.type)}}>
      <div className="insight-header">
        <span className="insight-type-icon" style={{color: getTypeColor(insight.type)}}>
          {getTypeIcon(insight.type)}
        </span>
        <h4>{insight.title}</h4>
        <span className="insight-priority">{insight.priority}</span>
      </div>
      <p className="insight-message">{insight.message}</p>
      {recommendation && (
        <div className="insight-recommendation">
          <strong>Action:</strong> {recommendation}
        </div>
      )}
    </div>
  );
};

/**
 * Optimization Suggestion Card
 * Shows RL-based queue optimization recommendations
 */
export const OptimizationCard = ({ data, onApply }) => {
  if (!data || !data.optimized_queue) return <div className="loading">Loading...</div>;

  const improvement = data.improvement_percentage || 0;

  return (
    <div className="optimization-card">
      <div className="card-header">
        <h3>Queue Optimization</h3>
        <span className="improvement-badge">
          {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}% better
        </span>
      </div>

      <div className="optimization-details">
        <p className="optimization-description">
          Reordering the queue can reduce wait times and improve patient satisfaction.
        </p>

        <div className="optimization-comparison">
          <div className="comparison-item">
            <div className="comparison-label">Current Avg Wait</div>
            <div className="comparison-value">{data.current_avg_wait || 0} min</div>
          </div>
          <div className="comparison-arrow">→</div>
          <div className="comparison-item">
            <div className="comparison-label">Optimized Avg Wait</div>
            <div className="comparison-value">{data.optimized_avg_wait || 0} min</div>
          </div>
        </div>

        <button className="btn-apply-optimization" onClick={onApply}>
          Apply Optimization
        </button>
      </div>
    </div>
  );
};

/**
 * Report Status Timeline
 * Shows the status progression of medical reports
 */
export const ReportTimeline = ({ reports }) => {
  const statusOrder = ['pending', 'reviewed', 'approved', 'flagged', 'rejected', 'completed'];
  
  const countByStatus = reports.reduce((acc, report) => {
    acc[report.status] = (acc[report.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="report-timeline">
      <h4>Report Status Distribution</h4>
      <div className="timeline-bar">
        {statusOrder.map(status => (
          <div
            key={status}
            className="timeline-segment"
            style={{width: `${(countByStatus[status] || 0) / reports.length * 100}%`}}
            title={`${status}: ${countByStatus[status] || 0} reports`}
          />
        ))}
      </div>
      <div className="timeline-legend">
        {statusOrder.map(status => (
          <div key={status} className="timeline-label">
            <span className="label-status">{status}</span>
            <span className="label-count">{countByStatus[status] || 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * No Data Placeholder
 * Shows when no data is available
 */
export const NoDataPlaceholder = ({ message = "No data available" }) => {
  return (
    <div className="no-data-placeholder">
      <div className="no-data-icon">📊</div>
      <p>{message}</p>
    </div>
  );
};
