"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/layout/navbar";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { CheckCircle, Circle, Plus, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function GoalDetailPage() {
  const { goalId } = useParams();
  const [activeTab, setActiveTab] = useState("roadmap");
  
  // Dummy data representing API responses
  const goal = {
    id: goalId,
    name: "Learn Next.js App Router",
    category: "Coding",
    description: "Master the new Next.js app router and server components",
    status: "active",
    progress: 45
  };

  const roadmap = [
    {
      id: "w1", weekNumber: 1, title: "Fundamentals", 
      tasks: [
        { id: "t1", title: "Read docs", isCompleted: true },
        { id: "t2", title: "Build hello world", isCompleted: true }
      ]
    },
    {
      id: "w2", weekNumber: 2, title: "Data Fetching", 
      tasks: [
        { id: "t3", title: "Server components", isCompleted: false },
        { id: "t4", title: "Client components", isCompleted: false }
      ]
    }
  ];

  const checkins = [
    { id: "c1", weekId: "w1", date: "2023-10-01", hoursSpent: 5, completionPct: 100 },
    { id: "c2", weekId: "w2", date: "2023-10-08", hoursSpent: 3, completionPct: 50 }
  ];

  const analyticsData = [
    { week: "W1", progress: 20, plannedHours: 5, actualHours: 5 },
    { week: "W2", progress: 45, plannedHours: 6, actualHours: 3 }
  ];

  const aiInsights = [
    { id: "i1", date: "Oct 8", summary: "Great start! You hit your hours. Focus on practical application next.", recommendations: ["Try building a small project", "Review client/server boundaries"] }
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-6">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full font-medium">{goal.category}</span>
              <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-medium capitalize">{goal.status}</span>
            </div>
            <h1 className="text-3xl font-bold text-slate-900">{goal.name}</h1>
            <p className="text-slate-500 mt-1">{goal.description}</p>
          </div>
          <Link href={`/goals/${goalId}/checkin`} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700">
            Weekly Check-in
          </Link>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-200 mb-6 overflow-x-auto">
          {["roadmap", "check-ins", "analytics", "ai-insights"].map(tab => (
            <button
              key={tab}
              className={`px-4 py-3 font-medium text-sm whitespace-nowrap capitalize border-b-2 transition-colors ${
                activeTab === tab ? "border-blue-600 text-blue-600" : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.replace("-", " ")}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 min-h-[400px]">
          {activeTab === "roadmap" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-slate-800 mb-4">Roadmap & Tasks</h2>
              {roadmap.map(week => (
                <div key={week.id} className="border border-slate-100 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="font-semibold text-slate-800">Week {week.weekNumber}: {week.title}</h3>
                    <button className="text-sm text-blue-600 flex items-center gap-1 hover:underline">
                      <Plus size={14} /> Add Task
                    </button>
                  </div>
                  <div className="space-y-2">
                    {week.tasks.map(task => (
                      <div key={task.id} className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-md cursor-pointer">
                        {task.isCompleted ? (
                          <CheckCircle size={20} className="text-green-500" />
                        ) : (
                          <Circle size={20} className="text-slate-300" />
                        )}
                        <span className={task.isCompleted ? "line-through text-slate-400" : "text-slate-700"}>
                          {task.title}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "check-ins" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-800 mb-4">Check-in History</h2>
              {checkins.length === 0 ? (
                <p className="text-slate-500">No check-ins yet.</p>
              ) : (
                checkins.map(ci => (
                  <div key={ci.id} className="border border-slate-100 rounded-lg p-4 flex justify-between items-center">
                    <div>
                      <p className="font-semibold text-slate-800">Date: {ci.date}</p>
                      <p className="text-sm text-slate-500">Hours spent: {ci.hoursSpent}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-blue-600">{ci.completionPct}% Completed</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "analytics" && (
            <div className="space-y-8">
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-4">Cumulative Progress (%)</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={analyticsData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="week" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="progress" stroke="#3b82f6" fill="#eff6ff" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-4">Planned vs Actual Hours</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analyticsData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="week" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="plannedHours" name="Planned" fill="#cbd5e1" radius={[4,4,0,0]} />
                      <Bar dataKey="actualHours" name="Actual" fill="#3b82f6" radius={[4,4,0,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === "ai-insights" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-800 mb-4">AI Analysis & Insights</h2>
              {aiInsights.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-slate-500">
                  <AlertCircle size={48} className="text-slate-300 mb-4" />
                  <p>No AI insights yet. Complete a check-in to get personalized feedback.</p>
                </div>
              ) : (
                aiInsights.map(insight => (
                  <div key={insight.id} className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                    <p className="text-sm text-slate-500 mb-2">{insight.date}</p>
                    <p className="font-medium text-slate-800 mb-4">{insight.summary}</p>
                    <div>
                      <h4 className="text-sm font-bold text-slate-700 mb-2 uppercase tracking-wide">Recommendations</h4>
                      <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
                        {insight.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
                      </ul>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
