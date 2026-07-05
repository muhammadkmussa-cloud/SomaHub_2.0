import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Sparkles, UserPlus } from 'lucide-react';
import { circulationApi } from '../../lib/circulation';
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, Panel, StatusBadge, TextField } from './phase2Helpers';

export default function BorrowersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', student_id: '' });
  const borrowersQuery = useQuery({ queryKey: ['borrowers'], queryFn: () => circulationApi.listBorrowers() });

  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  const handleScanID = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setIsScanning(true);
    setScanError(null);
    try {
      const result = await circulationApi.scanStudentID(file);
      const fullName = result.name || '';
      const parts = fullName.trim().split(/\s+/);
      const first_name = parts[0] || '';
      const last_name = parts.slice(1).join(' ') || '';
      setForm({
        first_name,
        last_name,
        email: form.email,
        phone: form.phone,
        student_id: result.student_id || '',
      });
    } catch (err: any) {
      setScanError(err.response?.data?.detail || 'OCR ID scan failed. Please enter details manually.');
    } finally {
      setIsScanning(false);
    }
  };

  const createBorrower = useMutation({
    mutationFn: circulationApi.createBorrower,
    onSuccess: () => {
      setForm({ first_name: '', last_name: '', email: '', phone: '', student_id: '' });
      void queryClient.invalidateQueries({ queryKey: ['borrowers'] });
    },
  });
  const suspendBorrower = useMutation({
    mutationFn: circulationApi.suspendBorrower,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['borrowers'] }),
  });

  const borrowers = borrowersQuery.data ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader title="Borrowers" description="Register borrowers, maintain contact details, and suspend access when needed." />
      <Panel title="Register Borrower">
        <div className="mb-4 max-w-xs">
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-obsidian-200 hover:border-emerald-400 rounded-lg p-4 cursor-pointer transition-colors bg-obsidian-50/50">
            <Sparkles size={24} className="text-emerald-500 animate-pulse mb-2" />
            <span className="text-xs font-semibold text-obsidian-700">Scan ID Card with AI OCR</span>
            <span className="text-[10px] text-obsidian-400 mt-1">Upload ID card to pre-fill</span>
            <input type="file" accept="image/*" onChange={handleScanID} className="hidden" disabled={isScanning} />
          </label>
          {isScanning && (
            <p className="text-xs text-emerald-600 mt-2 flex items-center gap-1.5 animate-pulse">
              <span className="h-2 w-2 rounded-full bg-emerald-500 inline-block animate-ping"></span>
              Scanning ID Card...
            </p>
          )}
          {scanError && (
            <p className="text-xs text-red-500 mt-2 font-medium">
              {scanError}
            </p>
          )}
        </div>
        <form
          className="grid grid-cols-1 md:grid-cols-6 gap-3 items-end"
          onSubmit={(event) => {
            event.preventDefault();
            createBorrower.mutate({
              first_name: form.first_name,
              last_name: form.last_name,
              email: form.email || undefined,
              phone: form.phone || undefined,
              student_id: form.student_id || undefined,
            });
          }}
        >
          <TextField label="First Name" value={form.first_name} onChange={(event) => setForm({ ...form, first_name: event.target.value })} required disabled={isScanning} />
          <TextField label="Last Name" value={form.last_name} onChange={(event) => setForm({ ...form, last_name: event.target.value })} required disabled={isScanning} />
          <TextField label="Email" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} disabled={isScanning} />
          <TextField label="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} disabled={isScanning} />
          <TextField label="Student ID" value={form.student_id} onChange={(event) => setForm({ ...form, student_id: event.target.value })} disabled={isScanning} />
          <Button type="submit" loading={createBorrower.isPending || isScanning} leftIcon={<UserPlus size={16} />}>Register</Button>
        </form>
      </Panel>

      <Panel title="Borrower List">
        {borrowersQuery.isLoading && <LoadingState />}
        {borrowersQuery.isError && <ErrorState message="Could not load borrowers." />}
        {!borrowersQuery.isLoading && !borrowersQuery.isError && borrowers.length === 0 && <EmptyState label="No borrowers registered." />}
        {borrowers.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-obsidian-500 border-b border-obsidian-100">
                <tr>
                  <th className="py-2 pr-4 font-medium">Name</th>
                  <th className="py-2 pr-4 font-medium">Email</th>
                  <th className="py-2 pr-4 font-medium">Student ID</th>
                  <th className="py-2 pr-4 font-medium">Status</th>
                  <th className="py-2 pr-4 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-obsidian-100">
                {borrowers.map((borrower) => (
                  <tr key={borrower.id}>
                    <td className="py-3 pr-4 font-medium text-obsidian-900">{borrower.first_name} {borrower.last_name}</td>
                    <td className="py-3 pr-4 text-obsidian-600">{borrower.email ?? '-'}</td>
                    <td className="py-3 pr-4 text-obsidian-500">{borrower.student_id ?? '-'}</td>
                    <td className="py-3 pr-4"><StatusBadge status={borrower.status} /></td>
                    <td className="py-3 pr-4">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        disabled={borrower.status === 'suspended'}
                        onClick={() => suspendBorrower.mutate(borrower.id)}
                      >
                        Suspend
                      </Button>
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
