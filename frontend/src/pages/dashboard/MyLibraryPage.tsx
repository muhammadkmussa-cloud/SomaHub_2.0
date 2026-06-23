import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Library } from 'lucide-react';
import { ebooksApi } from '../../lib/ebooks';
import { Badge, Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';

export default function MyLibraryPage() {
  const libraryQuery = useQuery({ queryKey: ['my-library'], queryFn: ebooksApi.myLibrary });

  if (libraryQuery.isLoading) return <LoadingState />;
  if (libraryQuery.isError) return <ErrorState message="Failed to load your library." />;

  const purchases = libraryQuery.data ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader
        title="My Library"
        description="Ebooks you own and can read."
        action={
          <Link
            to="/dashboard/bookstore"
            className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
          >
            Browse bookstore →
          </Link>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {purchases.map((purchase: { id: string; ebook_id: string; ebook?: { title: string; author: string } }) => (
          <Card key={purchase.id} className="flex flex-col gap-3">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Library size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <Link
                  to={`/dashboard/bookstore/${purchase.ebook_id}`}
                  className="font-display font-semibold text-obsidian-900 hover:text-emerald-600 block truncate"
                >
                  {purchase.ebook?.title ?? 'Ebook'}
                </Link>
                <p className="text-sm text-obsidian-500 truncate">
                  {purchase.ebook?.author ?? 'Unknown author'}
                </p>
              </div>
            </div>
            <Badge variant="emerald">Owned</Badge>
          </Card>
        ))}
      </div>

      {purchases.length === 0 && (
        <EmptyState label="Your library is empty. Visit the bookstore to add free ebooks." />
      )}
    </div>
  );
}
