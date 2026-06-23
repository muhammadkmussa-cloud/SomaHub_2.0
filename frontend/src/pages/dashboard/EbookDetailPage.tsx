import { useParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { ebooksApi } from '../../lib/ebooks';
import { readerApi } from '../../lib/reader';
import { Button, Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';

export default function EbookDetailPage() {
  const { ebookId = '' } = useParams();
  const queryClient = useQueryClient();
  const [review, setReview] = useState({ rating: 5, comment: '' });

  const ebookQuery = useQuery({
    queryKey: ['ebook', ebookId],
    queryFn: () => ebooksApi.get(ebookId),
    enabled: !!ebookId,
  });
  const ownedQuery = useQuery({
    queryKey: ['ebook-owned', ebookId],
    queryFn: () => readerApi.checkOwned(ebookId),
    enabled: !!ebookId,
  });
  const reviewsQuery = useQuery({
    queryKey: ['ebook-reviews', ebookId],
    queryFn: () => readerApi.listReviews(ebookId),
    enabled: !!ebookId,
  });

  const checkout = useMutation({
    mutationFn: () => ebooksApi.checkoutFree(ebookId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['ebook-owned', ebookId] });
      void queryClient.invalidateQueries({ queryKey: ['my-library'] });
    },
  });
  const favorite = useMutation({
    mutationFn: () => ebooksApi.addFavorite(ebookId),
  });
  const submitReview = useMutation({
    mutationFn: () => readerApi.addReview(ebookId, review.rating, review.comment),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['ebook-reviews', ebookId] }),
  });
  const saveProgress = useMutation({
    mutationFn: (progress: number) => readerApi.saveProgress(ebookId, progress),
  });

  if (ebookQuery.isLoading) return <LoadingState />;
  if (ebookQuery.isError || !ebookQuery.data) return <ErrorState message="Ebook not found." />;

  const ebook = ebookQuery.data;
  const owned = ownedQuery.data?.owned;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <Link to="/dashboard/bookstore" className="text-sm text-emerald-600 hover:underline">
        ← Back to bookstore
      </Link>
      <PageHeader title={ebook.title} description={ebook.author} />

      <Card className="space-y-4">
        {ebook.description && <p className="text-obsidian-600">{ebook.description}</p>}
        <div className="flex flex-wrap gap-2">
          {!owned && ebook.price === 0 && (
            <Button loading={checkout.isPending} onClick={() => checkout.mutate()}>
              Add to library
            </Button>
          )}
          {owned && (
            <>
              <Button variant="secondary" onClick={() => saveProgress.mutate(50)}>
                Save 50% progress
              </Button>
              <Button variant="outline" loading={favorite.isPending} onClick={() => favorite.mutate()}>
                Add to favorites
              </Button>
            </>
          )}
        </div>
      </Card>

      <Card>
        <h2 className="font-display font-semibold text-obsidian-800 mb-3">Reviews</h2>
        {owned && (
          <form
            className="space-y-2 mb-4"
            onSubmit={(e) => {
              e.preventDefault();
              submitReview.mutate();
            }}
          >
            <input
              type="number"
              min={1}
              max={5}
              value={review.rating}
              onChange={(e) => setReview({ ...review, rating: Number(e.target.value) })}
              className="border rounded px-2 py-1 text-sm w-20"
            />
            <textarea
              value={review.comment}
              onChange={(e) => setReview({ ...review, comment: e.target.value })}
              placeholder="Write a review..."
              className="w-full border rounded px-3 py-2 text-sm"
              rows={3}
            />
            <Button type="submit" size="sm" loading={submitReview.isPending}>
              Submit review
            </Button>
          </form>
        )}
        {(reviewsQuery.data ?? []).length === 0 ? (
          <EmptyState label="No reviews yet." />
        ) : (
          <ul className="space-y-2 text-sm">
            {(reviewsQuery.data ?? []).map((r: { id: string; rating: number; comment: string }) => (
              <li key={r.id} className="border-b border-obsidian-50 pb-2">
                <span className="font-medium">{r.rating}/5</span> — {r.comment}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
