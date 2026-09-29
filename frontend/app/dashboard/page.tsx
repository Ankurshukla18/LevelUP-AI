"use client";

import React, { useEffect, useState } from "react";
import Navbar from "@/components/layout/navbar";
import WeeklyChart from "@/components/dashboard/weekly-chart";
import { Activity, Target, TrendingUp, Zap, Plus, CheckCircle, BookOpen, Dumbbell, Code, Brain } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const [greeting, setGreeting] = useState("");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  const categories = [
    { title: "Academics", icon: BookOpen, progress: 75, streak: 5, color: "bg-blue-100 text-blue-600" },
    { title: "Fitness", icon: Dumbbell, progress: 60, streak: 3, color: "bg-green-100 text-green-600" },
    { title: "Coding", icon: Code, progress: 90, streak: 12, color: "bg-purple-100 text-purple-600" },
    { title: "Personal Growth", icon: Brain, progress: 40, streak: 2, color: "bg-orange-100 text-orange-600" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{greeting}, User!</h1>
            <p className="text-slate-500">Here's what's happening with your goals today.</p>
          </div>
          <div className="flex gap-3">
            <Link href="/goals/new" className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg hover:bg-slate-50 transition-colors shadow-sm">
              <Plus size={18} /> New Goal
            </Link>
            <Link href="/goals" className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
              <CheckCircle size={18} /> View All Goals
            </Link>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><Activity size={24} /></div>
            <div>
              <p className="text-sm font-medium text-slate-500">Overall Progress</p>
              <p className="text-2xl font-bold text-slate-900">68%</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3 bg-purple-50 text-purple-600 rounded-lg"><Target size={24} /></div>
            <div>
              <p className="text-sm font-medium text-slate-500">Active Goals</p>
              <p className="text-2xl font-bold text-slate-900">4</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3 bg-green-50 text-green-600 rounded-lg"><TrendingUp size={24} /></div>
            <div>
              <p className="text-sm font-medium text-slate-500">Weekly Completion</p>
              <p className="text-2xl font-bold text-slate-900">85%</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3 bg-orange-50 text-orange-600 rounded-lg"><Zap size={24} /></div>
            <div>
              <p className="text-sm font-medium text-slate-500">Current Streak</p>
              <p className="text-2xl font-bold text-slate-900">12 Days</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            {/* Weekly Progress Chart */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Weekly Progress</h2>
              <WeeklyChart />
            </div>

            {/* Categories */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Focus Areas</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {categories.map((cat, i) => (
                  <div key={i} className="p-4 border border-slate-100 rounded-lg flex flex-col gap-3">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-md ${cat.color}`}>
                          <cat.icon size={20} />
                        </div>
                        <span className="font-semibold text-slate-700">{cat.title}</span>
                      </div>
                      <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
                        <Zap size={12} className="text-orange-500" /> {cat.streak}
                      </span>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-500">Progress</span>
                        <span className="font-medium text-slate-700">{cat.progress}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${cat.progress}%` }}></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-4">Recent Activity</h2>
              <div className="space-y-4">
                {[
                  { text: "Completed 'React Tutorial'", time: "2 hours ago" },
                  { text: "Logged 1h Workout", time: "5 hours ago" },
                  { text: "Weekly check-in completed", time: "1 day ago" },
                  { text: "Started new goal 'Read 10 books'", time: "2 days ago" },
                ].map((act, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <div className="mt-1 w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">{act.text}</p>
                      <p className="text-xs text-slate-400">{act.time}</p>
                    </div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-6 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                View All Activity
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
