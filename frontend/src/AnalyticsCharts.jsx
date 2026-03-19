import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

/**
 * Performance Summary Chart
 * Displays key metrics in a bar chart format
 */
export const PerformanceSummaryChart = ({ performanceData }) => {
  if (!performanceData || !performanceData.metrics) {
    return <div className="chart-loading">Loading performance data...</div>;
  }

  const chartData = [
    {
      name: 'Total Appointments',
      value: performanceData.metrics?.total_appointments || 0,
      fill: '#06b6d4'
    },
    {
      name: 'Show Rate (%)',
      value: performanceData.metrics?.show_rate_percent || 0,
      fill: '#22c55e'
    },
    {
      name: 'No-Show Rate (%)',
      value: performanceData.metrics?.no_show_rate_percent || 0,
      fill: '#ef4444'
    },
    {
      name: 'Quality Score',
      value: performanceData.quality_score?.toFixed(1) || 0,
      fill: '#fbbf24'
    }
  ];

  return (
    <div className="chart-container">
      <h3 className="chart-title">Performance Metrics Overview</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="name" 
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis tick={{ fill: '#94a3b8' }} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 41, 0.9)', 
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '8px',
              color: '#f1f5f9'
            }}
          />
          <Bar dataKey="value" fill="#06b6d4" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * 7-Day Utilization Forecast Chart
 * Shows utilization trends and appointment count over 7 days
 */
export const UtilizationForecastChart = ({ forecastData }) => {
  if (!forecastData || !forecastData.forecast) {
    return <div className="chart-loading">Loading utilization forecast...</div>;
  }

  const chartData = forecastData.forecast.map((day, idx) => ({
    day: `Day ${idx + 1}`,
    utilization: day.utilization?.toFixed(0) || 0,
    appointments: day.appointments || 0,
    availableSlots: day.available_slots || 0
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">7-Day Utilization Forecast</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="day" 
            tick={{ fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis 
            yAxisId="left"
            tick={{ fill: '#94a3b8' }} 
            label={{ value: 'Utilization %', angle: -90, position: 'insideLeft' }}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Appointments', angle: 90, position: 'insideRight' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 41, 0.9)', 
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '8px',
              color: '#f1f5f9'
            }}
            formatter={(value) => value.toFixed(0)}
          />
          <Legend 
            wrapperStyle={{ color: '#cbd5e1', paddingTop: '20px' }}
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="utilization" 
            stroke="#06b6d4" 
            strokeWidth={3}
            dot={{ fill: '#06b6d4', r: 5 }}
            activeDot={{ r: 7 }}
            name="Utilization %"
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="appointments" 
            stroke="#22c55e" 
            strokeWidth={2}
            dot={{ fill: '#22c55e', r: 4 }}
            activeDot={{ r: 6 }}
            name="Appointments"
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Timing Metrics Chart
 * Displays consultation and wait times
 */
export const TimingMetricsChart = ({ performanceData }) => {
  if (!performanceData || !performanceData.timing_metrics) {
    return <div className="chart-loading">Loading timing metrics...</div>;
  }

  const chartData = [
    {
      name: 'Avg Consultation',
      time: performanceData.timing_metrics?.avg_consultation_minutes || 0,
      fill: '#06b6d4'
    },
    {
      name: 'Median Consultation',
      time: performanceData.timing_metrics?.median_consultation_minutes || 0,
      fill: '#0ea5e9'
    },
    {
      name: 'Avg Wait Time',
      time: performanceData.timing_metrics?.avg_wait_time_minutes || 0,
      fill: '#fbbf24'
    },
    {
      name: 'Median Wait Time',
      time: performanceData.timing_metrics?.median_wait_time_minutes || 0,
      fill: '#ef4444'
    }
  ];

  return (
    <div className="chart-container">
      <h3 className="chart-title">Timing Metrics (Minutes)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="name" 
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            angle={-30}
            textAnchor="end"
            height={100}
          />
          <YAxis tick={{ fill: '#94a3b8' }} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 41, 0.9)', 
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '8px',
              color: '#f1f5f9'
            }}
            formatter={(value) => `${value}m`}
          />
          <Bar dataKey="time" fill="#06b6d4" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Efficiency Metrics Pie Chart
 * Shows utilization percentage and appointments per day
 */
export const EfficiencyMetricsChart = ({ performanceData }) => {
  if (!performanceData || !performanceData.efficiency_metrics) {
    return <div className="chart-loading">Loading efficiency metrics...</div>;
  }

  const utilization = performanceData.efficiency_metrics?.utilization_percent || 0;
  const available = Math.max(0, 100 - utilization);

  const pieData = [
    { name: 'Utilized', value: utilization, fill: '#06b6d4' },
    { name: 'Available', value: available, fill: 'rgba(6, 182, 212, 0.2)' }
  ];

  return (
    <div className="chart-container">
      <h3 className="chart-title">Capacity Utilization</h3>
      <div className="efficiency-chart-wrapper">
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(15, 23, 41, 0.9)', 
                border: '1px solid rgba(6, 182, 212, 0.3)',
                borderRadius: '8px',
                color: '#f1f5f9'
              }}
              formatter={(value) => `${value}%`}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="efficiency-stats">
          <div className="efficiency-stat">
            <span className="stat-label">Utilization</span>
            <span className="stat-value">{utilization}%</span>
          </div>
          <div className="efficiency-stat">
            <span className="stat-label">Appointments/Day</span>
            <span className="stat-value">{performanceData.efficiency_metrics?.appointments_per_day || 0}</span>
          </div>
          <div className="efficiency-stat">
            <span className="stat-label">Working Days</span>
            <span className="stat-value">{performanceData.efficiency_metrics?.working_days || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Quality Score Gauge-like visualization
 * Shows quality score with progress indicator
 */
export const QualityScoreChart = ({ performanceData }) => {
  if (!performanceData) {
    return <div className="chart-loading">Loading quality metrics...</div>;
  }

  const score = performanceData.quality_score?.toFixed(1) || 0;
  const maxScore = 100;
  const percentage = (score / maxScore) * 100;
  
  let scoreColor = '#ef4444'; // Red for < 60
  if (score >= 80) scoreColor = '#22c55e'; // Green for >= 80
  else if (score >= 70) scoreColor = '#fbbf24'; // Yellow for >= 70
  else if (score >= 60) scoreColor = '#f97316'; // Orange for >= 60

  return (
    <div className="chart-container quality-score-container">
      <h3 className="chart-title">Quality Performance Score</h3>
      <div className="quality-score-display">
        <div className="quality-gauge">
          <div className="gauge-background">
            <div 
              className="gauge-fill" 
              style={{ 
                width: `${percentage}%`,
                backgroundColor: scoreColor
              }}
            ></div>
          </div>
          <div className="gauge-label">
            <span className="gauge-score">{score}</span>
            <span className="gauge-max">/ 100</span>
          </div>
        </div>
        <div className="quality-interpretation">
          <p className="quality-text">
            {score >= 80 && "🎉 Excellent performance! Keep maintaining these standards."}
            {score >= 70 && score < 80 && "👍 Good performance. Small improvements could boost scores further."}
            {score >= 60 && score < 70 && "⚠️ Room for improvement. Focus on patient satisfaction."}
            {score < 60 && "❌ Needs attention. Consider reviewing your processes."}
          </p>
        </div>
      </div>
    </div>
  );
};
