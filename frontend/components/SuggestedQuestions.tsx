'use client';

import React from 'react';
import { HelpCircle, Sparkles } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelectQuestion: (question: string) => void;
}

const SUGGESTIONS = [
  "How do I create a GitLab project?",
  "How does GitLab CI/CD work?",
  "What is a GitLab Runner and how to register it?",
  "How do I create a merge request?",
  "What authentication methods does GitLab API support?",
  "What is the difference between Issues and Merge Requests?",
  "How do I troubleshoot a failed CI/CD pipeline?"
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelectQuestion }) => {
  return (
    <div className="py-4">
      <div className="flex items-center gap-2 mb-3 text-xs font-semibold text-slate-400">
        <Sparkles className="w-3.5 h-3.5 text-orange-400" />
        <span>Suggested GitLab Documentation Topics:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(q)}
            className="text-left text-xs bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 px-3.5 py-2 rounded-xl transition-all shadow-sm flex items-center gap-2 group"
          >
            <HelpCircle className="w-3 h-3 text-orange-400 group-hover:scale-110 transition-transform flex-shrink-0" />
            <span className="line-clamp-1">{q}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
