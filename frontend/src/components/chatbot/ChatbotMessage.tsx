import { useState } from 'react';
import { Bot, User, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { cn } from '../ui';
import type { ChatMessage } from '../../lib/chatbot';

interface ChatbotMessageProps {
  message: ChatMessage;
  isTyping?: boolean;
}

function renderInlineMarkdown(text: string) {
  const regex = /(\*\*.*?\*\*|`.*?`)/g;
  const parts = text.split(regex);

  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={index} className="font-semibold text-obsidian-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code
          key={index}
          className="bg-black/10 dark:bg-white/10 px-1 py-0.5 rounded text-xs font-mono text-emerald-600 dark:text-emerald-400"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

function SimpleMarkdown({ content }: { content: string }) {
  const lines = content.split('\n');
  return (
    <div className="space-y-1.5">
      {lines.map((line, i) => {
        if (!line.trim()) return <br key={i} />;

        if (/^#{1,6}\s/.test(line)) {
          const level = line.match(/^#+/)?.[0].length || 1;
          const text = line.replace(/^#+\s/, '');
          const sizes = { 1: 'text-lg', 2: 'text-base', 3: 'text-sm' };
          return (
            <p key={i} className={cn('font-semibold', sizes[level as keyof typeof sizes] || 'text-sm')}>
              {renderInlineMarkdown(text)}
            </p>
          );
        }

        if (/^- /.test(line)) {
          const text = line.replace(/^- /, '');
          return (
            <div key={i} className="flex items-start gap-1.5 pl-3 text-sm leading-relaxed">
              <span className="select-none text-obsidian-400">•</span>
              <span>{renderInlineMarkdown(text)}</span>
            </div>
          );
        }

        if (/^\d+\. /.test(line)) {
          const match = line.match(/^(\d+)\.\s(.*)/);
          if (match) {
            const num = match[1];
            const text = match[2];
            return (
              <div key={i} className="flex items-start gap-1.5 pl-3 text-sm leading-relaxed">
                <span className="select-none text-obsidian-400">{num}.</span>
                <span>{renderInlineMarkdown(text)}</span>
              </div>
            );
          }
        }

        if (/^\*\*.+\*\*$/.test(line.trim())) {
          return (
            <p key={i} className="font-semibold text-sm">
              {renderInlineMarkdown(line.trim())}
            </p>
          );
        }

        return (
          <p key={i} className="text-sm leading-relaxed text-obsidian-700 dark:text-obsidian-200">
            {renderInlineMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}

export function ChatbotMessage({ message, isTyping }: ChatbotMessageProps) {
  const [showCitations, setShowCitations] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-emerald-600' : 'bg-sapphire-600',
        )}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-white" />
        )}
      </div>

      <div className={cn('flex-1 min-w-0 max-w-[85%]', isUser ? 'items-end' : 'items-start')}>
        <div
          className={cn(
            'rounded-2xl px-4 py-3',
            isUser
              ? 'bg-emerald-600 text-white rounded-tr-md'
              : 'bg-white dark:bg-obsidian-800 border border-obsidian-100 dark:border-obsidian-700 rounded-tl-md',
          )}
        >
          {isUser ? (
            <p className="text-sm">{message.content}</p>
          ) : message.content ? (
            <SimpleMarkdown content={message.content} />
          ) : isTyping ? (
            <div className="flex gap-1 py-1">
              <span className="w-2 h-2 bg-obsidian-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-obsidian-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-obsidian-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          ) : null}

          {message.error && (
            <div className="flex items-center gap-1.5 mt-1 text-xs text-red-500">
              <AlertCircle size={12} />
              <span>Failed to get response</span>
            </div>
          )}
        </div>

        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-1">
            <button
              type="button"
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center gap-1 text-xs text-obsidian-400 hover:text-obsidian-600 dark:hover:text-obsidian-300 transition-colors"
            >
              {showCitations ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {message.citations.length} source{message.citations.length > 1 ? 's' : ''}
            </button>
            {showCitations && (
              <div className="mt-1 space-y-1">
                {message.citations.map((citation, i) => (
                  <div
                    key={i}
                    className="text-xs text-obsidian-500 dark:text-obsidian-400 bg-obsidian-50 dark:bg-obsidian-800/50 rounded-lg px-2.5 py-1.5 border border-obsidian-100 dark:border-obsidian-700"
                  >
                    <span className="font-medium text-obsidian-700 dark:text-obsidian-300">
                      {citation.source}
                    </span>
                    {citation.type && (
                      <span className="ml-1.5 text-obsidian-400">({citation.type})</span>
                    )}
                    <p className="mt-0.5 text-obsidian-400 dark:text-obsidian-500 line-clamp-2">
                      {citation.text_snippet}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
