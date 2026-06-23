import { describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { ProtectedRoute } from '../router/ProtectedRoute';
import { useAuthStore } from '../stores/authStore';

function StaffOnly() {
  return <div>Staff content</div>;
}

describe('ProtectedRoute', () => {
  it('redirects readers away from staff routes', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      user: { userId: 'u1', role: 'reader', tenantId: 't1' },
      accessToken: 'token',
    });

    render(
      <MemoryRouter initialEntries={['/staff']}>
        <Routes>
          <Route element={<ProtectedRoute allowedRoles={['librarian', 'library_admin']} />}>
            <Route path="/staff" element={<StaffOnly />} />
          </Route>
          <Route path="/unauthorized" element={<div>Unauthorized</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Unauthorized')).toBeInTheDocument();
  });
});
