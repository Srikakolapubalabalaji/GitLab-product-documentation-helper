'use client';

import React from 'react';
import { HealthStatus } from '../types';
import { Database, Sparkles, FolderGit2, Activity, RefreshCw, BarChart2 } from 'lucide-react';

interface HeaderProps {
  health: HealthStatus | null;
  onOpenDocManager: () => void;
  onOpenEval: () => void;
  isReindexing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onOpenDocManager,
  onOpenEval,
  isReindexing
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white px-6 py-4 sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-500 via-red-500 to-purple-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
            <FolderGit2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-100">
                GitLab Product Documentation Helper
              </h1>
              <span className="bg-slate-800 text-orange-400 border border-orange-500/30 text-xs px-2 py-0.5 rounded-full font-semibold">
                RAG Pipeline
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Grounded AI Technical Assistant powered by Hugging Face, FAISS & Ollama
            </p>
          </div>
        </div>

        {/* Status Indicators & Action Buttons */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Health Badge */}
          <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg text-xs">
            <span className={`w-2 h-2 rounded-full ${health?.vector_index_ready ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
            <span className="text-slate-300 font-medium">
              {health ? `${health.vector_count} Document Vectors` : 'Connecting...'}
            </span>
          </div>

          {/* Model Badge */}
          <div className="hidden lg:flex items-center gap-1.5 bg-slate-800/50 border border-slate-700/40 px-3 py-1.5 rounded-lg text-xs text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>MiniLM + Ollama ({health?.ollama_model || 'llama3.2:1b'})</span>
          </div>

          {/* Document Management Button */}
          <button
            onClick={onOpenDocManager}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors shadow-sm"
          >
            <Database className="w-3.5 h-3.5 text-orange-400" />
            <span>Docs & Index</span>
          </button>

          {/* Benchmark Evaluation Button */}
          <button
            onClick={onOpenEval}
            className="flex items-center gap-2 bg-purple-900/40 hover:bg-purple-900/60 text-purple-200 border border-purple-700/50 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors shadow-sm"
          >
            <BarChart2 className="w-3.5 h-3.5 text-purple-400" />
            <span>RAG Evaluation</span>
          </button>
        </div>

      </div>
    </header>
  );
};
