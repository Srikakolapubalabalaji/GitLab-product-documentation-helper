'use client';

import React, { useState, useEffect } from 'react';
import { DocumentItem, DocumentListResponse } from '../types';
import { fetchDocuments, triggerReindex, uploadDocument } from '../lib/api';
import { X, Upload, RefreshCw, FileText, CheckCircle2, AlertCircle, Database } from 'lucide-react';

interface DocumentManagerProps {
  isOpen: boolean;
  onClose: () => void;
  onIndexUpdated: () => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  isOpen,
  onClose,
  onIndexUpdated
}) => {
  const [docData, setDocData] = useState<DocumentListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await fetchDocuments();
      setDocData(data);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to load document index.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadDocs();
    }
  }, [isOpen]);

  const handleReindex = async () => {
    setReindexing(true);
    setStatusMessage(null);
    try {
      const res = await triggerReindex();
      setStatusMessage({ type: 'success', text: res.message });
      await loadDocs();
      onIndexUpdated();
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Reindexing failed.' });
    } finally {
      setReindexing(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setStatusMessage(null);
    try {
      const res = await uploadDocument(files[0]);
      setStatusMessage({ type: 'success', text: res.message });
      await loadDocs();
      onIndexUpdated();
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Upload failed.' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-orange-500/10 border border-orange-500/20 rounded-xl text-orange-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">GitLab Documentation Store</h2>
              <p className="text-xs text-slate-400">Manage indexed files and FAISS vector database</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status Toast */}
        {statusMessage && (
          <div className={`p-3.5 rounded-xl border text-xs flex items-center gap-2 ${
            statusMessage.type === 'success' 
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300' 
              : 'bg-red-950/40 border-red-800 text-red-300'
          }`}>
            {statusMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />}
            <span>{statusMessage.text}</span>
          </div>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
            <span className="text-2xl font-bold text-white font-mono">{docData?.total_documents ?? 0}</span>
            <p className="text-xs text-slate-400 mt-0.5">Documents Ingested</p>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
            <span className="text-2xl font-bold text-orange-400 font-mono">{docData?.total_chunks ?? 0}</span>
            <p className="text-xs text-slate-400 mt-0.5">FAISS Vectors</p>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="flex items-center justify-between gap-3 pt-2">
          {/* File Upload Button */}
          <label className="flex-1 cursor-pointer bg-orange-600 hover:bg-orange-500 text-white font-medium text-xs px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all shadow-md shadow-orange-600/20">
            <Upload className="w-4 h-4" />
            <span>{uploading ? 'Ingesting File...' : 'Upload New Document'}</span>
            <input
              type="file"
              accept=".md,.txt,.pdf,.html,.htm"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading || reindexing}
            />
          </label>

          {/* Re-index Button */}
          <button
            onClick={handleReindex}
            disabled={reindexing || uploading}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${reindexing ? 'animate-spin text-orange-400' : ''}`} />
            <span>{reindexing ? 'Reindexing...' : 'Reindex All Docs'}</span>
          </button>
        </div>

        {/* Document List Table */}
        <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60 max-h-60 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading document list...</div>
          ) : !docData || docData.documents.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">No document files indexed yet.</div>
          ) : (
            <div className="divide-y divide-slate-800/60 text-xs">
              {docData.documents.map((doc, idx) => (
                <div key={idx} className="p-3 flex items-center justify-between hover:bg-slate-900/60 transition-colors">
                  <div className="flex items-center gap-2.5 truncate">
                    <FileText className="w-4 h-4 text-orange-400 flex-shrink-0" />
                    <div className="truncate">
                      <p className="font-semibold text-slate-200 truncate">{doc.document_name}</p>
                      <p className="text-[10px] text-slate-400">
                        {doc.document_type.toUpperCase()} • {(doc.file_size_bytes / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="bg-slate-800 text-orange-300 px-2 py-0.5 rounded text-[10px] font-mono border border-slate-700">
                      {doc.chunk_count} Chunks
                    </span>
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
