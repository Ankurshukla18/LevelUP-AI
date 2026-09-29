import React from "react";
import Navbar from "@/components/layout/navbar";
import { CheckCircle, Target, Activity, TrendingUp, Users } from "lucide-react";
import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-slate-900 text-white py-20 px-4">
          <div className="max-w-5xl mx-auto text-center space-y-6">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Master Your Life with AI
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto">
              LevelUp AI is your intelligent companion for setting, tracking, and achieving your most ambitious goals across all areas of life.
            </p>
          </div>
        </section>

        {/* Philosophy Section */}
        <section className="py-20 px-4">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Our Philosophy</h2>
              <p className="text-slate-600 max-w-2xl mx-auto text-lg">
                Success isn't an accident. It's the result of a systematic approach to continuous improvement.
              </p>
            </div>
            
            <div className="flex flex-col md:flex-row justify-between items-center space-y-8 md:space-y-0 md:space-x-4">
              {[
                { title: "Plan", icon: Target, desc: "Set clear, actionable goals." },
                { title: "Execute", icon: Activity, desc: "Take consistent daily action." },
                { title: "Measure", icon: CheckCircle, desc: "Track your real progress." },
                { title: "Reflect", icon: Users, desc: "Analyze what works and what doesn't." },
                { title: "Improve", icon: TrendingUp, desc: "Adapt and grow over time." }
              ].map((step, idx) => (
                <div key={idx} className="flex flex-col items-center text-center max-w-[150px]">
                  <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4">
                    <step.icon size={32} />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{step.title}</h3>
                  <p className="text-sm text-slate-600">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-blue-600 text-white py-20 px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to transform your life?</h2>
          <Link href="/dashboard" className="bg-white text-blue-600 px-8 py-3 rounded-full font-bold text-lg hover:bg-slate-100 transition-colors">
            Get Started Now
          </Link>
        </section>
      </main>

      <footer className="bg-slate-900 text-slate-400 py-8 text-center">
        <p>&copy; {new Date().getFullYear()} LevelUp AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
