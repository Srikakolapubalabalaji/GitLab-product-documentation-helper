'use client';

import React, { useState } from 'react';
import { EvalResponse } from '../types';
import { runEvaluation } from '../lib/api';
import { X, Play, BarChart2, CheckCircle2, XCircle, Clock, Award, ShieldCheck } from 'lucide-react';

interface EvaluationViewProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EvaluationView: React.FC<EvaluationViewProps> = ({ isOpen, onClose }) => {
  const [evalData, setEvalData] = useState<EvalResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunEval = async () => {
    setRunning(true);
    setError(null);
    try {
      const report = await runEvaluation();
      setEvalData(report);
    } catch (err: any) {
      setError(err.message || 'RAG evaluation execution failed.');
    } finally {
      setRunning(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-3xl w-full shadow-2xl space-y-5 max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">RAG System Evaluation Benchmark</h2>
              <p className="text-xs text-slate-400">Evaluate retrieval precision, groundedness, and response latency</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Action button */}
        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Runs 6 benchmark queries including out-of-domain guardrail checks.
          </p>
          <button
            onClick={handleRunEval}
            disabled={running}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium text-xs px-4 py-2 rounded-xl flex items-center gap-2 transition-all shadow-md disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${running ? 'animate-spin' : ''}`} />
            <span>{running ? 'Evaluating RAG Pipeline...' : 'Run Benchmark Suite'}</span>
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-950/40 border border-red-800 text-red-300 text-xs rounded-xl">
            {error}
          </div>
        )}

        {/* Results Overview Stats */}
        {evalData && (
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-2xl font-bold text-emerald-400 font-mono">{evalData.grounded_rate_pct}%</span>
              <p className="text-xs text-slate-400 mt-0.5">Grounded Rate</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-2xl font-bold text-purple-400 font-mono">{evalData.avg_latency_sec}s</span>
              <p className="text-xs text-slate-400 mt-0.5">Avg Latency</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-2xl font-bold text-white font-mono">{evalData.total_questions}</span>
              <p className="text-xs text-slate-400 mt-0.5">Benchmark Queries</p>
            </div>
          </div>
        )}

        {/* Detailed Items Table */}
        <div className="flex-1 overflow-y-auto border border-slate-800 rounded-xl bg-slate-950/60 p-2">
          {!evalData ? (
            <div className="p-12 text-center text-xs text-slate-500">
              Click <strong className="text-purple-300">Run Benchmark Suite</strong> to trigger evaluation metrics.
            </div>
          ) : (
            <div className="space-y-2 text-xs">
              {evalData.results.map((item, idx) => (
                <div key={idx} className="p-3 bg-slate-900 border border-slate-800/80 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {item.is_grounded ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      )}
                      <span className="font-semibold text-slate-200">{item.question}</span>
                    </div>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700 font-mono">
                      {item.category}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 bg-slate-950 p-2 rounded border border-slate-800/60 italic">
                    "{item.answer_snippet}"
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                    <span>Retrieved: {item.retrieved_chunks_count} chunks</span>
                    <span>Relevance: {(item.relevance_score * 100).toFixed(0)}%</span>
                    <span>Latency: {item.execution_time_sec}s</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
