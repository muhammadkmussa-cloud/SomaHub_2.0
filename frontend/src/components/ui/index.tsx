import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

import type { ClassValue } from 'clsx';

// ── cn utility ────────────────────────────────────────────────────────────────
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(...inputs));
}


// ── Button ────────────────────────────────────────────────────────────────────
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const buttonVariants: Record<ButtonVariant, string> = {
  primary:   'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm hover:shadow-emerald-glow active:scale-[0.98]',
  secondary: 'bg-sapphire-600 hover:bg-sapphire-700 text-white shadow-sm active:scale-[0.98]',
  ghost:     'bg-transparent hover:bg-obsidian-100 text-obsidian-700 border border-transparent',
  danger:    'bg-red-600 hover:bg-red-700 text-white shadow-sm active:scale-[0.98]',
  outline:   'bg-transparent border border-obsidian-200 hover:border-emerald-400 text-obsidian-700 hover:text-emerald-700',
};

const buttonSizes: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading, leftIcon, rightIcon, children, className, disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
        buttonVariants[variant],
        buttonSizes[size],
        className,
      )}
      {...props}
    >
      {loading ? <Spinner size="sm" className="mr-1" /> : leftIcon}
      {children}
      {rightIcon}
    </button>
  ),
);
Button.displayName = 'Button';

// ── Spinner ───────────────────────────────────────────────────────────────────
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spinnerSizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' };

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <svg
      className={cn('animate-spin text-current', spinnerSizes[size], className)}
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

// ── Input ─────────────────────────────────────────────────────────────────────
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftAddon, rightAddon, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-obsidian-700">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftAddon && (
            <span className="absolute left-3 text-obsidian-400 flex items-center">{leftAddon}</span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-obsidian-900 placeholder-obsidian-400 transition-all duration-150',
              'focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400',
              error
                ? 'border-red-400 focus:ring-red-400'
                : 'border-obsidian-200 hover:border-obsidian-300',
              leftAddon ? 'pl-10' : '',
              rightAddon ? 'pr-10' : '',
              className,
            )}
            {...props}
          />
          {rightAddon && (
            <span className="absolute right-3 text-obsidian-400 flex items-center">{rightAddon}</span>
          )}
        </div>
        {error && <p className="text-xs text-red-600 flex items-center gap-1">⚠ {error}</p>}
        {helperText && !error && <p className="text-xs text-obsidian-400">{helperText}</p>}
      </div>
    );
  },
);
Input.displayName = 'Input';

// ── Badge ─────────────────────────────────────────────────────────────────────
type BadgeVariant = 'emerald' | 'sapphire' | 'warning' | 'danger' | 'neutral';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const badgeVariants: Record<BadgeVariant, string> = {
  emerald:  'bg-emerald-100 text-emerald-700',
  sapphire: 'bg-sapphire-100 text-sapphire-700',
  warning:  'bg-amber-100 text-amber-700',
  danger:   'bg-red-100 text-red-700',
  neutral:  'bg-obsidian-100 text-obsidian-600',
};

export function Badge({ variant = 'neutral', children, className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', badgeVariants[variant], className)}>
      {children}
    </span>
  );
}

// ── Card ──────────────────────────────────────────────────────────────────────
interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: boolean;
}

export function Card({ children, className, hover, padding = true }: CardProps) {
  return (
    <div className={cn(
      'bg-white rounded-xl border border-obsidian-100 shadow-card',
      hover && 'transition-shadow duration-200 hover:shadow-card-hover cursor-pointer',
      padding && 'p-6',
      className,
    )}>
      {children}
    </div>
  );
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className }: Pick<SkeletonProps, 'className'>) {
  return (
    <div
      className={cn(
        'bg-obsidian-100 rounded animate-shimmer',
        className,
      )}
      style={{
        backgroundImage: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.6) 50%, transparent 100%)',
        backgroundSize: '200% 100%',
      }}
    />
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn('h-4', i === lines - 1 ? 'w-3/4' : 'w-full')}
        />
      ))}
    </div>
  );
}

// ── Alert ─────────────────────────────────────────────────────────────────────
type AlertVariant = 'success' | 'error' | 'warning' | 'info';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: React.ReactNode;
  className?: string;
  onDismiss?: () => void;
}

const alertStyles: Record<AlertVariant, { wrapper: string; icon: string }> = {
  success: { wrapper: 'bg-emerald-50 border-emerald-200 text-emerald-800', icon: '✓' },
  error:   { wrapper: 'bg-red-50 border-red-200 text-red-800',             icon: '✕' },
  warning: { wrapper: 'bg-amber-50 border-amber-200 text-amber-800',       icon: '!' },
  info:    { wrapper: 'bg-sapphire-50 border-sapphire-200 text-sapphire-800', icon: 'i' },
};

export function Alert({ variant = 'info', title, children, className, onDismiss }: AlertProps) {
  const style = alertStyles[variant];
  return (
    <div className={cn('flex gap-3 p-4 rounded-lg border text-sm', style.wrapper, className)}>
      <span className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold bg-current/10">
        {style.icon}
      </span>
      <div className="flex-1 min-w-0">
        {title && <p className="font-semibold mb-0.5">{title}</p>}
        <p>{children}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="flex-shrink-0 text-current opacity-60 hover:opacity-100">
          ✕
        </button>
      )}
    </div>
  );
}
