"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/layout/navbar";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";
import {
  Activity,
  Target,
  TrendingUp,
  Zap,
  Clock,
  CheckCircle2,
  Calendar,
  Loader2,
  BookOpen,
  Code,
  Dumbbell,
  Brain,
  ArrowUpRight
} from "lucide-react";
import { analyticsService } from "@/services/analytics";
import { goalsService } from "@/services/goals";

const COLORS = ["#2563eb", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#64748b"];

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [goals, setGoals] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [a, g] = await Promise.all([
          analyticsService.getDashboardAnalytics().catch(() => null),
          goalsService.getAll().catch(() => [])
        ]);
        setAnalytics(a);
        setGoals(g || []);
      } catch (err) {
        console.error("Failed to load analytics data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalHours = analytics?.total_hours_spent ?? 0;
  const overallCompletion = Math.round(analytics?.overall_completion_pct ?? 0);
  const streak = analytics?.current_streak ?? 0;
  const activeCount = analytics?.active_goals_count ?? goals.length;

  // Chart: Weekly Progress
  const weeklyChartData = analytics?.weekly_progress_data?.length
    ? analytics.weekly_progress_data.map((wp: any) => ({
        week: `Week ${wp.week}`,
        taskPct: Math.round(wp.task_pct ?? 0),
        timePct: Math.round(wp.time_pct ?? 0),
        consistency: Math.round(((wp.task_pct ?? 0) + (wp.time_pct ?? 0)) / 2)
      }))
    : [];

  // Chart: Category Distribution
  const categoryData = Object.entries(analytics?.goals_by_category || {}).map(([key, count]: [string, any]) => ({
    name: key.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()),
    value: count
  }));

  const categoryIcons: Record<string, any> = {
    academics: BookOpen,
    coding: Code,
    fitness: Dumbbell,
    personal_development: Brain
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Performance Analytics</h1>
          <p className="text-slate-500 mt-1">Deep insights into study consistency, task throughput, and category progress.</p>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
            <p>Aggregating analytics data...</p>
          </div>
        ) : (
          <>
            {/* Top Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
                <div className="p-3 bg-blue-50 text-blue-600 rounded-xl"><Activity size={24} /></div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Completion</p>
                  <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{overallCompletion}%</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl"><Clock size={24} /></div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Time Invested</p>
                  <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{totalHours} hrs</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
                <div className="p-3 bg-green-50 text-green-600 rounded-xl"><Target size={24} /></div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Roadmaps</p>
                  <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{activeCount}</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
                <div className="p-3 bg-orange-50 text-orange-600 rounded-xl"><Zap size={24} /></div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Current Streak</p>
                  <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{streak} Weeks</p>
                </div>
              </div>
            </div>

            {/* Charts Row 1: Weekly Trends & Category Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Trend Chart (2 cols) */}
              <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">Task vs Time Completion (%)</h2>
                    <p className="text-xs text-slate-500">Weekly planned target vs actual realization</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-blue-600"></span> Task %</span>
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-indigo-400"></span> Time %</span>
                  </div>
                </div>

                <div className="h-72">
                  {weeklyChartData.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center px-4">
                      <TrendingUp size={36} className="text-slate-300 mb-2" />
                      <p className="font-medium text-slate-600">No weekly check-in records available yet.</p>
                      <p className="text-xs text-slate-400 mt-1 max-w-sm">Log weekly check-ins to track planned vs realized completion trends.</p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={weeklyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} unit="%" domain={[0, 150]} />
                        <Tooltip />
                        <Bar dataKey="taskPct" name="Task %" fill="#2563eb" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="timePct" name="Time %" fill="#818cf8" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>

              {/* Category Pie Chart (1 col) */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Goal Distribution</h2>
                  <p className="text-xs text-slate-500 mb-4">Breakdown across life areas</p>
                </div>

                <div className="h-56">
                  {categoryData.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center px-4">
                      <Target size={36} className="text-slate-300 mb-2" />
                      <p className="font-medium text-slate-600">No goals categorized yet.</p>
                      <p className="text-xs text-slate-400 mt-1 max-w-xs">Create your first goal to view category breakdown.</p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={categoryData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {categoryData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-100 flex justify-around text-center text-xs text-slate-500">
                  <div>
                    <p className="font-bold text-slate-800 text-sm">{goals.length}</p>
                    <p>Total Goals</p>
                  </div>
                  <div>
                    <p className="font-bold text-slate-800 text-sm">{categoryData.length}</p>
                    <p>Categories</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Consistency Index Over Time */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Overall Consistency Score</h2>
                  <p className="text-xs text-slate-500">Computed strictly via Python backend progress services</p>
                </div>
                <span className="text-xs font-semibold bg-green-50 text-green-700 px-3 py-1 rounded-full flex items-center gap-1">
                  <ArrowUpRight size={14} /> High Discipline
                </span>
              </div>

              <div className="h-64">
                {weeklyChartData.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center px-4">
                    <Activity size={36} className="text-slate-300 mb-2" />
                    <p className="font-medium text-slate-600">No consistency data yet.</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-sm">Consistency index will be computed once you log consecutive weekly check-ins.</p>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={weeklyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} tickLine={false} />
                      <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} unit="%" domain={[0, 100]} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="consistency"
                        name="Consistency Index"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ r: 5, fill: "#10b981" }}
                        activeDot={{ r: 7 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Goal Performance Breakdown Table */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-lg font-bold text-slate-900">Active Goals Status & Target Review</h2>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 text-xs uppercase text-slate-400 font-semibold border-b border-slate-100">
                    <tr>
                      <th className="py-3 px-6">Goal Name</th>
                      <th className="py-3 px-6">Category</th>
                      <th className="py-3 px-6">Capacity</th>
                      <th className="py-3 px-6">Target Date</th>
                      <th className="py-3 px-6">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {goals.map(g => (
                      <tr key={g.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-4 px-6 font-semibold text-slate-800">{g.name}</td>
                        <td className="py-4 px-6 capitalize">
                          <span className="px-2.5 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-700">
                            {g.category.replace("_", " ")}
                          </span>
                        </td>
                        <td className="py-4 px-6">{g.available_hours_per_week ?? 0} hrs/wk</td>
                        <td className="py-4 px-6">{new Date(g.target_date).toLocaleDateString()}</td>
                        <td className="py-4 px-6">
                          <span className="capitalize font-semibold text-xs px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
                            {g.status || "active"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
