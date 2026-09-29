"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/layout/navbar";
import { goalsService } from "@/services/goals";
import { roadmapService } from "@/services/roadmap";
import { Sparkles, Loader2, Target, Calendar, Clock, ArrowLeft } from "lucide-react";
import Link from "next/link";

const CATEGORIES = [
  { label: "Coding / Software", value: "coding" },
  { label: "Academics / Exams", value: "academics" },
  { label: "Fitness / Health", value: "fitness" },
  { label: "Career / Job Search", value: "career" },
  { label: "Personal Development", value: "personal_development" },
  { label: "Custom / Other", value: "other" }
];

export default function NewGoalPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const today = new Date().toISOString().split("T")[0];
  const targetDefault = new Date(Date.now() + 56 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];

  const [formData, setFormData] = useState({
    name: "Learn Python",
    category: "coding",
    description: "Learn Python fundamentals, data structures, and build 2 real-world projects",
    startDate: today,
    targetDate: targetDefault,
    currentLevel: "Beginner",
    targetOutcome: "Become comfortable with Python syntax and independently build 2 projects",
    availableHoursPerWeek: "8",
    priority: "high",
    motivation: "Transition into software engineering and data science"
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        name: formData.name.trim(),
        category: formData.category,
        description: formData.description.trim() || undefined,
        start_date: formData.startDate,
        target_date: formData.targetDate,
        current_level: formData.currentLevel.trim(),
        target_outcome: formData.targetOutcome.trim(),
        available_hours_per_week: parseFloat(formData.availableHoursPerWeek) || 8.0,
        priority: formData.priority,
        motivation: formData.motivation.trim() || undefined
      };

      const newGoal = await goalsService.create(payload);
      
      // Auto-generate AI roadmap for the new goal
      try {
        await roadmapService.generate(newGoal.id);
      } catch (rmErr) {
        console.warn("Roadmap generation warning:", rmErr);
      }

      router.push(`/goals/${newGoal.id}`);
    } catch (err: any) {
      console.error("Goal creation error:", err);
      setError(err.message || "Failed to create goal. Please review your entries.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 md:p-6 space-y-6">
        <div className="flex items-center gap-2">
          <Link href="/goals" className="text-slate-500 hover:text-slate-800 text-sm flex items-center gap-1">
            <ArrowLeft size={16} /> Back to Goals
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Create New Goal</h1>
          <p className="text-slate-500 mt-1">Define your objective and let LevelUp AI generate your customized roadmap.</p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label htmlFor="name" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Goal Name <span className="text-red-500">*</span>
              </label>
              <input
                id="name"
                required
                placeholder="e.g. Learn Python, Master DSA, Increase Bench Press"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                id="category"
                required
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                value={formData.category}
                onChange={handleChange}
              >
                {CATEGORIES.map(c => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Priority <span className="text-red-500">*</span>
              </label>
              <select
                id="priority"
                required
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                value={formData.priority}
                onChange={handleChange}
              >
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label htmlFor="description" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Description (Optional)
              </label>
              <textarea
                id="description"
                rows={2}
                placeholder="Briefly describe what you're working toward..."
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
                value={formData.description}
                onChange={handleChange}
              ></textarea>
            </div>

            <div>
              <label htmlFor="startDate" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Start Date <span className="text-red-500">*</span>
              </label>
              <input
                id="startDate"
                type="date"
                required
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={formData.startDate}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="targetDate" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Target Date <span className="text-red-500">*</span>
              </label>
              <input
                id="targetDate"
                type="date"
                required
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={formData.targetDate}
                onChange={handleChange}
              />
            </div>

            <div className="md:col-span-2">
              <label htmlFor="currentLevel" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Current Level <span className="text-red-500">*</span>
              </label>
              <input
                id="currentLevel"
                required
                placeholder="e.g. Beginner, Intermediate, 135 lbs bench, basic HTML"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={formData.currentLevel}
                onChange={handleChange}
              />
            </div>

            <div className="md:col-span-2">
              <label htmlFor="targetOutcome" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Target Outcome <span className="text-red-500">*</span>
              </label>
              <textarea
                id="targetOutcome"
                required
                rows={2}
                placeholder="e.g. Become comfortable with Python and build 2 projects independently"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
                value={formData.targetOutcome}
                onChange={handleChange}
              ></textarea>
            </div>

            <div>
              <label htmlFor="availableHoursPerWeek" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Available Capacity (Hours / Week) <span className="text-red-500">*</span>
              </label>
              <input
                id="availableHoursPerWeek"
                type="number"
                min="1"
                max="168"
                required
                placeholder="e.g. 8"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={formData.availableHoursPerWeek}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="motivation" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Personal Motivation (Optional)
              </label>
              <input
                id="motivation"
                placeholder="Why is achieving this goal important to you?"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={formData.motivation}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row justify-end gap-3">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-5 py-2.5 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-colors disabled:opacity-70 flex items-center justify-center gap-2 shadow-sm"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Generating Goal & AI Roadmap...
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Create Goal & Generate Roadmap
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
