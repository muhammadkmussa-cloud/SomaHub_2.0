import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ShoppingBag, Edit, Trash } from 'lucide-react';
import { ebooksApi, resolveUploadUrl } from '../../lib/ebooks';
import type { Ebook } from '../../lib/ebooks';
import { Badge, Button, Card } from '../../components/ui';
import { EmptyState, ErrorState, LoadingState, PageHeader, Panel, TextField, SelectField } from './phase2Helpers';
import { useAuthStore } from '../../stores/authStore';
import { useState } from 'react';

export default function BookstorePage() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const isSuperAdmin = user?.role === 'super_admin';

  const ebooksQuery = useQuery({ queryKey: ['ebooks'], queryFn: ebooksApi.list });
  const libraryQuery = useQuery({ queryKey: ['my-library'], queryFn: ebooksApi.myLibrary, enabled: !isSuperAdmin });

  // Form State
  const [form, setForm] = useState({
    title: '',
    author: '',
    description: '',
    category: '',
    price: 0,
    cover_url: '',
    file_url: '',
    status: 'draft',
  });
  
  const [editingEbookId, setEditingEbookId] = useState<string | null>(null);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Mutations
  const checkout = useMutation({
    mutationFn: ebooksApi.checkoutFree,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['my-library'] });
      void queryClient.invalidateQueries({ queryKey: ['ebooks'] });
    },
  });

  const createEbook = useMutation({
    mutationFn: ebooksApi.create,
    onSuccess: () => {
      resetForm();
      void queryClient.invalidateQueries({ queryKey: ['ebooks'] });
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to create ebook.');
    }
  });

  const updateEbook = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Ebook> }) => ebooksApi.update(id, data),
    onSuccess: () => {
      resetForm();
      void queryClient.invalidateQueries({ queryKey: ['ebooks'] });
    },
    onError: (err: any) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to update ebook.');
    }
  });

  const deleteEbook = useMutation({
    mutationFn: ebooksApi.delete,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['ebooks'] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Failed to delete ebook.');
    }
  });

  const resetForm = () => {
    setForm({
      title: '',
      author: '',
      description: '',
      category: '',
      price: 0,
      cover_url: '',
      file_url: '',
      status: 'draft',
    });
    setEditingEbookId(null);
    setErrorMsg(null);
  };

  const handleEditClick = (ebook: Ebook) => {
    setEditingEbookId(ebook.id);
    setForm({
      title: ebook.title,
      author: ebook.author,
      description: ebook.description || '',
      category: ebook.category || '',
      price: ebook.price,
      cover_url: ebook.cover_url || '',
      file_url: ebook.file_url || '',
      status: ebook.status,
    });
    setErrorMsg(null);
  };

  const handleCoverUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadingCover(true);
    setErrorMsg(null);
    try {
      const result = await ebooksApi.uploadCover(file);
      setForm((prev) => ({ ...prev, cover_url: result.url }));
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to upload cover.');
    } finally {
      setUploadingCover(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadingFile(true);
    setErrorMsg(null);
    try {
      const result = await ebooksApi.uploadFile(file);
      setForm((prev) => ({ ...prev, file_url: result.url }));
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to upload file.');
    } finally {
      setUploadingFile(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.title.trim() || !form.author.trim()) {
      setErrorMsg('Title and Author are required.');
      return;
    }
    
    if (editingEbookId) {
      updateEbook.mutate({ id: editingEbookId, data: form });
    } else {
      createEbook.mutate(form);
    }
  };

  if (ebooksQuery.isLoading) return <LoadingState />;
  if (ebooksQuery.isError) return <ErrorState message="Failed to load ebooks." />;

  const ownedIds = new Set((libraryQuery.data ?? []).map((p: { ebook_id: string }) => p.ebook_id));
  const ebooks = ebooksQuery.data ?? [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader 
        title={isSuperAdmin ? "Bookstore Management" : "Bookstore"} 
        description={isSuperAdmin ? "Upload and manage digital books in the bookstore." : "Browse and purchase digital books."} 
      />

      <div className={isSuperAdmin ? "grid grid-cols-1 lg:grid-cols-3 gap-6" : "space-y-6"}>
        {isSuperAdmin && (
          <div className="lg:col-span-1 space-y-4">
            <Panel title={editingEbookId ? "Edit Ebook" : "Upload Ebook"}>
              {errorMsg && <ErrorState message={errorMsg} />}
              <form onSubmit={handleSubmit} className="space-y-4">
                <TextField 
                  label="Title" 
                  value={form.title} 
                  onChange={(e) => setForm({ ...form, title: e.target.value })} 
                  required 
                />
                <TextField 
                  label="Author" 
                  value={form.author} 
                  onChange={(e) => setForm({ ...form, author: e.target.value })} 
                  required 
                />
                <div className="flex flex-col gap-1 text-sm font-medium text-obsidian-700">
                  <span className="text-sm font-medium text-obsidian-700">Description</span>
                  <textarea
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="w-full rounded-lg border border-obsidian-200 px-3 py-2 text-sm text-obsidian-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
                    rows={3}
                  />
                </div>
                <TextField 
                  label="Category" 
                  value={form.category} 
                  onChange={(e) => setForm({ ...form, category: e.target.value })} 
                />
                <TextField 
                  label="Price ($)" 
                  type="number" 
                  step="0.01" 
                  min="0"
                  value={form.price} 
                  onChange={(e) => setForm({ ...form, price: Number(e.target.value) })} 
                />

                <div className="space-y-2">
                  <label className="flex flex-col gap-1 text-sm font-medium text-obsidian-700">
                    Cover Image
                    <input 
                      type="file" 
                      accept="image/*" 
                      onChange={handleCoverUpload} 
                      className="text-xs text-obsidian-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
                    />
                  </label>
                  {uploadingCover && <p className="text-xs text-emerald-600 animate-pulse">Uploading cover...</p>}
                  {form.cover_url && (
                    <div className="relative w-16 h-20 rounded border overflow-hidden">
                      <img src={form.cover_url} alt="Cover preview" className="w-full h-full object-cover" />
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="flex flex-col gap-1 text-sm font-medium text-obsidian-700">
                    Ebook File (PDF/EPUB)
                    <input 
                      type="file" 
                      accept=".pdf,.epub" 
                      onChange={handleFileUpload} 
                      className="text-xs text-obsidian-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
                    />
                  </label>
                  {uploadingFile && <p className="text-xs text-emerald-600 animate-pulse">Uploading file...</p>}
                  {form.file_url && <p className="text-xs text-emerald-700 truncate">✓ File uploaded: {form.file_url.split('/').pop()}</p>}
                </div>

                <SelectField 
                  label="Status" 
                  value={form.status} 
                  onChange={(val) => setForm({ ...form, status: val })}
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </SelectField>

                <div className="flex gap-2 pt-2">
                  <Button 
                    type="submit" 
                    loading={createEbook.isPending || updateEbook.isPending} 
                    className="flex-1"
                  >
                    {editingEbookId ? "Update Ebook" : "Upload Ebook"}
                  </Button>
                  {editingEbookId && (
                    <Button 
                      type="button" 
                      variant="secondary" 
                      onClick={resetForm}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </form>
            </Panel>
          </div>
        )}

        <div className={isSuperAdmin ? "lg:col-span-2 space-y-4" : "space-y-6"}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ebooks.map((ebook) => (
              <Card key={ebook.id} className="flex flex-col justify-between gap-3 h-full">
                {/* Cover thumbnail */}
                {ebook.cover_url && (
                  <img
                    src={resolveUploadUrl(ebook.cover_url) ?? ''}
                    alt={ebook.title}
                    className="w-full h-36 object-cover rounded-md border border-obsidian-100 bg-obsidian-50"
                  />
                )}
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      {isSuperAdmin ? (
                        <span className="font-display font-semibold text-obsidian-900 block truncate">
                          {ebook.title}
                        </span>
                      ) : (
                        <Link to={`/dashboard/bookstore/${ebook.id}`} className="font-display font-semibold text-obsidian-900 hover:text-emerald-600 block truncate">
                          {ebook.title}
                        </Link>
                      )}
                      <p className="text-sm text-obsidian-500 truncate">{ebook.author}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1.5 shrink-0">
                      <Badge variant={ebook.price === 0 ? 'emerald' : 'sapphire'}>
                        {ebook.price === 0 ? 'Free' : `$${ebook.price.toFixed(2)}`}
                      </Badge>
                      {isSuperAdmin && (
                        <Badge variant={ebook.status === 'published' ? 'emerald' : ebook.status === 'draft' ? 'warning' : 'danger'}>
                          {ebook.status}
                        </Badge>
                      )}
                    </div>
                  </div>
                  {ebook.description && (
                    <p className="text-sm text-obsidian-600 line-clamp-3">{ebook.description}</p>
                  )}
                </div>

                <div className="pt-2 border-t border-obsidian-50">
                  {isSuperAdmin ? (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        leftIcon={<Edit size={14} />}
                        onClick={() => handleEditClick(ebook)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        leftIcon={<Trash size={14} />}
                        loading={deleteEbook.isPending && deleteEbook.variables === ebook.id}
                        onClick={() => {
                          if (confirm(`Are you sure you want to delete "${ebook.title}"?`)) {
                            deleteEbook.mutate(ebook.id);
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  ) : ownedIds.has(ebook.id) ? (
                    <Badge variant="emerald" className="w-full text-center py-1">In your library</Badge>
                  ) : ebook.price === 0 ? (
                    <Button
                      size="sm"
                      className="w-full"
                      loading={checkout.isPending}
                      leftIcon={<ShoppingBag size={16} />}
                      onClick={() => checkout.mutate(ebook.id)}
                    >
                      Add to library
                    </Button>
                  ) : (
                    <p className="text-xs text-obsidian-400">Paid checkout via billing (Stripe/Paystack)</p>
                  )}
                </div>
              </Card>
            ))}
          </div>

          {ebooks.length === 0 && <EmptyState label="No ebooks published yet." />}
        </div>
      </div>
    </div>
  );
}
