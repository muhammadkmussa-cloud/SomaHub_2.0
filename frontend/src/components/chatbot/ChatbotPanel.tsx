import { useState, useRef, useEffect, useCallback } from 'react';
import {
  Bot,
  X,
  Trash2,
  ChevronDown,
  Sparkles,
  MessageSquare,
} from 'lucide-react';
import { cn } from '../ui';
import { ChatbotMessage } from './ChatbotMessage';
import { ChatbotInput } from './ChatbotInput';
import { chatbotApi } from '../../lib/chatbot';
import type { ChatMessage, Citation } from '../../lib/chatbot';

const SUGGESTED_QUESTIONS = [
  'How do I borrow a book?',
  'How do I search for books?',
  'How do I change my password?',
  'How do I purchase an ebook?',
  'Where do I find my purchases?',
  'What pages can I access?',
];

interface ChatbotPanelProps {
  onClose: () => void;
}

export function ChatbotPanel({ onClose }: ChatbotPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I\'m **SomaBot**, your AI assistant for SomaHub. I can help you navigate the platform, find books, explain borrowing procedures, and more. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = async (content: string) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setShowSuggestions(false);
    setIsLoading(true);

    const history = messages
      .filter((m) => m.id !== 'welcome')
      .map((m) => ({ role: m.role, content: m.content }));

    let citations: Citation[] = [];

    try {
      const fullAnswer = await chatbotApi.sendMessage(
        content,
        history,
        (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              last.content += token;
            }
            return [...updated];
          });
        },
        (cits) => {
          citations = cits;
        },
        (error) => {
          console.error('Chat error:', error);
        },
      );

      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          last.citations = citations;
        }
        return updated;
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          last.content = 'Sorry, I encountered an error. Please try again later.';
          last.error = true;
        }
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Hello! I\'m **SomaBot**, your AI assistant. How can I help you today?',
        timestamp: new Date(),
      },
    ]);
    setShowSuggestions(true);
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSend(question);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-obsidian-100 dark:border-obsidian-700 bg-gradient-to-r from-emerald-600 to-sapphire-600">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">SomaBot</h3>
            <p className="text-[10px] text-white/70">AI Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleClear}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            title="Clear chat"
          >
            <Trash2 size={15} />
          </button>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            title="Minimize"
          >
            <ChevronDown size={18} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-obsidian-50/50 dark:bg-obsidian-950/50"
      >
        {messages.map((msg) => (
          <ChatbotMessage
            key={msg.id}
            message={msg}
            isTyping={isLoading && msg.id === messages[messages.length - 1]?.id && !msg.content}
          />
        ))}

        {showSuggestions && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-2 text-xs text-obsidian-400">
              <Sparkles size={12} />
              <span>Suggested questions</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => handleSuggestedQuestion(q)}
                  className="text-xs px-3 py-1.5 rounded-full bg-white dark:bg-obsidian-800 border border-obsidian-100 dark:border-obsidian-700 text-obsidian-600 dark:text-obsidian-300 hover:border-emerald-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatbotInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
