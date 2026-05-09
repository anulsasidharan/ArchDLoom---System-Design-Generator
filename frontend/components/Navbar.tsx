"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Layers, Menu, X } from "lucide-react";
import { useState } from "react";

const NAV_LINKS = [
  { href: "/generate", label: "Generate" },
  { href: "/projects", label: "Projects" },
  { href: "/library", label: "Components" },
];

export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-md">
      <nav
        className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6"
        aria-label="Main navigation"
      >
        <Link
          href="/"
          className="flex items-center gap-2.5 text-foreground transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
          aria-label="ArchDLoom home"
        >
          <Layers className="h-5 w-5 text-green-400" aria-hidden />
          <span className="font-semibold tracking-tight">ArchDLoom</span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                pathname.startsWith(link.href)
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Link
            href="/generate"
            className="rounded-md bg-green-500 px-4 py-1.5 text-sm font-semibold text-slate-950 transition hover:bg-green-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring glow-green-sm"
          >
            Start Designing
          </Link>
        </div>

        <button
          type="button"
          className="rounded-md p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X className="h-5 w-5" aria-hidden /> : <Menu className="h-5 w-5" aria-hidden />}
        </button>
      </nav>

      {open && (
        <div className="border-t border-border/60 bg-background/95 px-4 pb-4 pt-2 md:hidden">
          <ul className="space-y-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    pathname.startsWith(link.href)
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            <li className="pt-2">
              <Link
                href="/generate"
                onClick={() => setOpen(false)}
                className="block rounded-md bg-green-500 px-3 py-2 text-center text-sm font-semibold text-slate-950 hover:bg-green-400"
              >
                Start Designing
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
