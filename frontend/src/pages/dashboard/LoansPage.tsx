import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BookMarked } from 'lucide-react';
import { circulationApi } from '../../lib/circulation';
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, Panel, SelectField, StatusBadge, TextField } from './phase2Helpers';

function tomorrowIso() {
  const date = new Date();
  date.setDate(date.getDate() + 14);
  return date.toISOString().slice(0, 10);
}

export default function LoansPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ borrower_id: '', book_copy_id: '', due_date: tomorrowIso() });
  const borrowersQuery = useQuery({ queryKey: ['borrowers'], queryFn: () => circulationApi.listBorrowers() });
  const copiesQuery = useQuery({ queryKey: ['book-copies', 'available'], queryFn: () => circulationApi.listCopies({ status: 'available' }) });
  const loansQuery = useQuery({ queryKey: ['loans'], queryFn: () => circulationApi.listLoans() });
  const issueLoan = useMutation({
    mutationFn: circulationApi.issueLoan,
    onSuccess: () => {
      setForm({ borrower_id: '', book_copy_id: '', due_date: tomorrowIso() });
      void queryClient.invalidateQueries({ queryKey: ['loans'] });
      void queryClient.invalidateQueries({ queryKey: ['book-copies'] });
      void queryClient.invalidateQueries({ queryKey: ['books'] });
    },
  });
  const returnLoan = useMutation({
    mutationFn: circulationApi.returnLoan,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['loans'] });
      void queryClient.invalidateQueries({ queryKey: ['fines'] });
      void queryClient.invalidateQueries({ queryKey: ['book-copies'] });
    },
  });
  const markLost = useMutation({
    mutationFn: circulationApi.markLost,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['loans'] });
      void queryClient.invalidateQueries({ queryKey: ['fines'] });
      void queryClient.invalidateQueries({ queryKey: ['book-copies'] });
    },
  });

  const borrowers = borrowersQuery.data ?? [];
  const copies = copiesQuery.data ?? [];
  const loans = loansQuery.data ?? [];
  const borrowerName = (id: string) => {
    const borrower = borrowers.find((item) => item.id === id);
    return borrower ? `${borrower.first_name} ${borrower.last_name}` : id.slice(0, 8);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Loans" description="Issue books, process returns, and mark lost copies." />
      <Panel title="Issue Book">
        <form
          className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end"
          onSubmit={(event) => {
            event.preventDefault();
            issueLoan.mutate(form);
          }}
        >
          <SelectField label="Borrower" value={form.borrower_id} onChange={(value) => setForm({ ...form, borrower_id: value })}>
            <option value="">Select borrower</option>
            {borrowers.filter((borrower) => borrower.status === 'active').map((borrower) => (
              <option key={borrower.id} value={borrower.id}>{borrower.first_name} {borrower.last_name}</option>
            ))}
          </SelectField>
          <SelectField label="Available Copy" value={form.book_copy_id} onChange={(value) => setForm({ ...form, book_copy_id: value })}>
            <option value="">Select copy</option>
            {copies.map((copy) => <option key={copy.id} value={copy.id}>{copy.barcode}</option>)}
          </SelectField>
          <TextField label="Due Date" type="date" value={form.due_date} onChange={(event) => setForm({ ...form, due_date: event.target.value })} required />
          <Button type="submit" loading={issueLoan.isPending} leftIcon={<BookMarked size={16} />}>Issue</Button>
        </form>
      </Panel>

      <Panel title="Loan Register">
        {loansQuery.isLoading && <LoadingState />}
        {loansQuery.isError && <ErrorState message="Could not load loans." />}
        {!loansQuery.isLoading && !loansQuery.isError && loans.length === 0 && <EmptyState label="No loans issued." />}
        {loans.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-obsidian-500 border-b border-obsidian-100">
                <tr>
                  <th className="py-2 pr-4 font-medium">Borrower</th>
                  <th className="py-2 pr-4 font-medium">Copy</th>
                  <th className="py-2 pr-4 font-medium">Due Date</th>
                  <th className="py-2 pr-4 font-medium">Status</th>
                  <th className="py-2 pr-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-obsidian-100">
                {loans.map((loan) => {
                  const canClose = loan.status === 'issued' || loan.status === 'overdue';
                  return (
                    <tr key={loan.id}>
                      <td className="py-3 pr-4 font-medium text-obsidian-900">{borrowerName(loan.borrower_id)}</td>
                      <td className="py-3 pr-4 text-obsidian-600">{loan.book_copy_id.slice(0, 8)}</td>
                      <td className="py-3 pr-4 text-obsidian-500">{loan.due_date}</td>
                      <td className="py-3 pr-4"><StatusBadge status={loan.status} /></td>
                      <td className="py-3 pr-4">
                        <div className="flex gap-2">
                          <Button type="button" size="sm" variant="outline" disabled={!canClose} onClick={() => returnLoan.mutate(loan.id)}>
                            Return
                          </Button>
                          <Button type="button" size="sm" variant="danger" disabled={!canClose} onClick={() => markLost.mutate(loan.id)}>
                            Lost
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
