import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CreditCard } from 'lucide-react';
import { circulationApi } from '../../lib/circulation';
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, Panel, SelectField, StatusBadge, TextField } from './phase2Helpers';

export default function FinesPage() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState('');
  const [payments, setPayments] = useState<Record<string, string>>({});
  const borrowersQuery = useQuery({ queryKey: ['borrowers'], queryFn: () => circulationApi.listBorrowers() });
  const finesQuery = useQuery({ queryKey: ['fines', status], queryFn: () => circulationApi.listFines(status || undefined) });
  const payFine = useMutation({
    mutationFn: ({ fineId, amount }: { fineId: string; amount: number }) => circulationApi.payFine(fineId, amount),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['fines'] }),
  });
  const waiveFine = useMutation({
    mutationFn: circulationApi.waiveFine,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['fines'] }),
  });

  const borrowers = borrowersQuery.data ?? [];
  const fines = finesQuery.data ?? [];
  const borrowerName = (id: string) => {
    const borrower = borrowers.find((item) => item.id === id);
    return borrower ? `${borrower.first_name} ${borrower.last_name}` : id.slice(0, 8);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Fines" description="Collect payments, waive balances, and review fine status." />
      <Panel title="Filters">
        <div className="max-w-xs">
          <SelectField label="Status" value={status} onChange={setStatus}>
            <option value="">All fines</option>
            <option value="unpaid">Unpaid</option>
            <option value="paid">Paid</option>
            <option value="waived">Waived</option>
          </SelectField>
        </div>
      </Panel>

      <Panel title="Fine Register">
        {finesQuery.isLoading && <LoadingState />}
        {finesQuery.isError && <ErrorState message="Could not load fines." />}
        {!finesQuery.isLoading && !finesQuery.isError && fines.length === 0 && <EmptyState label="No fines recorded." />}
        {fines.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-obsidian-500 border-b border-obsidian-100">
                <tr>
                  <th className="py-2 pr-4 font-medium">Borrower</th>
                  <th className="py-2 pr-4 font-medium">Reason</th>
                  <th className="py-2 pr-4 font-medium">Amount</th>
                  <th className="py-2 pr-4 font-medium">Paid</th>
                  <th className="py-2 pr-4 font-medium">Status</th>
                  <th className="py-2 pr-4 font-medium">Payment</th>
                  <th className="py-2 pr-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-obsidian-100">
                {fines.map((fine) => (
                  <tr key={fine.id}>
                    <td className="py-3 pr-4 font-medium text-obsidian-900">{borrowerName(fine.borrower_id)}</td>
                    <td className="py-3 pr-4 text-obsidian-600">{fine.reason.replace('_', ' ')}</td>
                    <td className="py-3 pr-4 text-obsidian-600">{fine.amount}</td>
                    <td className="py-3 pr-4 text-obsidian-500">{fine.paid_amount}</td>
                    <td className="py-3 pr-4"><StatusBadge status={fine.status} /></td>
                    <td className="py-3 pr-4 min-w-32">
                      <TextField
                        label="Amount"
                        type="number"
                        min={0}
                        value={payments[fine.id] ?? ''}
                        onChange={(event) => setPayments({ ...payments, [fine.id]: event.target.value })}
                        disabled={fine.status !== 'unpaid'}
                      />
                    </td>
                    <td className="py-3 pr-4">
                      <div className="flex gap-2">
                        <Button
                          type="button"
                          size="sm"
                          leftIcon={<CreditCard size={14} />}
                          disabled={fine.status !== 'unpaid'}
                          onClick={() => payFine.mutate({ fineId: fine.id, amount: Number(payments[fine.id] || 0) })}
                        >
                          Pay
                        </Button>
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          disabled={fine.status !== 'unpaid'}
                          onClick={() => waiveFine.mutate(fine.id)}
                        >
                          Waive
                        </Button>
                      </div>
                    </td>
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
