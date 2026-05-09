"use client";

import { useState } from "react";
import { Download, FileText, GitBranch, Layers, Network, TrendingUp, Package, CheckCircle2 } from "lucide-react";

const FILES = [
  { key: "prd", name: "Product Requirements Document", ext: ".docx", icon: FileText, color: "text-blue-400" },
  { key: "hld", name: "High-Level Design", ext: ".docx", icon: Network, color: "text-purple-400" },
  { key: "lld", name: "Low-Level Design", ext: ".docx", icon: Layers, color: "text-orange-400" },
  { key: "evolution", name: "Evolution Roadmap", ext: ".md", icon: TrendingUp, color: "text-green-400" },
  { key: "architecture", name: "Architecture Diagram", ext: ".md + .svg", icon: GitBranch, color: "text-cyan-400" },
];

type DownloadState = "idle" | "loading" | "success" | "error";

type Props = {
  jobId: string;
  apiBase: string;
};

export function DownloadPanel({ jobId, apiBase }: Props) {
  const [state, setState] = useState<DownloadState>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleDownloadAll = async () => {
    setState("loading");
    setErrorMsg(null);
    try {
      const res = await fetch(`${apiBase}/jobs/${jobId}/download`);
      if (!res.ok) throw new Error(`Download failed: ${res.statusText}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `archdloom-${jobId.slice(0, 8)}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setState("success");
      setTimeout(() => setState("idle"), 4000);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Download failed");
      setState("error");
    }
  };

  return (
    <div className="rounded-xl border border-border/60 bg-card p-6 space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-foreground">Export Package</p>
          <p className="text-xs text-muted-foreground mt-0.5">5 documents ready to download</p>
        </div>
        <Package className="h-5 w-5 text-muted-foreground shrink-0" aria-hidden />
      </div>

      <ul className="space-y-2" role="list" aria-label="Generated files">
        {FILES.map((file) => {
          const Icon = file.icon;
          return (
            <li
              key={file.key}
              className="flex items-center gap-3 rounded-lg border border-border/40 bg-muted/20 px-3 py-2.5"
            >
              <Icon className={`h-4 w-4 shrink-0 ${file.color}`} aria-hidden />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-foreground truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">{file.ext}</p>
              </div>
              {state === "success" && (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-green-400" aria-label="Downloaded" />
              )}
            </li>
          );
        })}
      </ul>

      {errorMsg && (
        <p className="text-xs text-destructive" role="alert">
          {errorMsg}
        </p>
      )}

      <button
        type="button"
        onClick={handleDownloadAll}
        disabled={state === "loading"}
        aria-busy={state === "loading"}
        aria-disabled={state === "loading"}
        className={`flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
          state === "success"
            ? "bg-green-500/20 border border-green-500/30 text-green-400 cursor-default"
            : state === "loading"
            ? "bg-muted text-muted-foreground cursor-wait"
            : "bg-green-500 text-slate-950 hover:bg-green-400 glow-green-sm"
        }`}
      >
        {state === "loading" ? (
          <>
            <span className="h-4 w-4 rounded-full border-2 border-muted-foreground border-t-transparent animate-spin" aria-hidden />
            Preparing ZIP…
          </>
        ) : state === "success" ? (
          <>
            <CheckCircle2 className="h-4 w-4" aria-hidden />
            Downloaded!
          </>
        ) : (
          <>
            <Download className="h-4 w-4" aria-hidden />
            Download All (.zip)
          </>
        )}
      </button>

      <p className="text-center text-xs text-muted-foreground">
        ZIP includes all 5 files · Generated for job{" "}
        <code className="rounded bg-muted px-1 font-mono">{jobId.slice(0, 8)}</code>
      </p>
    </div>
  );
}
