import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../../lib/analytics';
import { Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader } from './phase2Helpers';

export default function AnalyticsPage() {
  const dashboardQuery = useQuery({ queryKey: ['analytics-dashboard'], queryFn: analyticsApi.dashboard });
  const trendsQuery = useQuery({ queryKey: ['analytics-trends'], queryFn: () => analyticsApi.trends(14) });
  const topBooksQuery = useQuery({ queryKey: ['analytics-top-books'], queryFn: () => analyticsApi.topBooks(5) });

  if (dashboardQuery.isLoading) return <LoadingState />;
  if (dashboardQuery.isError) return <ErrorState message="Failed to load analytics." />;

  const stats = dashboardQuery.data;
  const trends = trendsQuery.data?.trends ?? [];
  const topBooks = topBooksQuery.data?.books ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Analytics" description="Library performance and circulation insights." />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Books', value: stats?.total_books ?? 0 },
          { label: 'Borrowers', value: stats?.total_borrowers ?? 0 },
          { label: 'Active Loans', value: stats?.active_loans ?? 0 },
          { label: 'Overdue', value: stats?.overdue_loans ?? 0 },
        ].map((item) => (
          <Card key={item.label}>
            <p className="text-2xl font-display font-bold text-obsidian-900">{item.value}</p>
            <p className="text-xs text-obsidian-500">{item.label}</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <h2 className="font-display font-semibold text-obsidian-800 mb-4">Loan trends (14 days)</h2>
          {trends.length === 0 ? (
            <EmptyState label="No loan activity in this period." />
          ) : (
            <ul className="space-y-2 text-sm">
              {trends.map((t) => (
                <li key={t.date} className="flex justify-between text-obsidian-600">
                  <span>{t.date}</span>
                  <span className="font-medium">{t.count} loans</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <h2 className="font-display font-semibold text-obsidian-800 mb-4">Top borrowed books</h2>
          {topBooks.length === 0 ? (
            <EmptyState label="No borrowing data yet." />
          ) : (
            <ul className="space-y-2 text-sm">
              {topBooks.map((book) => (
                <li key={book.book_id} className="flex justify-between text-obsidian-600">
                  <span>{book.title}</span>
                  <span className="font-medium">{book.borrow_count}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
