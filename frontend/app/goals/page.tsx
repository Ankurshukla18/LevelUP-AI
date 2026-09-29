"use client";

import React, { useEffect, useState } from "react";
import Navbar from "@/components/layout/navbar";
import Link from "next/link";
import { Plus, Target, Calendar, Activity, Clock, Loader2 } from "lucide-react";
import { goalsService } from "@/services/goals";
import { useAuth } from "@/contexts/auth-context";

export default function GoalsListPage() {
  const { user } = useAuth();
  const [goals, setGoals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadGoals() {
      try {
        setLoading(true);
        const data = await goalsService.getAll();
        setGoals(data || []);
      } catch (err: any) {
        console.error("Failed to load goals:", err);
        setError("Failed to load your goals. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    loadGoals();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Your Goals</h1>
            <p className="text-slate-500 mt-1">Manage and track your active personal and academic roadmaps.</p>
          </div>
          <Link href="/goals/new" className="bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-sm">
            <Plus size={18} /> Create New Goal
          </Link>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 size={36} className="animate-spin text-blue-600 mb-3" />
            <p>Loading your goals...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center">
            {error}
          </div>
        ) : goals.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center shadow-sm max-w-lg mx-auto">
            <Target size={48} className="mx-auto text-slate-300 mb-4" />
            <h2 className="text-xl font-bold text-slate-700 mb-2">No goals yet</h2>
            <p className="text-slate-500 mb-6">Start your journey by setting your first learning, fitness, or academic goal.</p>
            <Link href="/goals/new" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 inline-flex items-center gap-2">
              <Plus size={18} /> Create Goal
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map((goal) => {
              const categoryName = goal.category ? goal.category.replace("_", " ") : "Custom";
              const targetDateFormatted = goal.target_date ? new Date(goal.target_date).toLocaleDateString() : "No deadline";
              const progressPct = goal.progress || (goal.status === "completed" ? 100 : 0);

              return (
                <Link
                  key={goal.id}
                  href={`/goals/${goal.id}`}
                  className="block bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <span className="bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-semibold capitalize">
                        {categoryName}
                      </span>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-semibold capitalize ${
                        goal.status === "completed"
                          ? "bg-green-100 text-green-700"
                          : "bg-slate-100 text-slate-700"
                      }`}>
                        {goal.status || "active"}
                      </span>
                    </div>
                    
                    <h3 className="text-xl font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors line-clamp-1">
                      {goal.name}
                    </h3>
                    
                    {goal.description && (
                      <p className="text-sm text-slate-500 mb-4 line-clamp-2">
                        {goal.description}
                      </p>
                    )}
                  </div>
                  
                  <div className="space-y-4 pt-4 border-t border-slate-100 mt-2">
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock size={14} /> {goal.available_hours_per_week || 5} hrs/wk
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar size={14} /> Due: {targetDateFormatted}
                      </span>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-500 flex items-center gap-1">
                          <Activity size={12} /> Target
                        </span>
                        <span className="font-semibold text-slate-700">{goal.target_outcome || "In progress"}</span>
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
