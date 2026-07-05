import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BookPlus, CopyPlus, Search, Sparkles } from 'lucide-react';
import { circulationApi } from '../../lib/circulation';
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, Panel, StatusBadge, TextField } from './phase2Helpers';

export default function BooksPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [bookForm, setBookForm] = useState({ title: '', author: '', isbn: '', category: '', total_copies: 1 });
  const [copyForm, setCopyForm] = useState({ book_id: '', barcode: '', location: '' });
  const booksQuery = useQuery({ queryKey: ['books', search], queryFn: () => circulationApi.listBooks(search) });

  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  const handleScanCover = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setIsScanning(true);
    setScanError(null);
    try {
      const result = await circulationApi.scanBookCover(file);
      setBookForm({
        title: result.title || '',
        author: result.authors ? result.authors.join(', ') : '',
        isbn: result.isbn || '',
        category: result.categories ? result.categories[0] : '',
        total_copies: bookForm.total_copies,
      });
    } catch (err: any) {
      setScanError(err.response?.data?.detail || 'OCR scan failed. Please enter details manually.');
    } finally {
      setIsScanning(false);
    }
  };

  const createBook = useMutation({
    mutationFn: circulationApi.createBook,
    onSuccess: () => {
      setBookForm({ title: '', author: '', isbn: '', category: '', total_copies: 1 });
      void queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
  const createCopy = useMutation({
    mutationFn: circulationApi.createCopy,
    onSuccess: () => {
      setCopyForm({ book_id: '', barcode: '', location: '' });
      void queryClient.invalidateQueries({ queryKey: ['books'] });
      void queryClient.invalidateQueries({ queryKey: ['book-copies'] });
    },
  });

  const books = booksQuery.data ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Books" description="Catalog titles and track copy availability." />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Panel title="Add Book">
          <div className="mb-4">
            <label className="flex flex-col items-center justify-center border-2 border-dashed border-obsidian-200 hover:border-emerald-400 rounded-lg p-4 cursor-pointer transition-colors bg-obsidian-50/50">
              <Sparkles size={24} className="text-emerald-500 animate-pulse mb-2" />
              <span className="text-xs font-semibold text-obsidian-700">Scan Cover with AI OCR</span>
              <span className="text-[10px] text-obsidian-400 mt-1">Upload JPEG/PNG to pre-fill</span>
              <input type="file" accept="image/*" onChange={handleScanCover} className="hidden" disabled={isScanning} />
            </label>
            {isScanning && (
              <p className="text-xs text-emerald-600 mt-2 flex items-center gap-1.5 animate-pulse">
                <span className="h-2 w-2 rounded-full bg-emerald-500 inline-block animate-ping"></span>
                Processing book cover...
              </p>
            )}
            {scanError && (
              <p className="text-xs text-red-500 mt-2 font-medium">
                {scanError}
              </p>
            )}
          </div>
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              createBook.mutate({
                title: bookForm.title,
                author: bookForm.author,
                isbn: bookForm.isbn || undefined,
                category: bookForm.category || undefined,
                total_copies: bookForm.total_copies,
              });
            }}
          >
            <TextField label="Title" value={bookForm.title} onChange={(event) => setBookForm({ ...bookForm, title: event.target.value })} required disabled={isScanning} />
            <TextField label="Author" value={bookForm.author} onChange={(event) => setBookForm({ ...bookForm, author: event.target.value })} required disabled={isScanning} />
            <TextField label="ISBN" value={bookForm.isbn} onChange={(event) => setBookForm({ ...bookForm, isbn: event.target.value })} disabled={isScanning} />
            <TextField label="Category" value={bookForm.category} onChange={(event) => setBookForm({ ...bookForm, category: event.target.value })} disabled={isScanning} />
            <TextField
              label="Total Copies"
              type="number"
              min={0}
              value={bookForm.total_copies}
              onChange={(event) => setBookForm({ ...bookForm, total_copies: Number(event.target.value) })}
              disabled={isScanning}
            />
            <Button type="submit" loading={createBook.isPending} leftIcon={<BookPlus size={16} />} className="w-full">
              Add book
            </Button>
          </form>
        </Panel>

        <Panel title="Add Copy">
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              createCopy.mutate(copyForm);
            }}
          >
            <label className="flex flex-col gap-1 text-sm font-medium text-obsidian-700">
              Book
              <select
                value={copyForm.book_id}
                onChange={(event) => setCopyForm({ ...copyForm, book_id: event.target.value })}
                required
                className="h-10 rounded-lg border border-obsidian-200 bg-white px-3 text-sm text-obsidian-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option value="">Select a book</option>
                {books.map((book) => <option key={book.id} value={book.id}>{book.title}</option>)}
              </select>
            </label>
            <TextField label="Barcode" value={copyForm.barcode} onChange={(event) => setCopyForm({ ...copyForm, barcode: event.target.value })} required />
            <TextField label="Location" value={copyForm.location} onChange={(event) => setCopyForm({ ...copyForm, location: event.target.value })} />
            <Button type="submit" loading={createCopy.isPending} leftIcon={<CopyPlus size={16} />} className="w-full">
              Add copy
            </Button>
          </form>
        </Panel>

        <Panel title="Search">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-3 text-obsidian-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Title, author, or ISBN"
              className="w-full rounded-lg border border-obsidian-200 py-2.5 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            />
          </div>
        </Panel>
      </div>

      <Panel title="Catalog">
        {booksQuery.isLoading && <LoadingState />}
        {booksQuery.isError && <ErrorState message="Could not load books." />}
        {!booksQuery.isLoading && !booksQuery.isError && books.length === 0 && <EmptyState label="No books yet." />}
        {books.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-obsidian-500 border-b border-obsidian-100">
                <tr>
                  <th className="py-2 pr-4 font-medium">Title</th>
                  <th className="py-2 pr-4 font-medium">Author</th>
                  <th className="py-2 pr-4 font-medium">ISBN</th>
                  <th className="py-2 pr-4 font-medium">Category</th>
                  <th className="py-2 pr-4 font-medium">Availability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-obsidian-100">
                {books.map((book) => (
                  <tr key={book.id}>
                    <td className="py-3 pr-4 font-medium text-obsidian-900">{book.title}</td>
                    <td className="py-3 pr-4 text-obsidian-600">{book.author}</td>
                    <td className="py-3 pr-4 text-obsidian-500">{book.isbn ?? '-'}</td>
                    <td className="py-3 pr-4 text-obsidian-500">{book.category ?? '-'}</td>
                    <td className="py-3 pr-4"><StatusBadge status={`${book.available_copies}/${book.total_copies}`} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
