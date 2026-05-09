"""Security architecture plan generator.

Builds a `SecurityPlan` from parsed requirements, component selections, and the
compliance posture. The plan is consumed by the HLD docx and the architecture.md
shared `_security` template.
"""

from __future__ import annotations

from app.domain.components import ArchitecturePattern, ComponentSelectionResult
from app.domain.enterprise import ComplianceMapping, SecurityPlan
from app.domain.requirements import ParsedRequirement


def _has_pii(req: ParsedRequirement, mapping: ComplianceMapping) -> bool:
    codes = {f.code for f in mapping.frameworks}
    return "GDPR" in codes or "HIPAA" in codes


def build_security_plan(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
    compliance: ComplianceMapping,
) -> SecurityPlan:
    """Compose a `SecurityPlan` covering the major control families."""
    has_pii = _has_pii(requirements, compliance)
    is_payments = any(f.code == "PCI-DSS" for f in compliance.frameworks)
    is_ai = requirements.has_ai_features or components.architecture_pattern in {
        ArchitecturePattern.RAG_SYSTEM,
        ArchitecturePattern.AGENTIC_AI_SYSTEM,
        ArchitecturePattern.REALTIME_INFERENCE,
        ArchitecturePattern.FINE_TUNING_PIPELINE,
    }

    authentication: list[str] = [
        "Single-sign-on at the edge with OIDC / SAML; short-lived session tokens (15 min) with refresh.",
        "Hardware-MFA enforced for administrative and break-glass identities.",
        "Workload identity (e.g. IAM roles for service accounts) instead of long-lived secrets.",
    ]
    if is_payments:
        authentication.append("Step-up authentication for high-risk actions (refunds, payouts, vault access).")
    if is_ai:
        authentication.append("Per-application API keys for LLM access; rotate on schedule and on incident.")

    authorization: list[str] = [
        "Coarse RBAC at the edge plus fine-grained ABAC on sensitive resources (per-tenant, per-record).",
        "Centralized policy decision point (e.g. OPA/Cedar) with policy-as-code reviews.",
        "Periodic access reviews tied to HRIS lifecycle events (joiner / mover / leaver).",
    ]
    if is_ai:
        authorization.append(
            "Tool-call allow-lists and per-tool quotas for any agentic or RAG retrieval surface."
        )

    encryption_at_rest: list[str] = [
        "AES-256 with managed KMS keys on databases, object storage, message brokers, and snapshots.",
        "Customer-managed keys (CMKs) for sensitive tenants where supported; rotate per policy (e.g. annual).",
        "Crypto-shredding tied to retention policy for deleted PII / PHI records.",
    ]

    encryption_in_transit: list[str] = [
        "TLS 1.2+ on all external endpoints; HSTS and modern cipher suites only.",
        "mTLS east-west between services in the private tier (service mesh or sidecar proxies).",
        "Database connections enforce TLS; reject plaintext explicitly in cluster parameter groups.",
    ]

    network_security: list[str] = [
        "VPC-private compute with public ingress only via WAF + load balancer.",
        "Per-tier security groups / NSGs; east-west allow-lists default-deny.",
        "Private endpoints (PrivateLink / VPC peering) for managed services where available.",
        "Egress via NAT / proxy with allow-listed external destinations and DNS firewalling.",
    ]
    if is_ai:
        network_security.append(
            "Outbound LLM/tool calls routed through an egress proxy with audit logging and content scanning."
        )

    secrets_management: list[str] = [
        "Centralized secret store (e.g. AWS Secrets Manager / HashiCorp Vault) with auto-rotation hooks.",
        "No long-lived credentials in code or images; CI uses short-lived OIDC tokens.",
        "Sealed-secrets / SOPS for declarative manifests; secrets never logged or echoed.",
    ]

    audit_logging: list[str] = [
        "Centralized, tamper-evident logs for control-plane and data-plane events with 1+ year retention.",
        "Structured audit events for authentication, authorization, secret access, and data export.",
        "Immutable storage tier (object lock / WORM) for forensic-grade evidence on regulated subsets.",
    ]
    if has_pii:
        audit_logging.append("PII / PHI access logged with subject identifier hashing for replay forensics.")

    application_security: list[str] = [
        "Threat modeling on every new bounded context and on major changes to trust boundaries.",
        "Static analysis (SAST), dependency scanning, and container scanning gating CI.",
        "Annual external penetration test plus targeted reviews on high-risk surfaces.",
        "Runtime defense: WAF, bot management, request signing for sensitive write paths.",
    ]
    if is_ai:
        application_security.append(
            "Prompt-injection mitigations: input sanitization, retrieval allow-lists, output safety filters."
        )

    data_protection: list[str] = [
        "Data classification (Public / Internal / Confidential / Restricted) with tagging in storage.",
        "DLP scanning on egress (email, S3 share links, support tooling).",
        "Synthetic / masked data in non-prod environments; refreshes audited.",
    ]
    if has_pii:
        data_protection.append(
            "Subject-rights tooling: export / delete / rectify endpoints with SLA tracking."
        )
    if is_payments:
        data_protection.append(
            "PAN tokenized at the edge or via hosted vault; CDE network segmentation enforced."
        )

    iam_principles: list[str] = [
        "Least privilege, just-in-time elevation, and break-glass procedures with full session recording.",
        "Separation of duties between deploy, data access, and security review roles.",
        "Federated identity for humans; per-workload identity for services — no shared accounts.",
    ]

    threat_model_notes: list[str] = [
        "Adopt STRIDE per bounded context; track residual risk in a risk register reviewed quarterly.",
        "Monitor OWASP Top 10 + CWE Top 25 coverage in CI.",
    ]
    if is_ai:
        threat_model_notes.append(
            "Track OWASP LLM Top 10 (prompt injection, model DoS, data exfiltration via tools)."
        )
    if components.architecture_pattern == ArchitecturePattern.AGENTIC_AI_SYSTEM:
        threat_model_notes.append(
            "Agentic systems: explicit tool allow-list, sandboxing, and per-tool max-cost caps."
        )

    return SecurityPlan(
        authentication=authentication,
        authorization=authorization,
        encryption_at_rest=encryption_at_rest,
        encryption_in_transit=encryption_in_transit,
        network_security=network_security,
        secrets_management=secrets_management,
        audit_logging=audit_logging,
        application_security=application_security,
        data_protection=data_protection,
        iam_principles=iam_principles,
        threat_model_notes=threat_model_notes,
    )
