import api from './api';

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  library_type?: string;
  is_active: boolean;
  plan: string;
}

export const tenantsApi = {
  list: async () => (await api.get<Tenant[]>('/tenants')).data,
  update: async (id: string, data: Partial<Tenant>) =>
    (await api.patch(`/tenants/${id}`, data)).data,
};
