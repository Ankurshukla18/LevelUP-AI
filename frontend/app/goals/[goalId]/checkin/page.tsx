"use client";

import React, { useState } from "react";
import Navbar from "@/components/layout/navbar";
import { useParams, useRouter } from "next/navigation";
import { CheckCircle, Circle, Brain, Loader2 } from "lucide-react";

export default function CheckinPage() {
  const { goalId } = useParams();
  const router = useRouter();
  
  const [tasks, setTasks] = useState([
    { id: "t1", title: "Read documentation", isCompleted: false },
    { id: "t2", title: "Complete tutorials", isCompleted: false },
    { id: "t3", title: "Build small project", isCompleted: false }
  ]);
  
  const [formData, setFormData] = useState({
    hoursSpent: "",
    accomplishments: "",
    problemsFaced: "",
    difficultyLevel: "3",
    selfRating: "4",
    notes: ""
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const toggleTask = (id: string) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, isCompleted: !t.isCompleted } : t));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call for checkin submission
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSubmitted(true);
    }, 1000);
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysis({
        summary: "Solid progress this week despite some hurdles.",
        recommendations: ["Allocate more buffer time for bugs.", "Review specific topics you struggled with."]
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 md:p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">Weekly Check-in</h1>
          <p className="text-slate-500 mt-1">Reflect on your progress and update your goal status.</p>
        </div>

        {!isSubmitted ? (
          <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
            
            {/* Task Checklist */}
            <div>
              <h3 className="font-semibold text-slate-800 mb-3">This Week's Tasks</h3>
              <div className="space-y-2 border border-slate-100 p-4 rounded-lg bg-slate-50">
                {tasks.map(task => (
                  <div key={task.id} className="flex items-center gap-3 cursor-pointer" onClick={() => toggleTask(task.id)}>
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

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Hours Spent</label>
                <input
                  type="number"
                  required
                  min="0"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.hoursSpent}
                  onChange={e => setFormData({ ...formData, hoursSpent: e.target.value })}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Difficulty Level (1-5)</label>
                <select
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.difficultyLevel}
                  onChange={e => setFormData({ ...formData, difficultyLevel: e.target.value })}
                >
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Accomplishments</label>
              <textarea
                required
                rows={3}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                value={formData.accomplishments}
                onChange={e => setFormData({ ...formData, accomplishments: e.target.value })}
              ></textarea>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Problems Faced</label>
              <textarea
                rows={3}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                value={formData.problemsFaced}
                onChange={e => setFormData({ ...formData, problemsFaced: e.target.value })}
              ></textarea>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-70 flex items-center justify-center gap-2"
            >
              {isSubmitting ? <><Loader2 size={18} className="animate-spin" /> Submitting...</> : "Submit Check-in"}
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="bg-green-50 text-green-800 p-6 rounded-xl border border-green-200 text-center">
              <CheckCircle size={48} className="mx-auto mb-4 text-green-500" />
              <h2 className="text-2xl font-bold mb-2">Check-in Completed!</h2>
              <p>Your progress has been recorded successfully.</p>
            </div>

            {!analysis ? (
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm text-center">
                <Brain size={48} className="mx-auto mb-4 text-purple-500" />
                <h3 className="text-xl font-bold text-slate-800 mb-2">Get AI Feedback</h3>
                <p className="text-slate-500 mb-6">Let our AI analyze your week and provide actionable insights for the upcoming week.</p>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-70 flex items-center justify-center gap-2 mx-auto"
                >
                  {isAnalyzing ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : "Analyze My Week"}
                </button>
              </div>
            ) : (
              <div className="bg-gradient-to-br from-purple-50 to-white p-6 rounded-xl border border-purple-200 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-purple-800">
                  <Brain size={24} />
                  <h3 className="text-xl font-bold">AI Insights</h3>
                </div>
                <p className="text-slate-800 font-medium mb-4">{analysis.summary}</p>
                <div className="bg-white p-4 rounded-lg border border-purple-100">
                  <h4 className="text-sm font-bold text-purple-900 mb-2 uppercase tracking-wide">Recommendations</h4>
                  <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                    {analysis.recommendations.map((rec: string, i: number) => <li key={i}>{rec}</li>)}
                  </ul>
                </div>
                <div className="mt-6 text-center">
                  <button onClick={() => router.push(`/goals/${goalId}`)} className="text-blue-600 font-medium hover:underline">
                    Back to Goal Dashboard
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
