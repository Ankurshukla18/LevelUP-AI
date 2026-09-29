"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/layout/navbar";
import { useParams, useRouter } from "next/navigation";
import { CheckCircle, Circle, Brain, Loader2, Sparkles, ArrowRight, Check } from "lucide-react";
import { goalsService } from "@/services/goals";
import { roadmapService } from "@/services/roadmap";
import { checkinsService } from "@/services/checkins";
import { aiService } from "@/services/ai";

export default function CheckinPage() {
  const params = useParams();
  const goalId = params.goalId as string;
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [goal, setGoal] = useState<any>(null);
  const [roadmap, setRoadmap] = useState<any>(null);
  const [selectedWeek, setSelectedWeek] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);

  const [formData, setFormData] = useState({
    hoursSpent: "7",
    accomplishments: "",
    problemsFaced: "",
    difficultyLevel: "moderate",
    selfRating: "7",
    notes: ""
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedCheckin, setSubmittedCheckin] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [isAdjusting, setIsAdjusting] = useState(false);
  const [adjustmentApplied, setAdjustmentApplied] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [g, r] = await Promise.all([
          goalsService.getById(goalId).catch(() => null),
          roadmapService.get(goalId).catch(() => null)
        ]);
        setGoal(g);
        setRoadmap(r);

        if (r && r.weeks && r.weeks.length > 0) {
          // Select the first in_progress or not_started week, or the first week
          const currentWeek =
            r.weeks.find((w: any) => w.status === "in_progress") ||
            r.weeks.find((w: any) => w.status === "not_started") ||
            r.weeks[0];
          setSelectedWeek(currentWeek);
          setTasks(currentWeek.tasks ? currentWeek.tasks.map((t: any) => ({ ...t })) : []);
        }
      } catch (err) {
        console.error("Failed to load checkin context:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [goalId]);

  const handleWeekChange = (weekId: string) => {
    if (!roadmap?.weeks) return;
    const w = roadmap.weeks.find((item: any) => item.id === weekId);
    if (w) {
      setSelectedWeek(w);
      setTasks(w.tasks ? w.tasks.map((t: any) => ({ ...t })) : []);
    }
  };

  const toggleTask = (taskId: string) => {
    setTasks(tasks.map(t => t.id === taskId ? { ...t, is_completed: !t.is_completed } : t));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWeek) {
      setErrorMessage("No roadmap week selected.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const payload = {
        week_id: selectedWeek.id,
        hours_spent: parseFloat(formData.hoursSpent) || 0,
        accomplishments: formData.accomplishments.trim() || "Worked on weekly tasks.",
        problems_faced: formData.problemsFaced.trim() || undefined,
        difficulty_level: formData.difficultyLevel,
        self_rating: parseInt(formData.selfRating, 10) || 7,
        notes: formData.notes.trim() || undefined,
        tasks: tasks.map(t => ({
          task_id: t.id,
          is_completed: !!t.is_completed,
          notes: ""
        }))
      };

      const res = await checkinsService.create(goalId, payload);
      setSubmittedCheckin(res);
    } catch (err: any) {
      console.error("Check-in submission failed:", err);
      setErrorMessage(err.message || "Failed to submit check-in. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAnalyze = async () => {
    if (!submittedCheckin) return;
    setIsAnalyzing(true);
    try {
      const res = await aiService.analyzeWeek(goalId, submittedCheckin.id);
      setAnalysis(res);
    } catch (err: any) {
      console.error("AI Analysis failed:", err);
      alert("Failed to analyze week. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleApplyAdjustment = async () => {
    if (!analysis) return;
    setIsAdjusting(true);
    try {
      await aiService.adjustRoadmap(goalId, analysis.id);
      setAdjustmentApplied(true);
    } catch (err: any) {
      console.error("Failed to apply adjustment:", err);
      alert("Failed to apply adjustment.");
    } finally {
      setIsAdjusting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
          <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
          <p>Loading weekly check-in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Weekly Check-in</h1>
          <p className="text-slate-500 mt-1">
            Goal: <span className="font-semibold text-slate-800">{goal?.name || "Your Goal"}</span>
          </p>
        </div>

        {errorMessage && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-medium">
            {errorMessage}
          </div>
        )}

        {!submittedCheckin ? (
          <form onSubmit={handleSubmit} className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
            {/* Week Selector */}
            {roadmap?.weeks && roadmap.weeks.length > 0 && (
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Check-in for Week</label>
                <select
                  value={selectedWeek?.id}
                  onChange={(e) => handleWeekChange(e.target.value)}
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium text-slate-800 bg-white"
                >
                  {roadmap.weeks.map((w: any) => (
                    <option key={w.id} value={w.id}>
                      Week {w.week_number}: {w.title} ({w.status?.replace("_", " ")})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Task Checklist from Roadmap */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-slate-800 text-sm">Planned Tasks for this Week</h3>
                <span className="text-xs text-slate-500">Check off completed items</span>
              </div>
              
              {tasks.length === 0 ? (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 text-center">
                  No predefined tasks in this week's plan.
                </div>
              ) : (
                <div className="space-y-2 border border-slate-200 p-4 rounded-xl bg-slate-50/50">
                  {tasks.map(task => (
                    <div
                      key={task.id}
                      onClick={() => toggleTask(task.id)}
                      className="flex items-center gap-3 p-2 bg-white rounded-lg border border-slate-100 hover:border-slate-300 cursor-pointer transition-all"
                    >
                      {task.is_completed ? (
                        <CheckCircle size={20} className="text-green-500 shrink-0" />
                      ) : (
                        <Circle size={20} className="text-slate-300 shrink-0" />
                      )}
                      <span className={`text-sm flex-1 ${
                        task.is_completed ? "line-through text-slate-400 font-normal" : "text-slate-800 font-medium"
                      }`}>
                        {task.title}
                      </span>
                      {task.estimated_hours && (
                        <span className="text-xs text-slate-400">{task.estimated_hours}h</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Hours Spent this Week</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="168"
                  required
                  placeholder="e.g. 7"
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  value={formData.hoursSpent}
                  onChange={e => setFormData({ ...formData, hoursSpent: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Difficulty Level</label>
                <select
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                  value={formData.difficultyLevel}
                  onChange={e => setFormData({ ...formData, difficultyLevel: e.target.value })}
                >
                  <option value="easy">Easy — Smooth sailing</option>
                  <option value="moderate">Moderate — As expected</option>
                  <option value="hard">Hard — Challenging</option>
                  <option value="very_hard">Very Hard — Struggling</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-sm font-semibold text-slate-700">Self-Rated Understanding (1–10)</label>
                <span className="text-sm font-bold text-blue-600">{formData.selfRating} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={formData.selfRating}
                onChange={e => setFormData({ ...formData, selfRating: e.target.value })}
                className="w-full accent-blue-600 cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">What did you accomplish?</label>
              <textarea
                required
                rows={3}
                placeholder="Key concepts learned, practice problems solved, workout sets finished..."
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
                value={formData.accomplishments}
                onChange={e => setFormData({ ...formData, accomplishments: e.target.value })}
              ></textarea>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">What challenges or delays occurred?</label>
              <textarea
                rows={2}
                placeholder="e.g. Loops were difficult, time constraints, tricky bugs..."
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
                value={formData.problemsFaced}
                onChange={e => setFormData({ ...formData, problemsFaced: e.target.value })}
              ></textarea>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:opacity-70 flex items-center justify-center gap-2 shadow-sm"
            >
              {isSubmitting ? <><Loader2 size={18} className="animate-spin" /> Submitting & Calculating Progress...</> : "Submit Weekly Check-in"}
            </button>
          </form>
        ) : (
          /* Check-in Submitted State */
          <div className="space-y-6">
            <div className="bg-green-50 text-green-900 p-6 rounded-2xl border border-green-200 text-center">
              <CheckCircle size={44} className="mx-auto mb-3 text-green-600" />
              <h2 className="text-2xl font-bold">Weekly Check-in Recorded!</h2>
              <p className="text-green-700 text-sm mt-1">
                Completed {submittedCheckin.tasks_completed_count} tasks • Logged {submittedCheckin.hours_spent} hours
              </p>
              <p className="text-xs text-green-600 mt-2">
                Progress metrics were automatically calculated and saved to your history.
              </p>
            </div>

            {!analysis ? (
              <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm text-center space-y-4">
                <Brain size={48} className="mx-auto text-purple-600" />
                <h3 className="text-2xl font-bold text-slate-900">Get AI Weekly Analysis</h3>
                <p className="text-slate-500 text-sm max-w-md mx-auto">
                  Let AI interpret your accomplishments, identify why delays happened, recommend fixes for next week, and suggest roadmap adjustments.
                </p>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-xl font-semibold text-sm transition-colors disabled:opacity-70 flex items-center justify-center gap-2 mx-auto shadow-md"
                >
                  {isAnalyzing ? <><Loader2 size={18} className="animate-spin" /> Analyzing Your Week...</> : <><Sparkles size={18} /> Analyze My Week</>}
                </button>
              </div>
            ) : (
              /* Structured AI Analysis Card */
              <div className="bg-white p-6 md:p-8 rounded-2xl border border-purple-200 shadow-sm space-y-6">
                <div className="flex items-center gap-2.5 pb-4 border-b border-purple-100">
                  <div className="p-2 bg-purple-100 text-purple-700 rounded-lg">
                    <Sparkles size={20} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-purple-950">AI Weekly Analysis & Roadmap Feedback</h3>
                    <p className="text-xs text-purple-700">Tailored to your submitted performance and challenges</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-slate-700 text-xs uppercase tracking-wider mb-1">Weekly Summary</h4>
                  <p className="text-slate-800 text-sm font-medium leading-relaxed">{analysis.summary}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  {analysis.went_well && analysis.went_well.length > 0 && (
                    <div className="bg-green-50/60 p-4 rounded-xl border border-green-200">
                      <h4 className="font-bold text-green-900 mb-2">✓ What Went Well</h4>
                      <ul className="list-disc pl-4 space-y-1 text-green-800">
                        {analysis.went_well.map((item: string, i: number) => <li key={i}>{item}</li>)}
                      </ul>
                    </div>
                  )}

                  {analysis.delayed && analysis.delayed.length > 0 && (
                    <div className="bg-amber-50/60 p-4 rounded-xl border border-amber-200">
                      <h4 className="font-bold text-amber-900 mb-2">⚠ What Was Delayed</h4>
                      <ul className="list-disc pl-4 space-y-1 text-amber-800">
                        {analysis.delayed.map((item: string, i: number) => <li key={i}>{item}</li>)}
                      </ul>
                    </div>
                  )}
                </div>

                {analysis.recommendations && analysis.recommendations.length > 0 && (
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
                    <h4 className="font-bold text-slate-900 mb-2">💡 Recommendations for Next Week</h4>
                    <ul className="list-decimal pl-4 space-y-1 text-slate-700">
                      {analysis.recommendations.map((rec: string, i: number) => <li key={i}>{rec}</li>)}
                    </ul>
                  </div>
                )}

                {/* Adaptive Roadmap Adjustment Section */}
                {analysis.roadmap_adjustment_type && analysis.roadmap_adjustment_type !== "none" ? (
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-300 p-5 rounded-2xl space-y-3">
                    <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                      <Sparkles size={18} />
                      AI Suggested Roadmap Adjustment ({analysis.roadmap_adjustment_type.toUpperCase()})
                    </div>
                    <p className="text-xs text-amber-800 leading-relaxed">
                      Based on your pace and hurdles, AI suggests updating future weeks:{" "}
                      <span className="font-semibold">
                        {analysis.adjustment_details?.action || "Rebalance upcoming tasks to keep progress achievable without burnout."}
                      </span>
                    </p>

                    {adjustmentApplied ? (
                      <div className="flex items-center gap-2 text-green-700 font-semibold text-xs pt-1">
                        <Check size={16} /> Roadmap Adjustment Applied Successfully!
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2 pt-2">
                        <button
                          onClick={handleApplyAdjustment}
                          disabled={isAdjusting}
                          className="bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-colors disabled:opacity-70 shadow-sm"
                        >
                          {isAdjusting ? "Applying..." : "Apply Adjustment"}
                        </button>
                        <button
                          onClick={() => router.push(`/goals/${goalId}`)}
                          className="bg-white border border-amber-200 text-amber-800 text-xs font-semibold px-4 py-2 rounded-xl hover:bg-amber-100 transition-colors"
                        >
                          Keep Original Roadmap
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
                    <span className="font-semibold">Roadmap Status:</span> On track! No roadmap adjustments needed at this time.
                  </div>
                )}

                <div className="pt-4 flex justify-end">
                  <button
                    onClick={() => router.push(`/goals/${goalId}`)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-colors shadow-sm flex items-center gap-2"
                  >
                    Return to Goal Overview <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
