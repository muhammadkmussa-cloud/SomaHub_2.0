import api from './api';

export interface Book {
  id: string;
  tenant_id: string;
  isbn?: string | null;
  title: string;
  author: string;
  publisher?: string | null;
  publication_year?: number | null;
  category?: string | null;
  total_copies: number;
  available_copies: number;
  created_at: string;
  updated_at: string;
}

export interface BookCopy {
  id: string;
  tenant_id: string;
  book_id: string;
  barcode: string;
  location?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Borrower {
  id: string;
  tenant_id: string;
  first_name: string;
  last_name: string;
  email?: string | null;
  phone?: string | null;
  student_id?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Loan {
  id: string;
  tenant_id: string;
  borrower_id: string;
  book_copy_id: string;
  issued_by_user_id: string;
  due_date: string;
  status: string;
  issued_at: string;
  returned_at?: string | null;
}

export interface Fine {
  id: string;
  tenant_id: string;
  borrower_id: string;
  loan_id?: string | null;
  reason: string;
  amount: string;
  paid_amount: string;
  status: string;
  created_at: string;
}

export const circulationApi = {
  listBooks: async (search?: string) => {
    const { data } = await api.get<Book[]>('/books', { params: search ? { search } : undefined });
    return data;
  },
  createBook: async (payload: Partial<Book> & { title: string; author: string; total_copies: number }) => {
    const { data } = await api.post<Book>('/books', payload);
    return data;
  },
  listCopies: async (params?: { book_id?: string; status?: string }) => {
    const { data } = await api.get<BookCopy[]>('/book-copies', { params });
    return data;
  },
  createCopy: async (payload: { book_id: string; barcode: string; location?: string }) => {
    const { data } = await api.post<BookCopy>('/book-copies', payload);
    return data;
  },
  listBorrowers: async (search?: string) => {
    const { data } = await api.get<Borrower[]>('/borrowers', { params: search ? { search } : undefined });
    return data;
  },
  createBorrower: async (payload: {
    first_name: string;
    last_name: string;
    email?: string;
    phone?: string;
    student_id?: string;
  }) => {
    const { data } = await api.post<Borrower>('/borrowers', payload);
    return data;
  },
  suspendBorrower: async (borrowerId: string) => {
    const { data } = await api.post<Borrower>(`/borrowers/${borrowerId}/suspend`);
    return data;
  },
  listLoans: async (status?: string) => {
    const { data } = await api.get<Loan[]>('/loans', { params: status ? { status } : undefined });
    return data;
  },
  issueLoan: async (payload: { borrower_id: string; book_copy_id: string; due_date: string }) => {
    const { data } = await api.post<Loan>('/loans', payload);
    return data;
  },
  returnLoan: async (loanId: string) => {
    const { data } = await api.post<Loan>(`/loans/${loanId}/return`);
    return data;
  },
  markLost: async (loanId: string) => {
    const { data } = await api.post<Loan>(`/loans/${loanId}/lost`);
    return data;
  },
  listFines: async (status?: string) => {
    const { data } = await api.get<Fine[]>('/fines', { params: status ? { status } : undefined });
    return data;
  },
  payFine: async (fineId: string, amount: number) => {
    const { data } = await api.post<Fine>(`/fines/${fineId}/pay`, { amount });
    return data;
  },
  waiveFine: async (fineId: string) => {
    const { data } = await api.post<Fine>(`/fines/${fineId}/waive`);
    return data;
  },
};
