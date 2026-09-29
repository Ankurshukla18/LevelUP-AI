"use client";

import React, { useState } from "react";
import Navbar from "@/components/layout/navbar";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { ArrowUpRight, ArrowDownRight, Calendar } from "lucide-react";

export default function MonthlyReviewPage() {
  const [month, setMonth] = useState("2023-10");

  const stats = [
    { label: "Total Hours", value: "42", change: "+15%", positive: true },
    { label: "Tasks Completed", value: "28", change: "+5%", positive: true },
    { label: "Avg Weekly Completion", value: "85%", change: "-2%", positive: false },
    { label: "Best Streak", value: "14 days", change: "+4 days", positive: true },
  ];

  const chartData = [
    { name: "Week 1", hours: 10, tasks: 6 },
    { name: "Week 2", hours: 12, tasks: 8 },
    { name: "Week 3", hours: 8, tasks: 5 },
    { name: "Week 4", hours: 12, tasks: 9 },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Monthly Review</h1>
            <p className="text-slate-500 mt-1">Analyze your performance over the past month.</p>
          </div>
          
          <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-3 py-2 shadow-sm">
            <Calendar size={18} className="text-slate-500" />
            <input 
              type="month" 
              className="outline-none text-slate-700 bg-transparent font-medium"
              value={month}
              onChange={e => setMonth(e.target.value)}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <p className="text-sm font-medium text-slate-500 mb-1">{stat.label}</p>
              <div className="flex items-end gap-3">
                <h3 className="text-3xl font-bold text-slate-900">{stat.value}</h3>
                <span className={`flex items-center text-sm font-medium ${stat.positive ? 'text-green-600' : 'text-red-600'} pb-1`}>
                  {stat.positive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chart */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-6">Activity by Week</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip cursor={{fill: '#f1f5f9'}} />
                  <Bar dataKey="hours" name="Hours" fill="#3b82f6" radius={[4,4,0,0]} />
                  <Bar dataKey="tasks" name="Tasks" fill="#8b5cf6" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Monthly Insights Summary */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 mb-6">AI Summary & Insights</h2>
            <div className="space-y-4">
              <p className="text-slate-700 leading-relaxed">
                You had a strong month overall, particularly in Weeks 2 and 4. Your consistency in Coding goals improved significantly, logging 25% more hours than last month.
              </p>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h4 className="font-bold text-blue-900 mb-2">Wins</h4>
                <ul className="list-disc pl-5 text-sm text-blue-800 space-y-1">
                  <li>Completed your "Learn Next.js" goal earlier than expected.</li>
                  <li>Maintained a 14-day streak, your best this quarter.</li>
                </ul>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-100">
                <h4 className="font-bold text-orange-900 mb-2">Areas for Improvement</h4>
                <ul className="list-disc pl-5 text-sm text-orange-800 space-y-1">
                  <li>Week 3 saw a dip in activity due to unexpected work tasks.</li>
                  <li>Fitness tracking consistency dropped towards the end of the month.</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
