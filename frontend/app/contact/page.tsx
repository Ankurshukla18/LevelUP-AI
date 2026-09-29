"use client";

import React from "react";
import Navbar from "@/components/layout/navbar";
import { Mail, ArrowRight } from "lucide-react";
import { CONTACT_EMAIL } from "@/lib/constants";

export default function ContactPage() {
  const contactEmail = process.env.NEXT_PUBLIC_CONTACT_EMAIL || CONTACT_EMAIL;
  const subject = encodeURIComponent("LevelUp AI Contact");
  const body = encodeURIComponent("Hello LevelUp AI team,\n\nI would like to contact you regarding:\n");
  const mailtoUrl = `mailto:${contactEmail}?subject=${subject}&body=${body}`;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 w-full max-w-lg text-center">
          <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-100">
            <Mail className="w-7 h-7" />
          </div>

          <h1 className="text-3xl font-bold mb-3 text-slate-900">Contact Us</h1>
          <p className="text-slate-600 text-sm mb-6 leading-relaxed">
            Have questions, feedback, or need help with your study roadmaps and goals?
            Reach out directly and our team will get back to you promptly.
          </p>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6 text-left">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Direct Email</p>
            <p className="text-sm font-medium text-slate-800 break-all select-all font-mono">
              {contactEmail}
            </p>
          </div>

          <a
            href={mailtoUrl}
            className="w-full inline-flex items-center justify-center bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm text-base group"
          >
            <span>Contact Us</span>
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-0.5 transition-transform" />
          </a>

          <p className="text-xs text-slate-400 mt-4">
            Clicking &quot;Contact Us&quot; will automatically open your device&apos;s default email application.
          </p>
        </div>
      </main>

      <footer className="bg-slate-900 text-slate-400 py-8 text-center mt-auto">
        <p>&copy; {new Date().getFullYear()} LevelUp AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
