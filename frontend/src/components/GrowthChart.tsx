/**
 * Growth Chart Component
 * Interactive charts showing company growth metrics over time
 */

'use client';

import { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { TrendingUp, Users, DollarSign, Briefcase } from 'lucide-react';

import { GrowthMetrics, ChartDataPoint } from '@/types';
import { formatCurrency, formatRelativeDate } from '@/lib/utils';

interface GrowthChartProps {
  companyName: string;
  metrics: GrowthMetrics;
}

type ChartType = 'funding' | 'team' | 'jobs' | 'combined';

export default function GrowthChart({ companyName, metrics }: GrowthChartProps) {
  const [activeChart, setActiveChart] = useState<ChartType>('combined');

  // Custom Tooltip
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200">
          <p className="text-sm font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center space-x-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-600">{entry.name}:</span>
              <span className="font-bold text-gray-900">
                {entry.name === 'Funding'
                  ? formatCurrency(entry.value as number)
                  : entry.value?.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  // Chart buttons
  const chartButtons = [
    { type: 'combined' as ChartType, label: 'Overview', icon: TrendingUp },
    { type: 'funding' as ChartType, label: 'Funding', icon: DollarSign },
    { type: 'team' as ChartType, label: 'Team', icon: Users },
    { type: 'jobs' as ChartType, label: 'Jobs', icon: Briefcase },
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">
            Growth Metrics
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {companyName} · Historical Performance
          </p>
        </div>

        {/* Chart Type Selector */}
        <div className="flex space-x-2">
          {chartButtons.map(({ type, label, icon: Icon }) => (
            <button
              key={type}
              onClick={() => setActiveChart(type)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center space-x-2 ${
                activeChart === type
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Combined Chart */}
      {activeChart === 'combined' && (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={metrics.timeSeries}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="date"
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              yAxisId="left"
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => value.toLocaleString()}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="team_size"
              stroke="#3B82F6"
              strokeWidth={3}
              name="Team Size"
              dot={{ fill: '#3B82F6', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="job_posts"
              stroke="#10B981"
              strokeWidth={3}
              name="Job Posts"
              dot={{ fill: '#10B981', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="funding"
              stroke="#F59E0B"
              strokeWidth={3}
              name="Funding"
              dot={{ fill: '#F59E0B', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      {/* Funding Area Chart */}
      {activeChart === 'funding' && (
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={metrics.timeSeries}>
            <defs>
              <linearGradient id="colorFunding" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" stroke="#6B7280" style={{ fontSize: '12px' }} />
            <YAxis
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="funding"
              stroke="#F59E0B"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorFunding)"
              name="Funding"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Team Growth Area Chart */}
      {activeChart === 'team' && (
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={metrics.timeSeries}>
            <defs>
              <linearGradient id="colorTeam" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" stroke="#6B7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="team_size"
              stroke="#3B82F6"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorTeam)"
              name="Team Size"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Job Posts Bar Chart */}
      {activeChart === 'jobs' && (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={metrics.timeSeries}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" stroke="#6B7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              dataKey="job_posts"
              fill="#10B981"
              name="Job Posts"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      )}

      {/* Key Metrics Summary */}
      <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Current Team</p>
          <p className="text-2xl font-bold text-blue-600">
            {metrics.currentTeamSize}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            +{metrics.teamGrowthRate.toFixed(1)}% growth
          </p>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Total Funding</p>
          <p className="text-2xl font-bold text-yellow-600">
            {formatCurrency(metrics.totalFunding)}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {metrics.fundingStage}
          </p>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Active Jobs</p>
          <p className="text-2xl font-bold text-green-600">
            {metrics.activeJobs}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {metrics.jobVelocity.toFixed(1)}x velocity
          </p>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Last Updated</p>
          <p className="text-2xl font-bold text-gray-600">
            {formatRelativeDate(metrics.lastUpdated)}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Real-time sync
          </p>
        </div>
      </div>
    </div>
  );
}
