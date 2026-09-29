"use client";

import React from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { name: "Mon", score: 40 },
  { name: "Tue", score: 30 },
  { name: "Wed", score: 55 },
  { name: "Thu", score: 45 },
  { name: "Fri", score: 70 },
  { name: "Sat", score: 65 },
  { name: "Sun", score: 85 },
];

export default function WeeklyChart() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
          />
          <Area type="monotone" dataKey="score" stroke="#3b82f6" fill="#eff6ff" strokeWidth={3} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
