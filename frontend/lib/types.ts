export type TradeOffSet = {
  pros: string[];
  cons: string[];
};

export type ComponentAlternative = {
  name: string;
  rejection_reason: string;
};

export type ComponentSummary = {
  id?: string | null;
  name: string;
  category: string;
  vendor?: string | null;
  features?: unknown[];
  icon_url?: string | null;
  sla?: string | null;
};

export type ComponentDecision = {
  category: string;
  selected: ComponentSummary;
  alternatives: ComponentAlternative[];
  rationale: string;
  trade_offs: TradeOffSet;
  estimated_monthly_cost_usd?: number | null;
};

export type JobPreviewResponse = {
  status: string;
  mermaid?: string | null;
  svg?: string | null;
  component_selections: Record<string, ComponentDecision>;
};

export type JobStatusResponse = {
  status: string;
  progress: number;
  current_step?: string | null;
  error_message?: string | null;
};
