import { describe, expect, it } from 'vitest';
import { getRoleDashboardPath, hasMinimumRole } from '../stores/authStore';

describe('authStore helpers', () => {
  it('routes readers to bookstore', () => {
    expect(getRoleDashboardPath('reader')).toBe('/dashboard/bookstore');
  });

  it('routes librarians to dashboard', () => {
    expect(getRoleDashboardPath('librarian')).toBe('/dashboard');
  });

  it('enforces role hierarchy', () => {
    expect(hasMinimumRole('library_admin', 'librarian')).toBe(true);
    expect(hasMinimumRole('reader', 'librarian')).toBe(false);
  });
});
