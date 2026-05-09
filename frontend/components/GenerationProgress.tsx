"use client";

import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import type { JobStatusResponse } from "@/lib/types";

const STEPS = [
  { key: "parsing", label: "Parsing requirements", description: "Extracting scale, domain, and NFRs" },
  { key: "selecting", label: "Selecting components", description: "Scoring and ranking with trade-offs" },
  { key: "generating", label: "Generating documents", description: "PRD · HLD · LLD · Evolution plan" },
  { key: "packaging", label: "Packaging artifacts", description: "Diagrams, ZIP, and preview data" },
];

function stepIndex(currentStep: string | null | undefined): number {
  if (!currentStep) return 0;
  const lower = currentStep.toLowerCase();
  if (lower.includes("packag") || lower.includes("zip") || lower.includes("diagram")) return 3;
  if (lower.includes("generat") || lower.includes("document") || lower.includes("hld") || lower.includes("lld") || lower.includes("prd")) return 2;
  if (lower.includes("select") || lower.includes("component")) return 1;
  return 0;
}

type Props = {
  status: JobStatusResponse;
};

export function GenerationProgress({ status }: Props) {
  const isCompleted = status.status === "completed";
  const isFailed = status.status === "failed";
  const activeStep = isCompleted ? STEPS.length : stepIndex(status.current_step);
  const progress = status.progress ?? 0;

  return (
    <div className="rounded-xl border border-border/60 bg-card p-6 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-foreground">
            {isCompleted
              ? "Generation complete"
              : isFailed
              ? "Generation failed"
              : "Generating your architecture…"}
          </p>
          {status.current_step && !isCompleted && !isFailed && (
            <p className="mt-0.5 text-xs text-muted-foreground">{status.current_step}</p>
          )}
        </div>
        <div className="shrink-0 tabular-nums text-sm font-semibold text-green-400">
          {isCompleted ? "100%" : isFailed ? "—" : `${progress}%`}
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted" role="progressbar" aria-valuenow={isCompleted ? 100 : progress} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${isFailed ? "bg-destructive" : "bg-green-500"}`}
          style={{ width: `${isCompleted ? 100 : progress}%` }}
        />
      </div>

      {/* Step indicators */}
      <ol className="grid gap-3 sm:grid-cols-2" role="list">
        {STEPS.map((step, i) => {
          const done = isCompleted || i < activeStep;
          const active = !isCompleted && !isFailed && i === activeStep;
          const pending = !done && !active;

          return (
            <li
              key={step.key}
              className={`flex items-start gap-3 rounded-lg border p-3 transition-colors ${
                done
                  ? "border-green-500/20 bg-green-500/5"
                  : active
                  ? "border-border bg-muted/40"
                  : "border-border/40 bg-transparent opacity-50"
              }`}
            >
              <span className="mt-0.5 shrink-0">
                {done ? (
                  <CheckCircle2 className="h-4 w-4 text-green-400" aria-label="Completed" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 animate-spin text-green-400" aria-label="In progress" />
                ) : (
                  <Circle className="h-4 w-4 text-muted-foreground/40" aria-label="Pending" />
                )}
              </span>
              <div className="min-w-0">
                <p className={`text-xs font-medium ${done || active ? "text-foreground" : "text-muted-foreground"}`}>
                  {step.label}
                </p>
                <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
              </div>
            </li>
          );
        })}
      </ol>

      {isFailed && status.error_message && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3">
          <p className="text-sm text-destructive">{status.error_message}</p>
        </div>
      )}
    </div>
  );
}

export function GenerationProgressSkeleton() {
  return (
    <div className="rounded-xl border border-border/60 bg-card p-6 space-y-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="space-y-1.5">
          <div className="skeleton h-4 w-40 rounded" />
          <div className="skeleton h-3 w-28 rounded" />
        </div>
        <div className="skeleton h-5 w-12 rounded" />
      </div>
      <div className="skeleton h-1.5 w-full rounded-full" />
      <div className="grid gap-3 sm:grid-cols-2">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="rounded-lg border border-border/40 p-3 flex gap-3">
            <div className="skeleton h-4 w-4 rounded-full shrink-0 mt-0.5" />
            <div className="flex-1 space-y-1.5">
              <div className="skeleton h-3 w-24 rounded" />
              <div className="skeleton h-3 w-32 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
