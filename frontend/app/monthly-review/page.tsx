"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/layout/navbar";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { ArrowUpRight, Calendar, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import { analyticsService } from "@/services/analytics";
import { goalsService } from "@/services/goals";

export default function MonthlyReviewPage() {
  const currentMonthStr = new Date().toISOString().slice(0, 7);
  const [month, setMonth] = useState(currentMonthStr);
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
        console.error("Monthly review load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [month]);

  const totalHours = analytics?.total_hours_spent ?? 0;
  const activeCount = analytics?.active_goals_count ?? goals.length;
  const completedCount = analytics?.completed_goals_count ?? 0;
  const avgCompletion = Math.round(analytics?.overall_completion_pct ?? 0);
  const bestStreak = analytics?.current_streak ? `${analytics.current_streak} Weeks` : "0 Weeks";

  const stats = [
    { label: "Total Study & Work Hours", value: `${totalHours} hrs`, change: "—" },
    { label: "Active & Finished Goals", value: `${activeCount + completedCount}`, change: "—" },
    { label: "Avg Weekly Completion", value: `${avgCompletion}%`, change: "—" },
    { label: "Best Consistency Streak", value: bestStreak, change: "—" },
  ];

  const chartData = analytics?.weekly_progress_data?.length
    ? analytics.weekly_progress_data.map((wp: any) => ({
        name: `Week ${wp.week}`,
        hours: Math.round((wp.time_pct ?? 0) * 0.1),
        tasksPct: Math.round(wp.task_pct ?? 0)
      }))
    : [];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Monthly Review</h1>
            <p className="text-slate-500 mt-1">Review measurable progress, hours, and consistency trends across all categories.</p>
          </div>
          
          <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3.5 py-2 shadow-sm">
            <Calendar size={18} className="text-slate-500" />
            <input 
              type="month" 
              className="outline-none text-slate-700 bg-transparent text-sm font-semibold"
              value={month}
              onChange={e => setMonth(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
            <p>Loading monthly metrics...</p>
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.map((stat, i) => (
                <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">{stat.label}</p>
                  <div className="flex items-baseline justify-between mt-2">
                    <h3 className="text-2xl font-extrabold text-slate-900">{stat.value}</h3>
                    {stat.change && stat.change !== "—" ? (
                      <span className="flex items-center text-xs font-semibold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                        <ArrowUpRight size={14} />
                        {stat.change}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400 font-medium">—</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Activity by Week Chart */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-bold text-slate-900">Task Completion by Week (%)</h2>
                  <span className="text-xs text-slate-500">Month Overview</span>
                </div>
                <div className="h-72">
                  {chartData.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center px-4">
                      <p className="font-medium text-slate-600">No check-in data recorded for this month.</p>
                      <p className="text-xs text-slate-400 mt-1 max-w-sm">Complete weekly check-ins to view monthly completion trends.</p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} stroke="#94a3b8" />
                        <YAxis axisLine={false} tickLine={false} fontSize={12} stroke="#94a3b8" unit="%" domain={[0, 100]} />
                        <Tooltip cursor={{ fill: "#f8fafc" }} />
                        <Bar dataKey="tasksPct" name="Task Completion %" fill="#2563eb" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>

              {/* Monthly AI Summary & Observations */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center gap-2">
                  <Sparkles size={20} className="text-purple-600" />
                  <h2 className="text-lg font-bold text-slate-900">AI Retrospective & Insights</h2>
                </div>
                
                {analytics?.recent_progress?.length > 0 ? (
                  <>
                    <p className="text-slate-700 text-sm leading-relaxed">
                      During this period, your average completion rate reached {avgCompletion}%, logging a total of {totalHours} productive hours across {activeCount + completedCount} goals.
                    </p>

                    <div className="bg-blue-50/70 p-4 rounded-xl border border-blue-200 text-xs space-y-1.5">
                      <h4 className="font-bold text-blue-900 flex items-center gap-1.5 text-sm">
                        <CheckCircle2 size={16} className="text-blue-600" /> Key Observations
                      </h4>
                      <ul className="list-disc pl-5 text-blue-800 space-y-1">
                        <li>Maintained an active consistency streak of {analytics?.current_streak ?? 0} weeks.</li>
                        <li>Recorded {analytics?.recent_progress?.length} progress updates during this cycle.</li>
                        <li>Average task fulfillment rate recorded at {avgCompletion}%.</li>
                      </ul>
                    </div>

                    <div className="bg-amber-50/70 p-4 rounded-xl border border-amber-200 text-xs space-y-1.5">
                      <h4 className="font-bold text-amber-900 text-sm">Target Areas for Next Month</h4>
                      <ul className="list-disc pl-5 text-amber-800 space-y-1">
                        <li>Continue conducting timely weekly check-ins to maintain streak momentum.</li>
                        <li>Keep planned hours aligned with capacity to ensure steady progress.</li>
                      </ul>
                    </div>
                  </>
                ) : (
                  <div className="py-8 text-center text-slate-500">
                    <p className="font-medium text-slate-700">No Check-in Records for this Review Period</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                      AI retrospective and performance insights will automatically generate once you submit weekly check-ins for your active goals.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
