import type { InputHTMLAttributes, ReactNode } from 'react';
import { Alert, Badge, Button, Card, Input, Spinner, cn } from '../../components/ui';

export function PageHeader({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-display font-bold text-obsidian-900">{title}</h1>
        <p className="text-sm text-obsidian-500 mt-1">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const variant = status === 'active' || status === 'available' || status === 'paid' || status === 'returned'
    ? 'emerald'
    : status === 'issued' || status === 'loaned'
      ? 'sapphire'
      : status === 'overdue' || status === 'unpaid'
        ? 'warning'
        : 'danger';
  return <Badge variant={variant}>{status.replace('_', ' ')}</Badge>;
}

export function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <h2 className="font-display font-semibold text-obsidian-800 mb-4">{title}</h2>
      {children}
    </Card>
  );
}

export function EmptyState({ label }: { label: string }) {
  return (
    <div className="text-center py-10 text-sm text-obsidian-500">
      {label}
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="flex justify-center py-10 text-obsidian-500">
      <Spinner />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return <Alert variant="error">{message}</Alert>;
}

export function TextField(props: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return <Input {...props} className={cn('h-10', props.className)} />;
}

export function SelectField({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: ReactNode;
}) {
  const id = label.toLowerCase().replace(/\s+/g, '-');
  return (
    <label className="flex flex-col gap-1 text-sm font-medium text-obsidian-700" htmlFor={id}>
      {label}
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-10 rounded-lg border border-obsidian-200 bg-white px-3 text-sm text-obsidian-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
      >
        {children}
      </select>
    </label>
  );
}

export { Button };
