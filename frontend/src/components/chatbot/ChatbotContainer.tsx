import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { MessageCircle, X, Bot } from 'lucide-react';
import { ChatbotPanel } from './ChatbotPanel';
import { cn } from '../ui';

export function ChatbotContainer() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  const toggleOpen = () => {
    setIsOpen((v) => !v);
    setIsMinimized(false);
  };

  const handleClose = () => {
    if (isMinimized) {
      setIsMinimized(false);
    } else {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        toggleOpen();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (location.pathname.includes('/read/')) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] flex flex-col items-end gap-3">
      {isOpen && (
        <div
          ref={panelRef}
          className={cn(
            'w-[380px] max-w-[calc(100vw-2rem)] h-[600px] max-h-[calc(100vh-6rem)]',
            'bg-white dark:bg-obsidian-900 rounded-2xl shadow-2xl border border-obsidian-100 dark:border-obsidian-700',
            'flex flex-col overflow-hidden',
            'animate-scale-in origin-bottom-right',
          )}
        >
          <ChatbotPanel onClose={handleClose} />
        </div>
      )}

      {/* Floating button */}
      <button
        type="button"
        onClick={toggleOpen}
        className={cn(
          'relative w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200',
          'bg-gradient-to-r from-emerald-600 to-sapphire-600 text-white',
          'hover:shadow-emerald-glow hover:scale-105 active:scale-95',
          isOpen && 'rotate-45',
        )}
        aria-label="Toggle AI Assistant"
      >
        {isOpen ? (
          <X size={24} />
        ) : (
          <>
            <MessageCircle size={24} />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full flex items-center justify-center animate-pulse-soft">
              <Bot size={10} className="text-white" />
            </span>
          </>
        )}
      </button>

      {!isOpen && (
        <p className="text-[10px] text-obsidian-400 dark:text-obsidian-500 bg-white/80 dark:bg-obsidian-800/80 px-2 py-1 rounded-lg shadow-sm">
          Ctrl+B to chat
        </p>
      )}
    </div>
  );
}
