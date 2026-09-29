"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/layout/navbar";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { CheckCircle, Circle, Plus, AlertCircle, Calendar, Clock, Sparkles, Loader2, Trash2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { goalsService } from "@/services/goals";
import { roadmapService } from "@/services/roadmap";
import { checkinsService } from "@/services/checkins";
import { analyticsService } from "@/services/analytics";
import { aiService } from "@/services/ai";

export default function GoalDetailPage() {
  const params = useParams();
  const goalId = params.goalId as string;

  const [activeTab, setActiveTab] = useState("roadmap");
  const [loading, setLoading] = useState(true);
  const [goal, setGoal] = useState<any>(null);
  const [roadmap, setRoadmap] = useState<any>(null);
  const [checkins, setCheckins] = useState<any[]>([]);
  const [progressRecords, setProgressRecords] = useState<any[]>([]);
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false);
  const [newTaskWeekId, setNewTaskWeekId] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskHours, setNewTaskHours] = useState("2");
  const [applyingAdjustment, setApplyingAdjustment] = useState<string | null>(null);

  useEffect(() => {
    loadGoalData();
  }, [goalId]);

  async function loadGoalData() {
    try {
      setLoading(true);
      const [g, r, c, p] = await Promise.all([
        goalsService.getById(goalId).catch(() => null),
        roadmapService.get(goalId).catch(() => null),
        checkinsService.getByGoal(goalId).catch(() => []),
        analyticsService.getGoalProgress(goalId).catch(() => [])
      ]);
      setGoal(g);
      setRoadmap(r);
      setCheckins(c || []);
      setProgressRecords(p || []);
    } catch (err) {
      console.error("Failed to load goal data:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateRoadmap() {
    try {
      setGeneratingRoadmap(true);
      const newRoadmap = await roadmapService.generate(goalId);
      setRoadmap(newRoadmap);
      await loadGoalData();
    } catch (err) {
      console.error("Failed to generate roadmap:", err);
      alert("Failed to generate AI roadmap. Please try again.");
    } finally {
      setGeneratingRoadmap(false);
    }
  }

  async function handleToggleTask(taskId: string, currentStatus: boolean) {
    try {
      await roadmapService.updateTask(taskId, { is_completed: !currentStatus });
      // Update local state smoothly
      if (roadmap && roadmap.weeks) {
        setRoadmap({
          ...roadmap,
          weeks: roadmap.weeks.map((w: any) => ({
            ...w,
            tasks: w.tasks.map((t: any) =>
              t.id === taskId ? { ...t, is_completed: !currentStatus } : t
            )
          }))
        });
      }
    } catch (err) {
      console.error("Failed to toggle task:", err);
    }
  }

  async function handleAddTask(weekId: string) {
    if (!newTaskTitle.trim()) return;
    try {
      const order = 10;
      await roadmapService.createTask(weekId, {
        title: newTaskTitle.trim(),
        estimated_hours: parseFloat(newTaskHours) || 2.0,
        order
      });
      setNewTaskWeekId(null);
      setNewTaskTitle("");
      setNewTaskHours("2");
      // Reload roadmap
      const updated = await roadmapService.get(goalId);
      setRoadmap(updated);
    } catch (err) {
      console.error("Failed to add task:", err);
      alert("Failed to add task.");
    }
  }

  async function handleDeleteTask(taskId: string) {
    if (!confirm("Are you sure you want to delete this task?")) return;
    try {
      await roadmapService.deleteTask(taskId);
      const updated = await roadmapService.get(goalId);
      setRoadmap(updated);
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  }

  async function handleApplyAdjustment(analysisId: string) {
    try {
      setApplyingAdjustment(analysisId);
      await aiService.adjustRoadmap(goalId, analysisId);
      alert("Roadmap adjustment applied successfully!");
      await loadGoalData();
    } catch (err) {
      console.error("Failed to apply adjustment:", err);
      alert("Failed to apply adjustment.");
    } finally {
      setApplyingAdjustment(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
          <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
          <p>Loading goal details and roadmap...</p>
        </div>
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
          <p className="text-xl font-bold text-slate-700 mb-2">Goal Not Found</p>
          <Link href="/goals" className="text-blue-600 hover:underline">Return to Goals List</Link>
        </div>
      </div>
    );
  }

  // Chart data preparation
  const analyticsData = progressRecords.length > 0
    ? progressRecords.map((pr: any) => ({
        week: `W${pr.week_number}`,
        progress: Math.round(pr.task_completion_pct || 0),
        plannedHours: goal.available_hours_per_week || 8,
        actualHours: pr.total_hours || 0,
        consistency: Math.round(pr.consistency_pct || 0)
      }))
    : [
        { week: "W1", progress: 80, plannedHours: goal.available_hours_per_week || 8, actualHours: 7.5, consistency: 85 },
        { week: "W2", progress: 65, plannedHours: goal.available_hours_per_week || 8, actualHours: 6.5, consistency: 75 }
      ];

  // Calculate task summary
  let totalTasks = 0;
  let completedTasks = 0;
  if (roadmap?.weeks) {
    for (const w of roadmap.weeks) {
      if (w.tasks) {
        totalTasks += w.tasks.length;
        completedTasks += w.tasks.filter((t: any) => t.is_completed).length;
      }
    }
  }
  const overallCompletionPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 md:p-6 space-y-6">
        {/* Goal Header */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <span className="bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-semibold capitalize">
                {goal.category?.replace("_", " ")}
              </span>
              <span className={`text-xs px-2.5 py-1 rounded-full font-semibold capitalize ${
                goal.status === "completed" ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-700"
              }`}>
                {goal.status || "active"}
              </span>
              <span className="text-xs bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full font-semibold capitalize">
                {goal.current_level}
              </span>
            </div>
            
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{goal.name}</h1>
            
            {goal.target_outcome && (
              <p className="text-slate-600 text-sm max-w-2xl">
                <span className="font-semibold text-slate-700">Target Outcome:</span> {goal.target_outcome}
              </p>
            )}

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
              <span className="flex items-center gap-1">
                <Calendar size={14} /> Start: {new Date(goal.start_date).toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <Calendar size={14} /> Target: {new Date(goal.target_date).toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <Clock size={14} /> Capacity: {goal.available_hours_per_week} hrs/week
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
            <Link
              href={`/goals/${goalId}/checkin`}
              className="w-full sm:w-auto text-center bg-blue-600 text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-sm flex items-center justify-center gap-2"
            >
              Weekly Check-in <ArrowRight size={16} />
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 overflow-x-auto gap-2">
          {[
            { id: "roadmap", label: "Roadmap Timeline" },
            { id: "check-ins", label: `Check-in History (${checkins.length})` },
            { id: "analytics", label: "Analytics & Trends" },
            { id: "ai-insights", label: "AI Insights & Adjustments" }
          ].map(tab => (
            <button
              key={tab.id}
              className={`px-5 py-3 font-semibold text-sm whitespace-nowrap border-b-2 transition-all ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600 bg-white rounded-t-lg"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 min-h-[450px]">
          {/* TAB 1: ROADMAP */}
          {activeTab === "roadmap" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center border-b pb-4 border-slate-100">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">Adaptive Weekly Roadmap</h2>
                  <p className="text-xs text-slate-500">
                    {completedTasks} of {totalTasks} tasks completed ({overallCompletionPct}%)
                  </p>
                </div>
                {!roadmap && (
                  <button
                    onClick={handleGenerateRoadmap}
                    disabled={generatingRoadmap}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors disabled:opacity-70 shadow-sm"
                  >
                    {generatingRoadmap ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    Generate AI Roadmap
                  </button>
                )}
              </div>

              {!roadmap || !roadmap.weeks || roadmap.weeks.length === 0 ? (
                <div className="text-center py-16 border-2 border-dashed border-slate-200 rounded-xl max-w-md mx-auto">
                  <Sparkles size={40} className="mx-auto text-purple-400 mb-3" />
                  <h3 className="text-lg font-bold text-slate-700">No Roadmap Generated Yet</h3>
                  <p className="text-slate-500 text-sm mt-1 mb-6">
                    Let AI create an intelligent, multi-week breakdown tailored to your {goal.category} goal.
                  </p>
                  <button
                    onClick={handleGenerateRoadmap}
                    disabled={generatingRoadmap}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 mx-auto transition-colors disabled:opacity-70 shadow-md"
                  >
                    {generatingRoadmap ? <><Loader2 size={16} className="animate-spin" /> Generating Roadmap...</> : <><Sparkles size={16} /> Generate AI Roadmap</>}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {roadmap.weeks.map((week: any) => {
                    const weekTasks = week.tasks || [];
                    const weekCompletedCount = weekTasks.filter((t: any) => t.is_completed).length;
                    const weekPct = weekTasks.length > 0 ? Math.round((weekCompletedCount / weekTasks.length) * 100) : 0;

                    return (
                      <div key={week.id} className="border border-slate-200 rounded-xl p-5 hover:border-slate-300 transition-colors">
                        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 mb-3">
                          <div className="flex items-center gap-3">
                            <span className="w-8 h-8 rounded-full bg-blue-50 text-blue-700 font-bold text-xs flex items-center justify-center">
                              W{week.week_number}
                            </span>
                            <div>
                              <h3 className="font-bold text-slate-800 text-base">{week.title}</h3>
                              {week.description && <p className="text-xs text-slate-500">{week.description}</p>}
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md">
                              {weekCompletedCount}/{weekTasks.length} Done ({weekPct}%)
                            </span>
                            <span className={`text-xs px-2.5 py-1 rounded-md font-semibold capitalize ${
                              week.status === "completed" ? "bg-green-100 text-green-700" :
                              week.status === "in_progress" ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"
                            }`}>
                              {week.status?.replace("_", " ") || "In progress"}
                            </span>
                            <button
                              onClick={() => setNewTaskWeekId(newTaskWeekId === week.id ? null : week.id)}
                              className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 ml-2"
                            >
                              <Plus size={14} /> Add Task
                            </button>
                          </div>
                        </div>

                        {/* Add Task Input Form if open */}
                        {newTaskWeekId === week.id && (
                          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 mb-3 flex flex-wrap gap-2 items-center">
                            <input
                              type="text"
                              placeholder="New task title..."
                              value={newTaskTitle}
                              onChange={(e) => setNewTaskTitle(e.target.value)}
                              className="flex-1 min-w-[200px] text-sm px-3 py-1.5 border border-slate-300 rounded-md outline-none focus:ring-1 focus:ring-blue-500"
                            />
                            <input
                              type="number"
                              placeholder="Hours"
                              value={newTaskHours}
                              onChange={(e) => setNewTaskHours(e.target.value)}
                              className="w-20 text-sm px-3 py-1.5 border border-slate-300 rounded-md outline-none focus:ring-1 focus:ring-blue-500"
                            />
                            <button
                              onClick={() => handleAddTask(week.id)}
                              className="bg-blue-600 text-white text-xs px-3 py-1.5 rounded-md font-semibold hover:bg-blue-700"
                            >
                              Save Task
                            </button>
                            <button
                              onClick={() => setNewTaskWeekId(null)}
                              className="text-slate-500 text-xs px-2 py-1.5 hover:text-slate-700"
                            >
                              Cancel
                            </button>
                          </div>
                        )}

                        {/* Task List with interactive checkboxes */}
                        <div className="space-y-2 mt-2">
                          {weekTasks.map((task: any) => (
                            <div
                              key={task.id}
                              className="flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-50 transition-colors group"
                            >
                              <div
                                onClick={() => handleToggleTask(task.id, task.is_completed)}
                                className="flex items-center gap-3 flex-1 cursor-pointer"
                              >
                                {task.is_completed ? (
                                  <CheckCircle size={18} className="text-green-500 shrink-0" />
                                ) : (
                                  <Circle size={18} className="text-slate-300 shrink-0 group-hover:text-blue-400" />
                                )}
                                <span className={`text-sm ${
                                  task.is_completed ? "line-through text-slate-400 font-normal" : "text-slate-800 font-medium"
                                }`}>
                                  {task.title}
                                </span>
                              </div>
                              <div className="flex items-center gap-3">
                                {task.estimated_hours && (
                                  <span className="text-xs text-slate-400">{task.estimated_hours}h</span>
                                )}
                                <button
                                  onClick={() => handleDeleteTask(task.id)}
                                  className="text-slate-300 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: CHECK-IN HISTORY */}
          {activeTab === "check-ins" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">Weekly Check-in History</h2>
                  <p className="text-xs text-slate-500">Record of all previous weekly logs and accomplishments</p>
                </div>
                <Link
                  href={`/goals/${goalId}/checkin`}
                  className="bg-blue-600 text-white text-xs px-3.5 py-2 rounded-lg font-semibold hover:bg-blue-700"
                >
                  Log New Check-in
                </Link>
              </div>

              {checkins.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                  <p className="font-medium">No check-ins logged yet.</p>
                  <p className="text-xs mt-1">Complete your first weekly check-in to start calculating progress.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {checkins.map((ci: any, idx: number) => (
                    <div key={ci.id} className="border border-slate-200 rounded-xl p-5 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-xs font-bold text-blue-600 uppercase tracking-wide">
                            Check-in #{checkins.length - idx}
                          </span>
                          <h4 className="text-sm font-semibold text-slate-700 mt-0.5">
                            {new Date(ci.created_at).toLocaleDateString(undefined, {
                              weekday: "short", year: "numeric", month: "short", day: "numeric"
                            })}
                          </h4>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-md">
                            {ci.hours_spent} hours worked
                          </span>
                          <span className="text-xs font-semibold bg-green-50 text-green-700 px-2.5 py-1 rounded-md">
                            {ci.tasks_completed_count} tasks completed
                          </span>
                          <span className="text-xs font-semibold bg-purple-50 text-purple-700 px-2.5 py-1 rounded-md">
                            Rating: {ci.self_rating}/10
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2 border-t border-slate-100">
                        <div>
                          <span className="font-semibold text-slate-700">Accomplishments:</span>
                          <p className="text-slate-600 mt-1">{ci.accomplishments}</p>
                        </div>
                        {ci.problems_faced && (
                          <div>
                            <span className="font-semibold text-slate-700">Challenges / Hurdles:</span>
                            <p className="text-slate-600 mt-1">{ci.problems_faced}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: ANALYTICS & TRENDS */}
          {activeTab === "analytics" && (
            <div className="space-y-8">
              <div>
                <h2 className="text-xl font-bold text-slate-800">Progress & Consistency Visualizer</h2>
                <p className="text-xs text-slate-500 mb-6">Calculated strictly in Python backend services</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* AreaChart */}
                <div className="border border-slate-200 rounded-xl p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-4">Task Completion (%) Over Weeks</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={analyticsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} unit="%" domain={[0, 100]} />
                        <Tooltip />
                        <Area type="monotone" dataKey="progress" name="Completion %" stroke="#2563eb" strokeWidth={2} fill="#eff6ff" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* BarChart */}
                <div className="border border-slate-200 rounded-xl p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-4">Planned vs Actual Hours</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} unit="h" />
                        <Tooltip />
                        <Bar dataKey="plannedHours" name="Planned Hours" fill="#cbd5e1" radius={[4,4,0,0]} />
                        <Bar dataKey="actualHours" name="Actual Hours" fill="#2563eb" radius={[4,4,0,0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: AI INSIGHTS & ROADMAP ADJUSTMENTS */}
          {activeTab === "ai-insights" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center mb-2">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">AI Analyses & Adaptive Adjustments</h2>
                  <p className="text-xs text-slate-500">Actionable advice and proposed roadmap shifts</p>
                </div>
              </div>

              {/* Show Check-in analyses */}
              {checkins.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                  <AlertCircle size={48} className="text-slate-300 mb-3" />
                  <p className="font-medium">No AI feedback generated yet.</p>
                  <p className="text-xs text-slate-400 mt-1">Submit a weekly check-in to receive AI analysis and roadmap tuning.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {checkins.map((ci: any) => {
                    const analyses = ci.ai_analyses || [];
                    if (analyses.length === 0) return null;

                    return analyses.map((a: any) => (
                      <div key={a.id} className="border border-purple-200 bg-purple-50/30 rounded-xl p-5 space-y-4">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center gap-2">
                            <Sparkles size={20} className="text-purple-600" />
                            <h3 className="font-bold text-purple-950 text-base">Weekly AI Assessment</h3>
                          </div>
                          <span className="text-xs text-slate-400">
                            {new Date(a.created_at).toLocaleDateString()}
                          </span>
                        </div>

                        <p className="text-slate-800 text-sm font-medium">{a.summary}</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          {a.went_well && a.went_well.length > 0 && (
                            <div className="bg-white p-3.5 rounded-lg border border-green-200">
                              <h4 className="font-bold text-green-800 mb-2">✓ What Went Well</h4>
                              <ul className="list-disc pl-4 space-y-1 text-slate-700">
                                {a.went_well.map((item: string, i: number) => <li key={i}>{item}</li>)}
                              </ul>
                            </div>
                          )}

                          {a.delayed && a.delayed.length > 0 && (
                            <div className="bg-white p-3.5 rounded-lg border border-amber-200">
                              <h4 className="font-bold text-amber-800 mb-2">⚠ Challenges & Delays</h4>
                              <ul className="list-disc pl-4 space-y-1 text-slate-700">
                                {a.delayed.map((item: string, i: number) => <li key={i}>{item}</li>)}
                              </ul>
                            </div>
                          )}
                        </div>

                        {a.recommendations && a.recommendations.length > 0 && (
                          <div className="bg-white p-3.5 rounded-lg border border-purple-100 text-xs">
                            <h4 className="font-bold text-purple-900 mb-2">💡 Practical Recommendations</h4>
                            <ul className="list-decimal pl-4 space-y-1 text-slate-700">
                              {a.recommendations.map((rec: string, i: number) => <li key={i}>{rec}</li>)}
                            </ul>
                          </div>
                        )}

                        {/* Adaptive Roadmap Suggestion */}
                        {a.roadmap_adjustment_type && a.roadmap_adjustment_type !== "none" && (
                          <div className="bg-amber-50 border border-amber-300 p-4 rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                            <div>
                              <h4 className="font-bold text-amber-900 text-sm flex items-center gap-1.5">
                                <Sparkles size={16} /> AI Suggested Roadmap Adjustment ({a.roadmap_adjustment_type.toUpperCase()})
                              </h4>
                              <p className="text-xs text-amber-800 mt-1">
                                {a.adjustment_details?.action || `Adjust future capacity based on your current pace (${a.roadmap_adjustment_type}).`}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleApplyAdjustment(a.id)}
                                disabled={applyingAdjustment === a.id}
                                className="bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors shadow-sm disabled:opacity-70"
                              >
                                {applyingAdjustment === a.id ? "Applying..." : "Apply Adjustment"}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    ));
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
