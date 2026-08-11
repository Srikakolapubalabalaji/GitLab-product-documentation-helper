'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { ChatContainer } from '../components/ChatContainer';
import { DocumentManager } from '../components/DocumentManager';
import { EvaluationView } from '../components/EvaluationView';
import { HealthStatus } from '../types';
import { fetchHealth } from '../lib/api';

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isDocManagerOpen, setIsDocManagerOpen] = useState(false);
  const [isEvalOpen, setIsEvalOpen] = useState(false);

  const loadHealthStatus = async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      console.warn('Backend server not connected yet.');
      setHealth(null);
    }
  };

  useEffect(() => {
    loadHealthStatus();
    const interval = setInterval(loadHealthStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950">
      
      {/* Header */}
      <Header
        health={health}
        onOpenDocManager={() => setIsDocManagerOpen(true)}
        onOpenEval={() => setIsEvalOpen(true)}
        isReindexing={false}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 flex overflow-hidden relative">
        <ChatContainer />
      </main>

      {/* Modals & Drawers */}
      <DocumentManager
        isOpen={isDocManagerOpen}
        onClose={() => setIsDocManagerOpen(false)}
        onIndexUpdated={loadHealthStatus}
      />

      <EvaluationView
        isOpen={isEvalOpen}
        onClose={() => setIsEvalOpen(false)}
      />

    </div>
  );
}
