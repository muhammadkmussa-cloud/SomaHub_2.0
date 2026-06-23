import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
  },
  webServer: [
    {
      command:
        'cd ../backend && APP_ENV=testing DATABASE_URL=sqlite+aiosqlite:///./e2e.db SECRET_KEY=e2e-secret-key-not-for-production-12345678901234567890 PYTHONPATH=. uv run python scripts/seed_e2e.py && APP_ENV=testing DATABASE_URL=sqlite+aiosqlite:///./e2e.db SECRET_KEY=e2e-secret-key-not-for-production-12345678901234567890 PYTHONPATH=. uv run uvicorn app.main:app --host 127.0.0.1 --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: 'npm run dev -- --host --port 5173',
      port: 5173,
      reuseExistingServer: !process.env.CI,
      env: {
        VITE_API_URL: 'http://localhost:8000/api/v1',
      },
    },
  ],
});
