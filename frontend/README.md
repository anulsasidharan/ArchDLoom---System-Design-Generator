# Frontend Workspace

Next.js 14 (App Router), TypeScript, Tailwind CSS, and shadcn/ui base (`components/ui/button`, `lib/utils`).

## Commands

From the repository root (npm workspaces):

```bash
npm install
npm run dev:frontend
```

Or from this directory:

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_URL` if the API is not on `http://localhost:8000`.

## Layout

- `app/` — App Router (`layout.tsx`, `page.tsx`, `globals.css`)
- `components/ui/` — shadcn-style primitives
- `lib/` — Shared utilities (e.g. `cn()`)
- `public/` — Static assets
