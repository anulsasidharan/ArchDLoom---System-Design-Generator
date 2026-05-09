"use client";

import type { ComponentDecision } from "@/lib/types";
import { X } from "lucide-react";

type Props = {
  category: string | null;
  decision: ComponentDecision | null;
  onClose: () => void;
};

export function ComponentDetailPanel({ category, decision, onClose }: Props) {
  if (!category || !decision) return null;

  const cost = decision.estimated_monthly_cost_usd;
  const iconSrc =
    decision.selected.icon_url &&
    (decision.selected.icon_url.startsWith("http") ||
      decision.selected.icon_url.startsWith("/"))
      ? decision.selected.icon_url
      : null;

  return (
    <aside className="fixed right-4 top-4 z-50 w-full max-w-md rounded-xl border border-border bg-background/95 p-6 shadow-xl backdrop-blur-sm md:right-8 md:top-8">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{category}</p>
          <h3 className="text-xl font-semibold tracking-tight">{decision.selected.name}</h3>
          {decision.selected.vendor ? (
            <p className="text-sm text-muted-foreground">{decision.selected.vendor}</p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-md p-1 text-muted-foreground transition hover:bg-muted hover:text-foreground"
          aria-label="Close panel"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="mt-4 flex gap-4">
        {iconSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={iconSrc} alt="" className="h-14 w-14 shrink-0 rounded-md border bg-muted object-contain p-1" />
        ) : (
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-md border bg-muted text-xs text-muted-foreground">
            icon
          </div>
        )}
        <div className="min-w-0 flex-1 space-y-3 text-sm leading-relaxed">
          <div>
            <p className="font-medium text-foreground">Why this component</p>
            <p className="text-muted-foreground">{decision.rationale}</p>
          </div>
          {cost != null ? (
            <p className="text-sm">
              <span className="font-medium">Estimated cost</span>{" "}
              <span className="tabular-nums">${cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}/mo</span>
            </p>
          ) : null}
        </div>
      </div>

      <div className="mt-6 space-y-4 border-t pt-4">
        <div>
          <p className="mb-2 text-sm font-medium">Trade-offs</p>
          <ul className="space-y-1 text-sm">
            {decision.trade_offs.pros.map((p, i) => (
              <li key={`pro-${i}`} className="flex gap-2 text-emerald-800 dark:text-emerald-300">
                <span aria-hidden>✓</span>
                <span>{p}</span>
              </li>
            ))}
            {decision.trade_offs.cons.map((c, i) => (
              <li key={`con-${i}`} className="flex gap-2 text-amber-900 dark:text-amber-200">
                <span aria-hidden>⚠</span>
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="mb-2 text-sm font-medium">Alternatives considered</p>
          <ul className="space-y-2 text-sm text-muted-foreground">
            {decision.alternatives.map((alt, i) => (
              <li key={i}>
                <span className="font-medium text-foreground">{alt.name}</span>
                <span className="block text-xs">{alt.rejection_reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </aside>
  );
}
