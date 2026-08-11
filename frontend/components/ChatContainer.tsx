'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import { ChatMessage } from './ChatMessage';
import { SuggestedQuestions } from './SuggestedQuestions';
import { sendChatMessage } from '../lib/api';
import { Send, Trash2, Loader2, Sparkles, AlertCircle } from 'lucide-react';

export const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText?: string) => {
    const query = questionText || input.trim();
    if (!query || loading) return;

    setError(null);
    setInput('');

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendChatMessage(query, messages);
      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        retrieved_chunks: response.retrieved_chunks,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'An error occurred while contacting the RAG server.',
        error: err.message || 'Server connection failed',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 text-slate-100 overflow-hidden relative">
      
      {/* Top Bar / Clear Button */}
      <div className="bg-slate-900/60 border-b border-slate-800/80 px-6 py-2.5 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <Sparkles className="w-3.5 h-3.5 text-orange-400" />
          <span>Interactive RAG Assistant</span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/30 px-2.5 py-1 rounded-lg transition-colors border border-transparent hover:border-red-900/40"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Chat</span>
          </button>
        )}
      </div>

      {/* Main Scrollable Messages Body */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/20 pb-4">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto px-6 py-12 text-center space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-orange-500/20 to-red-500/20 border border-orange-500/30 text-orange-400 mx-auto flex items-center justify-center shadow-lg shadow-orange-500/10">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">Welcome to GitLab Documentation Helper</h2>
              <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto leading-relaxed">
                Ask any question regarding GitLab Projects, Repositories, Merge Requests, CI/CD Pipelines,
                Runners, API Authentication, or Issues. Answers are grounded in indexed documentation with full source citations.
              </p>
            </div>
            
            <SuggestedQuestions onSelectQuestion={handleSend} />
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="py-6 px-6 bg-slate-950/90 border-t border-slate-900">
            <div className="max-w-4xl mx-auto flex items-center gap-3 text-xs text-slate-400">
              <Loader2 className="w-4 h-4 text-orange-400 animate-spin" />
              <span>Querying FAISS vector index & generating grounded answer with Ollama...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 md:p-6 bg-slate-900/80 border-t border-slate-800/80">
        <div className="max-w-4xl mx-auto space-y-2">
          
          <div className="relative flex items-center bg-slate-950 border border-slate-800 rounded-2xl focus-within:border-orange-500/60 focus-within:ring-2 focus-within:ring-orange-500/20 transition-all shadow-inner">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about GitLab documentation (e.g. 'How do I configure a CI/CD pipeline?')..."
              rows={2}
              className="w-full bg-transparent px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none"
              disabled={loading}
            />

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className="absolute right-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-400 hover:to-red-500 text-white p-2.5 rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-orange-500/20"
              title="Send question"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
            <span>Press <kbd className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700 font-mono">Enter</kbd> to send, <kbd className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700 font-mono">Shift+Enter</kbd> for line break</span>
            <span>Grounded Answers Only • No Hallucinations</span>
          </div>

        </div>
      </div>

    </div>
  );
};
