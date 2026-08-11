'use client';

import React, { useState } from 'react';
import { SourceMetadata } from '../types';
import { ExternalLink, BookOpen, ChevronDown, ChevronUp, FileText, CheckCircle2 } from 'lucide-react';

interface SourceCitationsProps {
  sources: SourceMetadata[];
}

export const SourceCitations: React.FC<SourceCitationsProps> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedSnippet, setSelectedSnippet] = useState<SourceMetadata | null>(null);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border border-slate-800 bg-slate-900/60 rounded-xl overflow-hidden shadow-sm">
      {/* Citation Header Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-800/60 transition-colors"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-orange-400" />
          <span>Retrieved Sources ({sources.length})</span>
          <span className="bg-orange-500/10 text-orange-400 border border-orange-500/20 text-[10px] px-2 py-0.5 rounded-full font-mono">
            FAISS Top-K Verified
          </span>
        </div>
        <div className="flex items-center gap-1 text-slate-400">
          <span className="text-[11px]">{isOpen ? 'Hide Citations' : 'View Citations'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Accordion Content */}
      {isOpen && (
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {sources.map((src, idx) => (
              <div
                key={idx}
                className="p-3 bg-slate-900 border border-slate-800 rounded-lg hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-200 truncate">
                      <FileText className="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                      <span className="truncate">{src.document_name}</span>
                    </span>
                    <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono flex-shrink-0">
                      {(src.score * 100).toFixed(0)}% Match
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 mb-2">
                    <strong className="text-slate-300">Section:</strong> {src.section_name || 'General'}
                    {src.page_number && ` • Page ${src.page_number}`}
                  </p>

                  <p className="text-[11px] text-slate-400 line-clamp-2 italic bg-slate-950/60 p-2 rounded border border-slate-800/80 mb-2 font-mono">
                    "{src.chunk_snippet}"
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px]">
                  {src.source_url ? (
                    <a
                      href={src.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-orange-400 hover:text-orange-300 transition-colors font-medium"
                    >
                      <span>Open Official Doc</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-slate-500">Local Dataset</span>
                  )}
                  
                  <button
                    onClick={() => setSelectedSnippet(src)}
                    className="text-slate-400 hover:text-slate-200 text-[10px] underline"
                  >
                    View Chunk
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Snippet Detail Modal */}
      {selectedSnippet && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 max-w-xl w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-orange-400" />
                <span>{selectedSnippet.document_name}</span>
              </h3>
              <button
                onClick={() => setSelectedSnippet(null)}
                className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 bg-slate-800 rounded"
              >
                Close
              </button>
            </div>
            
            <div className="space-y-2 text-xs text-slate-300">
              <p><strong className="text-slate-400">Section:</strong> {selectedSnippet.section_name}</p>
              <p><strong className="text-slate-400">Relevance Score:</strong> {(selectedSnippet.score * 100).toFixed(1)}%</p>
              {selectedSnippet.source_url && (
                <p><strong className="text-slate-400">URL:</strong> <a href={selectedSnippet.source_url} target="_blank" rel="noreferrer" className="text-orange-400 underline">{selectedSnippet.source_url}</a></p>
              )}
            </div>

            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap">
              {selectedSnippet.chunk_snippet}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
