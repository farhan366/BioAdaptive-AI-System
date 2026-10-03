import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function SHAPChart({ shapData }) {
  const data = shapData || [
    { feature: 'SCL / EDA', contribution: 0.42 },
    { feature: 'Heart Rate', contribution: 0.35 },
    { feature: 'RMSSD (HRV)', contribution: -0.28 },
    { feature: 'DASS Score', contribution: 0.15 },
  ];

  return (
    <div className="bg-medical-card border border-medical-border rounded-xl p-5">
      <h3 className="font-semibold text-md mb-2 text-slate-200">XAI SHAP Feature Contributions</h3>
      <p className="text-xs text-slate-400 mb-4">Physiological driver importance for current stage prediction</p>
      
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <XAxis type="number" stroke="#64748b" />
            <YAxis dataKey="feature" type="category" stroke="#94a3b8" width={100} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#131B2E', borderColor: '#1E293B' }} />
            <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.contribution > 0 ? '#F43F5E' : '#38BDF8'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}