"use client";

import React, { useEffect, useState } from "react";
import Navbar from "@/components/layout/navbar";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Activity, Target, TrendingUp, Zap, Plus, CheckCircle, BookOpen, Dumbbell, Code, Brain, Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";
import { analyticsService } from "@/services/analytics";
import { goalsService } from "@/services/goals";

export default function DashboardPage() {
  const { user } = useAuth();
  const [greeting, setGreeting] = useState("Welcome");
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [goals, setGoals] = useState<any[]>([]);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");

    async function loadData() {
      try {
        setLoading(true);
        const [analyticsData, goalsData] = await Promise.all([
          analyticsService.getDashboardAnalytics().catch(() => null),
          goalsService.getAll().catch(() => [])
        ]);
        setAnalytics(analyticsData);
        setGoals(goalsData || []);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const overallProgress = Math.round(analytics?.overall_completion_pct ?? 0);
  const activeGoalsCount = analytics?.active_goals_count ?? goals.length;
  const weeklyCompletion = Math.round(analytics?.weekly_completion_pct ?? 0);
  const currentStreak = analytics?.current_streak ?? 0;

  // Chart data from analytics
  const chartData = analytics?.weekly_progress_data?.length
    ? analytics.weekly_progress_data.map((wp: any) => ({
        week: `Week ${wp.week}`,
        taskPct: Math.round(wp.task_pct ?? 0),
        timePct: Math.round(wp.time_pct ?? 0)
      }))
    : [];

  const categoryIcons: Record<string, any> = {
    academics: { icon: BookOpen, color: "bg-blue-100 text-blue-600" },
    coding: { icon: Code, color: "bg-purple-100 text-purple-600" },
    fitness: { icon: Dumbbell, color: "bg-green-100 text-green-600" },
    personal_development: { icon: Brain, color: "bg-orange-100 text-orange-600" },
  };

  return (
    <div className="flex flex-col w-full min-w-0">
      <div className="hidden md:block mb-6">
        <Navbar />
      </div>
      
      <div className="w-full min-w-0 space-y-6 sm:space-y-8">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 break-words">
              {greeting}, {user?.name || "Student"} 👋
            </h1>
            <p className="text-slate-500 mt-1 text-sm sm:text-base">Here is a summary of your active learning and personal progress.</p>
          </div>
          <div className="flex flex-wrap sm:flex-nowrap gap-2.5 sm:gap-3 w-full sm:w-auto">
            <Link
              href="/goals/new"
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 bg-white border border-slate-200 text-slate-700 px-3.5 sm:px-4 py-2 rounded-lg hover:bg-slate-50 transition-colors shadow-sm font-medium text-sm whitespace-nowrap"
            >
              <Plus size={18} className="shrink-0" /> <span>Create Goal</span>
            </Link>
            <Link
              href="/goals"
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 bg-blue-600 text-white px-3.5 sm:px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm font-medium text-sm whitespace-nowrap"
            >
              <CheckCircle size={18} className="shrink-0" /> <span>View Goals</span>
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
            <p className="text-sm">Loading your dashboard analytics...</p>
          </div>
        ) : (
          <>
            {/* Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <div className="bg-white p-4 sm:p-5 lg:p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3.5 sm:gap-4 min-w-0">
                <div className="p-3 bg-blue-50 text-blue-600 rounded-xl shrink-0"><Activity size={24} /></div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider truncate">Overall Progress</p>
                  <p className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-0.5">{overallProgress}%</p>
                </div>
              </div>
              <div className="bg-white p-4 sm:p-5 lg:p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3.5 sm:gap-4 min-w-0">
                <div className="p-3 bg-purple-50 text-purple-600 rounded-xl shrink-0"><Target size={24} /></div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider truncate">Active Goals</p>
                  <p className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-0.5">{activeGoalsCount}</p>
                </div>
              </div>
              <div className="bg-white p-4 sm:p-5 lg:p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3.5 sm:gap-4 min-w-0">
                <div className="p-3 bg-green-50 text-green-600 rounded-xl shrink-0"><TrendingUp size={24} /></div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider truncate">Weekly Completion</p>
                  <p className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-0.5">{weeklyCompletion}%</p>
                </div>
              </div>
              <div className="bg-white p-4 sm:p-5 lg:p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3.5 sm:gap-4 min-w-0">
                <div className="p-3 bg-orange-50 text-orange-600 rounded-xl shrink-0"><Zap size={24} /></div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider truncate">Current Streak</p>
                  <p className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-0.5">{currentStreak} Weeks</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 min-w-0">
              {/* Main Content Area */}
              <div className="lg:col-span-2 space-y-6 sm:space-y-8 min-w-0">
                {/* Weekly Progress Chart */}
                <div className="bg-white p-4 sm:p-6 rounded-xl border border-slate-200 shadow-sm min-w-0 overflow-hidden">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 sm:gap-4 mb-6">
                    <div>
                      <h2 className="text-base sm:text-lg font-bold text-slate-900">Weekly Progress Over Time</h2>
                      <p className="text-xs text-slate-500">Task completion percentage by week</p>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
                      <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-blue-600"></span> Task %</span>
                      <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-indigo-300"></span> Time %</span>
                    </div>
                  </div>
                  {chartData.length === 0 ? (
                    <div className="h-56 sm:h-64 flex flex-col items-center justify-center text-slate-400 text-center px-4">
                      <Activity size={36} className="text-slate-300 mb-2" />
                      <p className="font-medium text-slate-600 text-sm">No weekly check-in data yet.</p>
                      <p className="text-xs text-slate-400 mt-1 max-w-sm">Complete your weekly check-ins to track task and time completion trends here.</p>
                    </div>
                  ) : (
                    <div className="h-56 sm:h-64 min-w-0 w-full overflow-hidden">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                          <defs>
                            <linearGradient id="taskColor" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#2563eb" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                            </linearGradient>
                            <linearGradient id="timeColor" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#818cf8" stopOpacity={0.6}/>
                              <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="week" stroke="#94a3b8" fontSize={11} tickLine={false} />
                          <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} unit="%" domain={[0, 100]} />
                          <Tooltip />
                          <Area type="monotone" dataKey="taskPct" name="Task Completion" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#taskColor)" />
                          <Area type="monotone" dataKey="timePct" name="Time Completion" stroke="#818cf8" strokeWidth={2} fillOpacity={1} fill="url(#timeColor)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>

                {/* Focus Areas / Goals */}
                <div className="bg-white p-4 sm:p-6 rounded-xl border border-slate-200 shadow-sm min-w-0">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-base sm:text-lg font-bold text-slate-900">Active Goals & Focus Areas</h2>
                    <Link href="/goals" className="text-xs sm:text-sm text-blue-600 hover:underline font-medium flex items-center gap-1">
                      View all <ArrowRight size={14} />
                    </Link>
                  </div>
                  
                  {goals.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      <p className="text-sm">No active goals yet.</p>
                      <Link href="/goals/new" className="text-blue-600 font-medium hover:underline text-sm mt-2 inline-block">
                        Create your first goal →
                      </Link>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                      {goals.slice(0, 4).map((g) => {
                        const iconData = categoryIcons[g.category] || { icon: Brain, color: "bg-blue-100 text-blue-600" };
                        const IconComponent = iconData.icon;

                        return (
                          <Link
                            key={g.id}
                            href={`/goals/${g.id}`}
                            className="p-3.5 sm:p-4 border border-slate-100 rounded-xl hover:border-blue-200 hover:shadow-sm transition-all flex flex-col justify-between group min-w-0"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center gap-2.5 min-w-0">
                                <div className={`p-2 rounded-lg shrink-0 ${iconData.color}`}>
                                  <IconComponent size={18} />
                                </div>
                                <div className="min-w-0 flex-1">
                                  <h3 className="font-semibold text-slate-800 group-hover:text-blue-600 transition-colors truncate text-sm sm:text-base">
                                    {g.name}
                                  </h3>
                                  <p className="text-xs text-slate-400 capitalize truncate">{g.category.replace("_", " ")}</p>
                                </div>
                              </div>
                            </div>
                            <div className="mt-3">
                              <div className="flex justify-between text-xs text-slate-500 mb-1">
                                <span>{g.available_hours_per_week ?? 0} hrs/wk</span>
                                <span className="font-medium capitalize text-slate-700">{g.status}</span>
                              </div>
                              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-blue-600 h-1.5 rounded-full transition-all" style={{ width: `${Math.min(100, Math.max(0, g.progress_percentage ?? (g.status === "completed" ? 100 : 0)))}%` }}></div>
                              </div>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

              {/* Sidebar: Recent Activity & Quick Action */}
              <div className="space-y-6 min-w-0">
                <div className="bg-white p-4 sm:p-6 rounded-xl border border-slate-200 shadow-sm min-w-0">
                  <h2 className="text-base sm:text-lg font-bold text-slate-900 mb-4">Recent Progress Log</h2>
                  
                  {analytics?.recent_progress?.length > 0 ? (
                    <div className="space-y-4">
                      {analytics.recent_progress.slice(0, 5).map((pr: any, i: number) => (
                        <div key={pr.id || i} className="flex gap-3 items-start pb-3 border-b border-slate-100 last:border-0 last:pb-0 min-w-0">
                          <div className="mt-1 w-2.5 h-2.5 bg-blue-600 rounded-full shrink-0"></div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-800 truncate">
                              Week {pr.week_number} Check-in Logged
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5 truncate">
                              {pr.total_completed_tasks} tasks finished • {pr.total_hours} hrs worked
                            </p>
                            <div className="text-xs font-semibold text-blue-600 mt-1">
                              {Math.round(pr.task_completion_pct)}% completion
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">No recent check-ins recorded yet.</p>
                  )}
                </div>

                {/* Quick Check-in Callout */}
                {goals.length > 0 && (
                  <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-5 sm:p-6 rounded-xl text-white shadow-md min-w-0">
                    <h3 className="font-bold text-base sm:text-lg mb-2">Ready for Weekly Check-in?</h3>
                    <p className="text-blue-100 text-xs sm:text-sm mb-4">
                      Record this week's hours and finished tasks to get fresh AI insights and roadmap suggestions.
                    </p>
                    <Link
                      href={`/goals/${goals[0].id}/checkin`}
                      className="bg-white text-blue-700 px-4 py-2.5 rounded-lg font-semibold text-sm hover:bg-blue-50 transition-colors inline-block w-full sm:w-auto text-center truncate"
                    >
                      Start Check-in for {goals[0].name}
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
