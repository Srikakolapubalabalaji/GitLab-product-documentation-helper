'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage as ChatMessageType } from '../types';
import { SourceCitations } from './SourceCitations';
import { Bot, User, Copy, Check, AlertCircle, Sparkles } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`py-6 px-4 md:px-6 transition-colors ${isUser ? 'bg-slate-900/40' : 'bg-slate-950/80 border-y border-slate-800/40'}`}>
      <div className="max-w-4xl mx-auto flex gap-4">
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md ${
          isUser 
            ? 'bg-slate-800 text-slate-300 border border-slate-700' 
            : 'bg-gradient-to-br from-orange-500 to-red-600 text-white shadow-orange-500/20'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4.5 h-4.5" />}
        </div>

        {/* Message Content */}
        <div className="flex-1 overflow-hidden space-y-2">
          
          {/* Header row */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold text-slate-200">
              {isUser ? 'You' : 'GitLab Documentation Helper'}
            </span>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500">{message.timestamp}</span>
              {!isUser && (
                <button
                  onClick={handleCopy}
                  className="p-1 text-slate-400 hover:text-slate-200 transition-colors rounded hover:bg-slate-800"
                  title="Copy Answer"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              )}
            </div>
          </div>

          {/* Body Text */}
          {message.error ? (
            <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-red-300 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Query Execution Warning</p>
                <p className="mt-0.5 text-red-300/90">{message.error}</p>
              </div>
            </div>
          ) : (
            <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800 prose-code:text-orange-300">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, className, children, ...props }) {
                    return (
                      <code className="bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded text-orange-300 text-xs font-mono" {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre({ children }) {
                    return (
                      <div className="relative group my-3">
                        <pre className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl overflow-x-auto text-xs text-slate-200 font-mono">
                          {children}
                        </pre>
                      </div>
                    );
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Sources Accordion */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <SourceCitations sources={message.sources} />
          )}

        </div>
      </div>
    </div>
  );
};
