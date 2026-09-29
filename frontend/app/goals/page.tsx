"use client";

import React from "react";
import Navbar from "@/components/layout/navbar";
import Link from "next/link";
import { Plus, Target, Calendar, Activity } from "lucide-react";

export default function GoalsListPage() {
  const goals = [
    { id: "1", name: "Learn Next.js App Router", category: "Coding", progress: 45, status: "active", targetDate: "2023-12-31" },
    { id: "2", name: "Run a 5k", category: "Fitness", progress: 80, status: "active", targetDate: "2023-11-15" },
    { id: "3", name: "Read 12 Books", category: "Personal Growth", progress: 100, status: "completed", targetDate: "2023-10-01" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Your Goals</h1>
            <p className="text-slate-500 mt-1">Manage and track your active objectives.</p>
          </div>
          <Link href="/goals/new" className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2">
            <Plus size={18} /> New Goal
          </Link>
        </div>

        {goals.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center shadow-sm">
            <Target size={48} className="mx-auto text-slate-300 mb-4" />
            <h2 className="text-xl font-bold text-slate-700 mb-2">No goals yet</h2>
            <p className="text-slate-500 mb-6">Start your journey by setting your first goal.</p>
            <Link href="/goals/new" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 inline-flex items-center gap-2">
              <Plus size={18} /> Create Goal
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map(goal => (
              <Link key={goal.id} href={`/goals/${goal.id}`} className="block bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow group">
                <div className="flex justify-between items-start mb-4">
                  <span className="bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded-full font-medium">{goal.category}</span>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${goal.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    {goal.status}
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-slate-800 mb-4 group-hover:text-blue-600 transition-colors line-clamp-2">
                  {goal.name}
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-500 flex items-center gap-1"><Activity size={14} /> Progress</span>
                      <span className="font-medium text-slate-700">{goal.progress}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className={`h-2 rounded-full ${goal.status === 'completed' ? 'bg-green-500' : 'bg-blue-600'}`} style={{ width: `${goal.progress}%` }}></div>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-sm text-slate-500 gap-1 pt-2 border-t border-slate-100">
                    <Calendar size={14} />
                    <span>Target: {new Date(goal.targetDate).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
