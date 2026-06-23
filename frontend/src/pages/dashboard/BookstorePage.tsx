import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ShoppingBag } from 'lucide-react';
import { ebooksApi } from '../../lib/ebooks';
import { Badge, Button, Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';

export default function BookstorePage() {
  const queryClient = useQueryClient();
  const ebooksQuery = useQuery({ queryKey: ['ebooks'], queryFn: ebooksApi.list });
  const libraryQuery = useQuery({ queryKey: ['my-library'], queryFn: ebooksApi.myLibrary });

  const checkout = useMutation({
    mutationFn: ebooksApi.checkoutFree,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['my-library'] });
      void queryClient.invalidateQueries({ queryKey: ['ebooks'] });
    },
  });

  if (ebooksQuery.isLoading) return <LoadingState />;
  if (ebooksQuery.isError) return <ErrorState message="Failed to load ebooks." />;

  const ownedIds = new Set((libraryQuery.data ?? []).map((p: { ebook_id: string }) => p.ebook_id));

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Bookstore" description="Browse and purchase digital books." />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(ebooksQuery.data ?? []).map((ebook) => (
          <Card key={ebook.id} className="flex flex-col gap-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <Link to={`/dashboard/bookstore/${ebook.id}`} className="font-display font-semibold text-obsidian-900 hover:text-emerald-600">
                  {ebook.title}
                </Link>
                <p className="text-sm text-obsidian-500">{ebook.author}</p>
              </div>
              <Badge variant={ebook.price === 0 ? 'emerald' : 'sapphire'}>
                {ebook.price === 0 ? 'Free' : `$${ebook.price.toFixed(2)}`}
              </Badge>
            </div>
            {ebook.description && (
              <p className="text-sm text-obsidian-600 line-clamp-3">{ebook.description}</p>
            )}
            {ownedIds.has(ebook.id) ? (
              <Badge variant="emerald">In your library</Badge>
            ) : ebook.price === 0 ? (
              <Button
                size="sm"
                loading={checkout.isPending}
                leftIcon={<ShoppingBag size={16} />}
                onClick={() => checkout.mutate(ebook.id)}
              >
                Add to library
              </Button>
            ) : (
              <p className="text-xs text-obsidian-400">Paid checkout via billing (Stripe/Paystack)</p>
            )}
          </Card>
        ))}
      </div>

      {(ebooksQuery.data ?? []).length === 0 && <EmptyState label="No ebooks published yet." />}
    </div>
  );
}
