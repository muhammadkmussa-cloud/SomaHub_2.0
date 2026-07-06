import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import {
  Play,
  Pause,
  RotateCcw,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  FileText,
  Headphones,
  X,
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { ebooksApi } from '../../lib/ebooks';
import { Button, Spinner } from '../../components/ui';

// ── PDF.js worker ─────────────────────────────────────────────────────────────
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

// ── URL resolver: turns /uploads/ebooks/abc.pdf → http://localhost:8000/uploads/... ──
const BACKEND_BASE = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1').replace(
  /\/api\/v1\/?$/,
  '',
);

function resolveUploadUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `${BACKEND_BASE}${url.startsWith('/') ? '' : '/'}${url}`;
}

// ── Fallback book-mode text generator (used when no PDF exists) ───────────────
const generateBookPages = (title: string, author: string): string[] => [
  `${title.toUpperCase()}\n\nBy ${author}`,
  `Chapter 1: The Beginning\n\nThis digital edition of "${title}" is brought to you by SomaHub. Read, learn, and expand your horizons page by page. Enjoy the immersive reading interface.`,
  `Section I\n\nKnowledge is the ultimate key to human progress. Libraries have historically stood as monuments to our shared quest for truth, science, philosophy, and clean craftsmanship.`,
  `Section II\n\nAs you navigate the pages of this book, take notes of key principles, quotes, and reflections. The Text-To-Speech engine can read the pages out loud to help you absorb the content audibly.`,
  `Chapter 2: Core Concepts\n\nEvery journey starts with a simple step. Great software applications begin with clean architecture, robust code patterns, and an aesthetic UI that commands respect.`,
  `Section III\n\nWe design software not just for machines, but for people. The usability, responsiveness, and beauty of an application directly influence its adoption and success.`,
  `Chapter 3: Final Reflections\n\nWe hope this copy of "${title}" aids in your studies and professional development. Continue learning, exploring, and building amazing things.`,
];

const cleanTextForTTS = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/#{1,6}\s+/g, '')
    .replace(/>\s+/g, '')
    .replace(/!\[.*?\]\(.*?\)/g, '') // strip image markdown
    .replace(/(\*\*\*|\*\*|\*|___|__|_) /g, ' ')
    .replace(/(\*\*\*|\*\*|\*|___|__|_)/g, '')
    .replace(/^\s*[-*•]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .trim();
};

const IMAGE_RE = /^!\[.*?\]\(.*?\)/;

const partitionText = (fullText: string, charLimit: number): string[] => {
  const lines = fullText.split('\n');
  const pages: string[] = [];
  let currentLines: string[] = [];
  let len = 0;
  for (const line of lines) {
    const isImage = IMAGE_RE.test(line.trim());
    // Images consume a full page worth of space
    const weight = isImage ? charLimit : line.length;

    if (isImage && currentLines.length > 0) {
      // Flush current text as its own page, then put image on its own page
      pages.push(currentLines.join('\n'));
      pages.push(line);
      currentLines = [];
      len = 0;
    } else if (isImage && currentLines.length === 0) {
      // Image at start — give it its own page
      pages.push(line);
      len = 0;
    } else if (len + weight + 1 > charLimit && currentLines.length > 0) {
      pages.push(currentLines.join('\n'));
      currentLines = [line];
      len = weight;
    } else {
      currentLines.push(line);
      len += weight + 1;
    }
  }
  if (currentLines.length > 0) pages.push(currentLines.join('\n'));
  // Filter out pages that are entirely empty whitespace
  return pages.filter(p => p.trim().length > 0);
};

function renderInlineMarkdown(text: string): React.ReactNode {
  const regex = /(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|___.*?___|__.*?__|__.*?_)/g;
  const parts = text.split(regex);
  return parts.map((part, index) => {
    if (part.startsWith('***') && part.endsWith('***')) {
      return <strong key={index}><em>{part.slice(3, -3)}</em></strong>;
    }
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    return part;
  });
}

function BookPageContent({ text, zoomLevel }: { text: string; zoomLevel: number }) {
  const lines = text.split('\n');
  const nonEmptyLines = lines.filter(l => l.trim());
  const isImageOnly = nonEmptyLines.length === 1 && IMAGE_RE.test(nonEmptyLines[0].trim());
  return (
    <div
      className={`flex-1 overflow-y-auto leading-relaxed pr-1 ${isImageOnly ? 'flex flex-col items-center justify-center' : ''}`}
      style={{ fontSize: `${zoomLevel * 1.125}rem`, lineHeight: '1.6' }}
    >
      {lines.map((line, index) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={index} className="h-3" />;
        }

        // 1. Heading
        const headingMatch = line.match(/^(#{1,4})\s+(.*)/);
        if (headingMatch) {
          const level = headingMatch[1].length;
          const content = headingMatch[2];
          if (level === 1) return <h1 key={index} className="text-2xl font-bold my-4 text-[#1a130b] leading-tight text-left">{renderInlineMarkdown(content)}</h1>;
          if (level === 2) return <h2 key={index} className="text-xl font-semibold my-3.5 text-[#1a130b] leading-tight text-left">{renderInlineMarkdown(content)}</h2>;
          if (level === 3) return <h3 key={index} className="text-lg font-semibold my-3 text-[#1a130b] leading-tight text-left">{renderInlineMarkdown(content)}</h3>;
          return <h4 key={index} className="text-base font-semibold my-2.5 text-[#1a130b] leading-tight text-left">{renderInlineMarkdown(content)}</h4>;
        }

        // 2. Blockquote
        if (line.startsWith('> ')) {
          return (
            <blockquote key={index} className="border-l-4 border-[#cda869] pl-4 py-1.5 my-3 italic text-[#5c4a31] bg-black/[0.02] rounded-r text-left">
              {renderInlineMarkdown(line.slice(2))}
            </blockquote>
          );
        }

        // 3. Lists (bullet or numbered)
        const listMatch = line.match(/^(\s*)([-*•]|\d+\.|\w\.)\s+(.*)/);
        if (listMatch) {
          const leadingSpaces = listMatch[1].length;
          const marker = listMatch[2];
          const content = listMatch[3];
          let paddingClass = 'pl-2';
          if (leadingSpaces >= 8) paddingClass = 'pl-10';
          else if (leadingSpaces >= 4) paddingClass = 'pl-6';
          
          const isBullet = ['-', '*', '•'].includes(marker);
          const displayMarker = isBullet ? (leadingSpaces >= 4 ? '◦' : '•') : marker;
          
          return (
            <div key={index} className={`flex items-start gap-2 py-0.5 my-1 text-left ${paddingClass}`}>
              <span className="select-none text-[#a49162] font-semibold min-w-[14px]">{displayMarker}</span>
              <span className="flex-1">{renderInlineMarkdown(content)}</span>
            </div>
          );
        }

        // 3.5. Images / Charts / Graphs / Diagrams
        const imageMatch = trimmed.match(/^!\[(.*?)\]\((.*?)\)/);
        if (imageMatch) {
          const altText = imageMatch[1];
          const src = imageMatch[2];
          const resolvedSrc = resolveUploadUrl(src) || src;
          const isChart = altText.toLowerCase().includes('chart') || 
                          altText.toLowerCase().includes('diagram') || 
                          altText.toLowerCase().includes('graph') ||
                          altText.toLowerCase().includes('data');
          
          return (
            <div key={index} className={`flex flex-col items-center justify-center rounded-xl overflow-hidden ${isImageOnly ? 'my-0 w-full h-full' : 'my-3'}`}>
              {/* Badge row */}
              <div className="w-full flex items-center gap-2 mb-2 shrink-0">
                <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[9px] font-bold uppercase tracking-widest select-none border ${
                  isChart
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    isChart ? 'bg-emerald-500' : 'bg-amber-500'
                  }`} />
                  {isChart ? 'Chart / Diagram' : 'Figure'}
                </div>
                {altText && (
                  <span className="text-[10px] text-[#8c7b50] italic truncate">
                    {altText}
                  </span>
                )}
              </div>
              {/* Image container */}
              <div className={`w-full flex items-center justify-center bg-white rounded-lg border border-[#e0cf9b]/60 shadow-sm ${isImageOnly ? 'flex-1 p-3' : 'p-2'}`}>
                <img
                  src={resolvedSrc}
                  alt={altText}
                  className={`max-w-full rounded object-contain ${isImageOnly ? 'max-h-[420px]' : 'max-h-[240px]'}`}
                  loading="lazy"
                />
              </div>
            </div>
          );
        }

        // 4. Paragraph
        return (
          <p key={index} className="my-2.5 text-left leading-relaxed">
            {renderInlineMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

export default function BookReaderPage() {
  const { ebookId = '' } = useParams();

  // ── Ebook data ─────────────────────────────────────────────────────────────
  const { data: ebook, isLoading, isError } = useQuery({
    queryKey: ['ebook', ebookId],
    queryFn: () => ebooksApi.get(ebookId),
    enabled: !!ebookId,
  });

  // ── Reading progress data ──────────────────────────────────────────────────
  const { data: progressData } = useQuery({
    queryKey: ['reading-progress', ebookId],
    queryFn: () => ebooksApi.getProgress(ebookId),
    enabled: !!ebookId,
    retry: false,
  });

  const pdfUrl = resolveUploadUrl(ebook?.file_url);
  const hasPdf = !!pdfUrl;

  // ── View mode (pdf = real PDF | book = serif text mode) ────────────────────
  const [viewMode, setViewMode] = useState<'pdf' | 'book'>('pdf');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isImmersive, setIsImmersive] = useState(false);

  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!(
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).mozFullScreenElement ||
        (document as any).msFullscreenElement
      );
      setIsFullscreen(isCurrentlyFullscreen);
      if (!isCurrentlyFullscreen) {
        setIsImmersive(false);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, []);

  // Switch to pdf mode by default once we know if a PDF exists
  useEffect(() => {
    if (ebook) setViewMode(hasPdf ? 'pdf' : 'book');
  }, [ebook, hasPdf]);

  // ── PDF state ──────────────────────────────────────────────────────────────
  const [numPdfPages, setNumPdfPages] = useState(0);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [pdfLoaded, setPdfLoaded] = useState(false);

  // ── Shared navigation state ────────────────────────────────────────────────
  // currentPage is a 1-indexed "spread" index (1 spread = 1 or 2 physical pages in double mode)
  const [currentPage, setCurrentPage] = useState(1);
  const [doublePage, setDoublePage] = useState(true);

  // ── Zoom ───────────────────────────────────────────────────────────────────
  const [zoomLevel, setZoomLevel] = useState(1.0);

  // ── TTS (book-mode only) ───────────────────────────────────────────────────
  const [isPlaying, setIsPlaying] = useState(false);
  const [speechRate, setSpeechRate] = useState(1);

  // ── Container ref for responsive PDF width ─────────────────────────────────
  const containerRef = useRef<HTMLDivElement>(null);
  const readerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) setContainerWidth(entry.contentRect.width);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // ── PDF page math ──────────────────────────────────────────────────────────
  const totalPdfSpreads = doublePage ? Math.ceil(numPdfPages / 2) : numPdfPages;
  const leftPdfPage = doublePage ? (currentPage - 1) * 2 + 1 : currentPage;
  const rightPdfPage = doublePage ? (currentPage - 1) * 2 + 2 : null;

  // Page width per PDF page (leave room for gutter + padding)
  const pdfPageWidth = containerWidth
    ? Math.min(
        Math.floor((containerWidth - (doublePage ? 56 : 32)) / (doublePage ? 2 : 1)),
        620,
      ) * zoomLevel
    : undefined;

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPdfPages(numPages);
    setPdfLoaded(true);
    setPdfError(null);
  }, []);

  const onDocumentLoadError = useCallback((err: Error) => {
    setPdfError(`Failed to load PDF: ${err.message}`);
    setPdfLoaded(false);
  }, []);

  // ── Book-mode text ─────────────────────────────────────────────────────────
  const baseText = ebook?.content || (ebook ? generateBookPages(ebook.title, ebook.author).join('\n\n') : '');
  const charLimit = Math.floor(480 / (zoomLevel * zoomLevel));
  const textPages = partitionText(baseText, charLimit);
  const totalTextSpreads = doublePage ? Math.ceil(textPages.length / 2) : textPages.length;

  const totalSpreads = viewMode === 'pdf' ? totalPdfSpreads : totalTextSpreads;
  const safeCurrentPage = Math.min(currentPage, Math.max(1, totalSpreads));

  // ── Restore Reading Progress ───────────────────────────────────────────────
  const hasRestoredProgress = useRef(false);

  useEffect(() => {
    if (!ebook || !progressData || hasRestoredProgress.current) return;

    if (viewMode === 'pdf') {
      if (pdfLoaded && numPdfPages > 0) {
        const lastPage = progressData.last_page || 1;
        const targetSpread = doublePage ? Math.floor((lastPage - 1) / 2) + 1 : lastPage;
        const maxSpreads = doublePage ? Math.ceil(numPdfPages / 2) : numPdfPages;
        setCurrentPage(Math.max(1, Math.min(maxSpreads, targetSpread)));
        hasRestoredProgress.current = true;
      }
    } else {
      if (textPages.length > 0) {
        const lastPage = progressData.last_page || 1;
        const targetSpread = doublePage ? Math.floor((lastPage - 1) / 2) + 1 : lastPage;
        const maxSpreads = doublePage ? Math.ceil(textPages.length / 2) : textPages.length;
        setCurrentPage(Math.max(1, Math.min(maxSpreads, targetSpread)));
        hasRestoredProgress.current = true;
      }
    }
  }, [ebook, progressData, viewMode, pdfLoaded, numPdfPages, textPages.length, doublePage]);

  // ── Save Reading Progress ──────────────────────────────────────────────────
  useEffect(() => {
    if (!hasRestoredProgress.current || !ebookId) return;

    const physPage = doublePage ? (safeCurrentPage - 1) * 2 + 1 : safeCurrentPage;
    const totalPages = viewMode === 'pdf' ? numPdfPages : textPages.length;
    if (totalPages <= 0) return;

    const progressPercent = Math.min(100, Math.max(0, Math.round((physPage / totalPages) * 100)));

    const timer = setTimeout(async () => {
      try {
        await ebooksApi.updateProgress(ebookId, progressPercent, physPage);
      } catch (err) {
        console.error('Failed to save reading progress:', err);
      }
    }, 1500);

    return () => clearTimeout(timer);
  }, [safeCurrentPage, doublePage, viewMode, numPdfPages, textPages.length, ebookId]);

  // ── Navigation helpers ─────────────────────────────────────────────────────
  const goTo = (page: number) => setCurrentPage(Math.max(1, Math.min(totalSpreads, page)));

  // ── TTS ────────────────────────────────────────────────────────────────────
  useEffect(() => () => window.speechSynthesis.cancel(), []);
  useEffect(() => { if (isPlaying) speakPage(); }, [safeCurrentPage]);

  const speakPage = () => {
    window.speechSynthesis.cancel();
    const leftIdx = doublePage ? (safeCurrentPage - 1) * 2 : safeCurrentPage - 1;
    const rightIdx = doublePage ? leftIdx + 1 : -1;
    const rawText = [textPages[leftIdx] || '', rightIdx >= 0 ? textPages[rightIdx] || '' : ''].join('. ');
    const text = cleanTextForTTS(rawText);
    if (!text.trim()) return;
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = speechRate;
    utt.onend = () => setIsPlaying(false);
    utt.onerror = () => setIsPlaying(false);
    window.speechSynthesis.speak(utt);
    setIsPlaying(true);
  };

  const handlePlayPause = () => {
    if (isPlaying) { window.speechSynthesis.cancel(); setIsPlaying(false); }
    else speakPage();
  };

  // ── Keyboard Navigation ────────────────────────────────────────────────────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        document.activeElement?.tagName === 'INPUT' ||
        document.activeElement?.tagName === 'SELECT' ||
        document.activeElement?.tagName === 'TEXTAREA'
      ) {
        return;
      }
      if (e.key === 'ArrowRight') {
        setCurrentPage((prev) => Math.min(totalSpreads, prev + 1));
      } else if (e.key === 'ArrowLeft') {
        setCurrentPage((prev) => Math.max(1, prev - 1));
      } else if (e.key === 'Escape') {
        setIsImmersive(false);
        const isNativeFs = !!(
          document.fullscreenElement ||
          (document as any).webkitFullscreenElement ||
          (document as any).mozFullScreenElement ||
          (document as any).msFullscreenElement
        );
        if (isNativeFs) {
          if (document.exitFullscreen) {
            void document.exitFullscreen();
          } else if ((document as any).webkitExitFullscreen) {
            void (document as any).webkitExitFullscreen();
          } else if ((document as any).mozCancelFullScreen) {
            void (document as any).mozCancelFullScreen();
          } else if ((document as any).msExitFullscreen) {
            void (document as any).msExitFullscreen();
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [totalSpreads]);

  // ── Fullscreen ─────────────────────────────────────────────────────────────
  const toggleFullScreen = () => {
    const elem = readerRef.current;
    const doc = document as any;
    if (!elem) return;

    if (!isImmersive) {
      setIsImmersive(true);
      if (elem.requestFullscreen) {
        elem.requestFullscreen().catch((err) => console.warn("Fullscreen request failed:", err));
      } else if ((elem as any).webkitRequestFullscreen) {
        (elem as any).webkitRequestFullscreen();
      } else if ((elem as any).mozRequestFullScreen) {
        (elem as any).mozRequestFullScreen();
      } else if ((elem as any).msRequestFullscreen) {
        (elem as any).msRequestFullscreen();
      }
    } else {
      setIsImmersive(false);
      const isNativeFs = !!(
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).mozFullScreenElement ||
        (document as any).msFullscreenElement
      );
      if (isNativeFs) {
        if (document.exitFullscreen) {
          void document.exitFullscreen();
        } else if (doc.webkitExitFullscreen) {
          void doc.webkitExitFullscreen();
        } else if (doc.mozCancelFullScreen) {
          void doc.mozCancelFullScreen();
        } else if (doc.msExitFullscreen) {
          void doc.msExitFullscreen();
        }
      }
    }
  };

  // ── Smart View Transitions ────────────────────────────────────────────────
  const handleViewModeChange = (newMode: 'pdf' | 'book') => {
    const physPage = doublePage ? (safeCurrentPage - 1) * 2 + 1 : safeCurrentPage;
    setViewMode(newMode);

    if (newMode === 'pdf') {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    }

    const newTotalSpreads = newMode === 'pdf' ? totalPdfSpreads : totalTextSpreads;
    const newSpread = doublePage ? Math.floor((physPage - 1) / 2) + 1 : physPage;
    setCurrentPage(Math.max(1, Math.min(newTotalSpreads, newSpread)));
  };

  const handleDoublePageToggle = () => {
    const physPage = doublePage ? (safeCurrentPage - 1) * 2 + 1 : safeCurrentPage;
    const newDouble = !doublePage;
    setDoublePage(newDouble);

    const newTotal = viewMode === 'pdf'
      ? (newDouble ? Math.ceil(numPdfPages / 2) : numPdfPages)
      : (newDouble ? Math.ceil(textPages.length / 2) : textPages.length);

    const newSpread = newDouble ? Math.floor((physPage - 1) / 2) + 1 : physPage;
    setCurrentPage(Math.max(1, Math.min(newTotal, newSpread)));
  };

  // ── Handle zoom with position preservation ─────────────────────────────────
  const handleZoomChange = (newZoom: number) => {
    const progress = (safeCurrentPage - 1) / Math.max(1, totalSpreads - 1);
    setZoomLevel(newZoom);
    if (viewMode === 'book') {
      const newCharLimit = Math.floor(650 / (newZoom * newZoom));
      const newPages = partitionText(baseText, newCharLimit);
      const newTotal = doublePage ? Math.ceil(newPages.length / 2) : newPages.length;
      setCurrentPage(Math.max(1, Math.round(progress * (newTotal - 1)) + 1));
    }
  };

  // ── Loading / error states ─────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="min-h-screen bg-obsidian-950 flex items-center justify-center">
        <Spinner size="lg" className="text-emerald-500" />
      </div>
    );
  }

  if (isError || !ebook) {
    return (
      <div className="min-h-screen bg-obsidian-950 flex flex-col items-center justify-center gap-4 text-center p-6">
        <p className="text-xl text-white font-medium">Ebook reader failed to load.</p>
        <Link to="/dashboard/my-library">
          <Button>Back to library</Button>
        </Link>
      </div>
    );
  }

  const coverUrl = resolveUploadUrl(ebook.cover_url);
  const leftTextPage = doublePage ? textPages[(safeCurrentPage - 1) * 2] : textPages[safeCurrentPage - 1];
  const rightTextPage = doublePage ? textPages[(safeCurrentPage - 1) * 2 + 1] : null;

  return (
    <div ref={readerRef} className="fixed inset-0 bg-black z-50 flex flex-col justify-between overflow-hidden select-none font-sans">
      {/* Immersive Floating Exit Button */}
      {isImmersive && (
        <button
          onClick={toggleFullScreen}
          className="absolute top-4 right-4 z-50 w-10 h-10 rounded-full bg-black/60 hover:bg-emerald-600/90 text-white flex items-center justify-center transition-all shadow-lg border border-white/10"
          title="Exit Full Screen"
        >
          <Minimize2 size={18} />
        </button>
      )}

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      {!isImmersive && (
        <header className="h-14 bg-obsidian-900 border-b border-obsidian-800 flex items-center justify-between px-4 text-white shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <Link to="/dashboard/my-library" className="hover:text-emerald-400 transition-colors shrink-0">
              <X size={20} />
            </Link>
            {coverUrl && (
              <img src={coverUrl} alt={ebook.title} className="h-8 w-6 rounded object-cover shrink-0 border border-obsidian-700" />
            )}
            <div className="min-w-0">
              <h1 className="text-sm font-semibold truncate max-w-[160px] sm:max-w-sm">{ebook.title}</h1>
              <p className="text-xs text-obsidian-400 truncate">{ebook.author}</p>
            </div>
          </div>

          {/* View mode toggle (only shown when PDF is available) */}
          {hasPdf && (
            <div className="flex bg-obsidian-800 rounded-lg p-0.5 border border-obsidian-700">
              <button
                onClick={() => handleViewModeChange('pdf')}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  viewMode === 'pdf' ? 'bg-emerald-600 text-white' : 'text-obsidian-400 hover:text-white'
                }`}
              >
                <FileText size={14} />
                PDF
              </button>
              <button
                onClick={() => handleViewModeChange('book')}
                className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  viewMode === 'book' ? 'bg-emerald-600 text-white' : 'text-obsidian-400 hover:text-white'
                }`}
              >
                <BookOpen size={14} />
                Text
              </button>
            </div>
          )}

          <button
            onClick={toggleFullScreen}
            className="text-obsidian-400 hover:text-white transition-colors shrink-0"
            title={isImmersive ? "Exit Full Screen" : "Full Screen"}
          >
            {isImmersive ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
        </header>
      )}

      {/* ── Main canvas ─────────────────────────────────────────────────────── */}
      <main ref={containerRef} className="flex-1 relative flex overflow-auto bg-obsidian-950 p-4 sm:p-6 group">
        
        {/* Floating Canvas Navigation Arrows */}
        {safeCurrentPage > 1 && (
          <button
            onClick={() => goTo(safeCurrentPage - 1)}
            className="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-black/40 hover:bg-emerald-600/90 text-white flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 hidden md:flex cursor-pointer"
            title="Previous Page"
          >
            <ChevronLeft size={24} />
          </button>
        )}
        {safeCurrentPage < totalSpreads && (
          <button
            onClick={() => goTo(safeCurrentPage + 1)}
            className="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-black/40 hover:bg-emerald-600/90 text-white flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 hidden md:flex cursor-pointer"
            title="Next Page"
          >
            <ChevronRight size={24} />
          </button>
        )}

        {/* ── PDF VIEW MODE ─────────────────────────────────────────────────── */}
        {viewMode === 'pdf' && pdfUrl && (
          <div className="mx-auto my-auto flex flex-col items-center w-full max-w-[1280px]">
            {pdfError && (
              <div className="flex flex-col items-center gap-3 text-red-400 py-16">
                <AlertCircle size={40} className="opacity-60" />
                <p className="text-sm font-medium">{pdfError}</p>
                <p className="text-xs text-obsidian-500">Make sure the backend is running and the file was uploaded correctly.</p>
              </div>
            )}

            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex flex-col items-center gap-3 py-24 text-obsidian-400">
                  <Loader2 size={36} className="animate-spin text-emerald-500" />
                  <span className="text-sm">Loading PDF…</span>
                </div>
              }
              error={null /* handled by onLoadError */}
              className="flex items-start justify-center gap-2"
            >
              {doublePage ? (
                <>
                  {leftPdfPage <= numPdfPages && (
                    <div className="shadow-2xl">
                      <Page
                        key={`pdf-left-${leftPdfPage}`}
                        pageNumber={leftPdfPage}
                        width={pdfPageWidth}
                        renderAnnotationLayer
                        renderTextLayer
                        loading={
                          <div className="flex items-center justify-center bg-white" style={{ width: pdfPageWidth, height: (pdfPageWidth ?? 400) * 1.414 }}>
                            <Loader2 size={24} className="animate-spin text-obsidian-300" />
                          </div>
                        }
                      />
                    </div>
                  )}
                  {rightPdfPage && rightPdfPage <= numPdfPages && (
                    <div className="shadow-2xl">
                      <Page
                        key={`pdf-right-${rightPdfPage}`}
                        pageNumber={rightPdfPage}
                        width={pdfPageWidth}
                        renderAnnotationLayer
                        renderTextLayer
                        loading={
                          <div className="flex items-center justify-center bg-white" style={{ width: pdfPageWidth, height: (pdfPageWidth ?? 400) * 1.414 }}>
                            <Loader2 size={24} className="animate-spin text-obsidian-300" />
                          </div>
                        }
                      />
                    </div>
                  )}
                </>
              ) : (
                <div className="shadow-2xl">
                  <Page
                    key={`pdf-single-${safeCurrentPage}`}
                    pageNumber={safeCurrentPage}
                    width={pdfPageWidth}
                    renderAnnotationLayer
                    renderTextLayer
                    loading={
                      <div className="flex items-center justify-center bg-white" style={{ width: pdfPageWidth, height: (pdfPageWidth ?? 400) * 1.414 }}>
                        <Loader2 size={24} className="animate-spin text-obsidian-300" />
                      </div>
                    }
                  />
                </div>
              )}
            </Document>
          </div>
        )}

        {/* ── BOOK / TEXT VIEW MODE ─────────────────────────────────────────── */}
        {viewMode === 'book' && (
          <div className={`mx-auto my-auto w-full ${doublePage ? 'max-w-5xl' : 'max-w-xl'} h-full flex items-center justify-center`}>
            <div className={`grid grid-cols-1 ${doublePage ? 'md:grid-cols-2' : ''} w-full h-[85vh] max-h-[680px] bg-[#fbf5e6] text-[#2c2214] font-serif rounded-lg shadow-2xl overflow-hidden relative border border-[#eadaab]`}>
              {/* Left page */}
              <div className={`flex flex-col justify-between p-6 sm:p-10 ${doublePage ? 'md:border-r border-[#e0cf9b]' : ''} h-full relative`}>
                <div className="flex justify-between text-[11px] text-[#8c7b50] italic border-b border-[#e2d5ab] pb-1.5 mb-4">
                  <span>{doublePage ? (safeCurrentPage - 1) * 2 + 1 : safeCurrentPage}</span>
                  <span>{ebook.title}</span>
                </div>
                <BookPageContent text={leftTextPage || 'End of Book'} zoomLevel={zoomLevel} />
                <div className="text-center text-xs text-[#8c7b50] font-semibold mt-4">
                  {doublePage ? (safeCurrentPage - 1) * 2 + 1 : safeCurrentPage}
                </div>
              </div>

              {/* Right page (double-page mode) */}
              {doublePage && (
                <div className="hidden md:flex flex-col justify-between p-6 sm:p-10 h-full relative bg-[#FAF3E0]">
                  <div className="flex justify-between text-[11px] text-[#8c7b50] italic border-b border-[#e2d5ab] pb-1.5 mb-4">
                     <span>CONTINUED</span>
                     <span>{(safeCurrentPage - 1) * 2 + 2}</span>
                  </div>
                  <BookPageContent text={rightTextPage || ''} zoomLevel={zoomLevel} />
                  <div className="text-center text-xs text-[#8c7b50] font-semibold mt-4">
                    {(safeCurrentPage - 1) * 2 + 2}
                  </div>
                  <div className="absolute top-0 left-0 bottom-0 w-4 bg-gradient-to-r from-black/[0.05] to-transparent pointer-events-none" />
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* ── Footer controls ──────────────────────────────────────────────────── */}
      {!isImmersive && (
        <footer className="bg-obsidian-900 border-t border-obsidian-800 text-white flex flex-col gap-2 p-3 sm:px-6 shrink-0">

        {/* TTS row – active in book mode, dimmed in PDF mode */}
        <div className={`flex flex-wrap items-center justify-between gap-4 border-b border-obsidian-850 pb-2 transition-opacity ${viewMode === 'pdf' ? 'opacity-40 pointer-events-none' : 'opacity-100'}`}>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <Headphones size={16} />
            </span>
            <span className="text-xs font-semibold tracking-wider uppercase text-emerald-400">
              {viewMode === 'pdf' ? 'Audio (Text mode only)' : 'Audio Read Aloud'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handlePlayPause}
              className="w-10 h-10 rounded-full bg-emerald-600 hover:bg-emerald-500 flex items-center justify-center shadow-lg transition-transform active:scale-95"
            >
              {isPlaying ? <Pause size={18} fill="white" /> : <Play size={18} fill="white" className="ml-0.5" />}
            </button>
            <button onClick={() => goTo(safeCurrentPage - 1)} className="p-2 text-obsidian-400 hover:text-white transition-colors" title="Previous Page">
              <RotateCcw size={18} />
            </button>
            <button onClick={() => goTo(safeCurrentPage + 1)} className="p-2 text-obsidian-400 hover:text-white transition-colors" title="Next Page">
              <RotateCw size={18} />
            </button>
            <div className="flex items-center gap-1.5 ml-2 border-l border-obsidian-800 pl-3">
              <select
                value={speechRate}
                onChange={(e) => {
                  setSpeechRate(Number(e.target.value));
                  if (isPlaying) setTimeout(() => speakPage(), 50);
                }}
                className="bg-obsidian-800 border border-obsidian-750 text-xs rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-emerald-400"
              >
                <option value="0.75">0.75x</option>
                <option value="1">1.0x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="2">2.0x</option>
              </select>
            </div>
          </div>
        </div>

        {/* Navigation & page scrubber row */}
        <div className="flex items-center justify-between gap-4">
          <div className="text-xs sm:text-sm font-medium text-obsidian-300 select-none w-36 shrink-0">
            {viewMode === 'pdf' && pdfLoaded
              ? `Pages ${leftPdfPage}${rightPdfPage && rightPdfPage <= numPdfPages ? `–${rightPdfPage}` : ''} / ${numPdfPages}`
              : `Page ${safeCurrentPage} / ${totalSpreads}`}
          </div>

          <input
            type="range"
            min={1}
            max={Math.max(1, totalSpreads)}
            value={safeCurrentPage}
            onChange={(e) => goTo(Number(e.target.value))}
            className="flex-1 accent-emerald-500 h-1.5 bg-obsidian-800 rounded-lg cursor-pointer appearance-none"
          />

          <div className="flex items-center gap-2 shrink-0 pr-16 md:pr-0">
            {/* Zoom */}
            <div className="flex items-center gap-1 bg-obsidian-800 rounded border border-obsidian-750 px-1 py-0.5">
              <button
                onClick={() => handleZoomChange(Math.max(0.6, zoomLevel - 0.2))}
                disabled={zoomLevel <= 0.6}
                className="p-1 rounded text-obsidian-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="Zoom Out"
              >
                <ZoomOut size={15} />
              </button>
              <span className="text-xs font-semibold px-1 min-w-[36px] text-center select-none text-obsidian-200">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => handleZoomChange(Math.min(2.5, zoomLevel + 0.2))}
                disabled={zoomLevel >= 2.5}
                className="p-1 rounded text-obsidian-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="Zoom In"
              >
                <ZoomIn size={15} />
              </button>
            </div>

            {/* Prev spread */}
            <button
              onClick={() => goTo(safeCurrentPage - 1)}
              disabled={safeCurrentPage <= 1}
              className="p-1.5 rounded-lg hover:bg-obsidian-800 text-obsidian-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={20} />
            </button>

            {/* Double-page toggle */}
            <button
              onClick={handleDoublePageToggle}
              className={`px-2 py-1 text-xs font-semibold rounded border transition-colors ${
                doublePage
                  ? 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30'
                  : 'bg-obsidian-800 text-obsidian-400 border-obsidian-700'
              }`}
              title="Toggle single / double page"
            >
              {doublePage ? '2 Pages' : '1 Page'}
            </button>

            {/* Next spread */}
            <button
              onClick={() => goTo(safeCurrentPage + 1)}
              disabled={safeCurrentPage >= totalSpreads}
              className="p-1.5 rounded-lg hover:bg-obsidian-800 text-obsidian-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
        </footer>
      )}
    </div>
  );
}
