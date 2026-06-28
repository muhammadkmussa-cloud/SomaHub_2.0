import api from './api';

export interface Citation {
  source: string;
  type: string;
  text_snippet: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
  error?: boolean;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  sources: Record<string, unknown>[];
  context_used: boolean;
}

export interface StreamEvent {
  type: 'token' | 'citations' | 'done' | 'error';
  data: unknown;
}

export interface AIStatus {
  vector_store_count: number;
  ollama_status: string;
  ollama_models: string[];
}

export const chatbotApi = {
  async sendMessage(
    message: string,
    history: { role: string; content: string }[] = [],
    onToken?: (token: string) => void,
    onCitations?: (citations: Citation[]) => void,
    onError?: (error: string) => void,
  ): Promise<string> {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/ai/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(api.defaults.headers.common['Authorization']
            ? { Authorization: api.defaults.headers.common['Authorization'] as string }
            : {}),
        },
        body: JSON.stringify({
          message,
          history: history.slice(-20).map((h) => ({
            role: h.role,
            content: h.content,
          })),
          stream: true,
        }),
      },
    );

    if (!response.ok) {
      const errorText = await response.text();
      onError?.(errorText || 'Failed to get response');
      return '';
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError?.('No response stream available');
      return '';
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let fullAnswer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const event: StreamEvent = JSON.parse(line);
          switch (event.type) {
            case 'token':
              if (typeof event.data === 'string') {
                fullAnswer += event.data;
                onToken?.(event.data);
              }
              break;
            case 'citations':
              if (Array.isArray(event.data)) {
                onCitations?.(event.data as Citation[]);
              }
              break;
            case 'error':
              onError?.(String(event.data));
              break;
          }
        } catch {
          // Skip malformed lines
        }
      }
    }

    return fullAnswer;
  },

  async ingestDocument(file: File): Promise<{ chunks_indexed: number; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/ai/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async ocrImage(file: File): Promise<Record<string, unknown>> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/ai/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async ocrCatalog(file: File): Promise<{ book_id: string; metadata: Record<string, unknown> }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/ai/ocr/catalog', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getStatus(): Promise<AIStatus> {
    const response = await api.get('/ai/status');
    return response.data;
  },

  async indexAppKnowledge(): Promise<{ status: string; entries_indexed: number }> {
    const response = await api.post('/ai/knowledge/index-app');
    return response.data;
  },

  async indexBooks(): Promise<{ status: string; books_indexed: number }> {
    const response = await api.post('/ai/knowledge/index-books');
    return response.data;
  },

  async search(query: string, topK: number = 5, category?: string): Promise<{ results: unknown[]; total: number }> {
    const params = new URLSearchParams({ query, top_k: String(topK) });
    if (category) params.set('filter_category', category);
    const response = await api.post(`/ai/search?${params}`);
    return response.data;
  },
};
