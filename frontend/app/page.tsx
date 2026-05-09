import { Button } from "@/components/ui/button";

export default function HomePage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 px-6 py-24">
      <div className="space-y-3">
        <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">ArchDLoom · Phase 1 shell</p>
        <h1 className="text-balance font-serif text-4xl font-semibold tracking-tight sm:text-5xl">
          Weaving enterprise-grade system designs
        </h1>
        <p className="text-lg text-muted-foreground">
          Next.js 14 · Tailwind · shadcn/ui base wired to consume the FastAPI backend at{" "}
          <code className="rounded bg-muted px-1.5 py-0.5 text-sm">{apiUrl}</code>.
        </p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button asChild>
          <a href={`${apiUrl}/docs`} target="_blank" rel="noopener noreferrer">
            Open API docs
          </a>
        </Button>
        <Button variant="outline" asChild>
          <a href="/generate">Open generation & diagram preview</a>
        </Button>
      </div>
    </main>
  );
}
