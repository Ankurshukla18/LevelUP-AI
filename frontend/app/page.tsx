import Navbar from '@/components/layout/navbar';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Target, Activity, Brain, BarChart, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <main className="flex-1">
        <section className="py-20 md:py-32 bg-white text-center px-4">
          <div className="container mx-auto max-w-4xl">
            <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight mb-6">
              Plan. Track. Analyze. <span className="text-indigo-600">Improve.</span>
            </h1>
            <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
              LifeTrack AI is your intelligent workspace to define goals, break them down into AI-generated roadmaps, and track your weekly progress with actionable insights.
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/register">
                <Button size="lg" className="h-12 px-8 text-base">Get Started <ArrowRight className="ml-2 h-4 w-4" /></Button>
              </Link>
              <Link href="#features">
                <Button size="lg" variant="outline" className="h-12 px-8 text-base">Explore Features</Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="features" className="py-20 bg-slate-50">
          <div className="container mx-auto px-4 max-w-6xl">
            <h2 className="text-3xl font-bold text-center mb-16">How LifeTrack AI Helps</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {[
                { title: 'Smart Goals', desc: 'Define what you want to achieve with structured parameters.', icon: Target },
                { title: 'AI Roadmaps', desc: 'Get intelligent weekly breakdowns customized for your timeline.', icon: Brain },
                { title: 'Weekly Check-ins', desc: 'Log your progress, hours, and challenges every week.', icon: Activity },
                { title: 'Analytics', desc: 'Visualize your growth and adjust strategies based on data.', icon: BarChart },
              ].map((f, i) => (
                <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center">
                  <div className="h-12 w-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center mb-4">
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
                  <p className="text-slate-600">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
