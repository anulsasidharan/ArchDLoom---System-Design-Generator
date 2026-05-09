"""High-Level Design Word document: logical architecture and cross-cutting concerns."""

from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from app.domain.components import ComponentSelectionResult
from app.domain.requirements import ParsedRequirement
from app.services.jinja_env import render_template


def generate_hld_docx(
    requirements: ParsedRequirement,
    components: ComponentSelectionResult,
    *,
    project_title: str | None = None,
    diagram_png: bytes | None = None,
) -> bytes:
    title = project_title or requirements.system_name
    doc = Document()

    h0 = doc.add_heading(f"{title} — High-Level Design", 0)
    h0.alignment = WD_ALIGN_PARAGRAPH.CENTER

    total = components.total_monthly_cost_usd
    preamble = render_template(
        "documents/hld_preamble.md.j2",
        project_title=title,
        domain=requirements.domain,
        pattern=components.architecture_pattern.value,
        total_cost=total,
        has_ai=requirements.has_ai_features,
    )
    for block in preamble.split("\n\n"):
        line = block.strip()
        if line:
            doc.add_paragraph(line)

    doc.add_heading("1. System context", 1)
    doc.add_paragraph(
        requirements.summary
        or f"{requirements.system_name} operates in the {requirements.domain} domain "
        f"with {len(requirements.functional_requirements)} major functional areas."
    )
    sm = requirements.scale_metrics
    scale_bits = []
    if sm.daily_active_users is not None:
        scale_bits.append(f"Daily active users (signal): ~{sm.daily_active_users:,}")
    if sm.peak_requests_per_second is not None:
        scale_bits.append(f"Peak RPS (signal): ~{sm.peak_requests_per_second}")
    if sm.data_volume_gb is not None:
        scale_bits.append(f"Data volume (signal): ~{sm.data_volume_gb} GB")
    if scale_bits:
        for b in scale_bits:
            doc.add_paragraph(b, style="List Bullet")
    else:
        doc.add_paragraph(
            "Quantitative scale signals were not specified — validate DAU, peak traffic, "
            "and data growth before production sizing."
        )

    doc.add_heading("2. Logical architecture", 1)
    if diagram_png:
        doc.add_picture(BytesIO(diagram_png), width=Inches(6.2))
        doc.add_paragraph()
    doc.add_paragraph(
        f"The selected pattern is **{components.architecture_pattern.value}**. "
        "Components below map to deployable or managed services; boundaries align with "
        "failure isolation and team ownership where applicable."
    )

    doc.add_heading("3. Component decisions", 1)
    for key, decision in sorted(components.selections.items(), key=lambda x: x[0]):
        doc.add_heading(f"{decision.selected.name} ({key})", 2)
        p = doc.add_paragraph()
        p.add_run("Category: ").bold = True
        p.add_run(decision.selected.category)
        if decision.selected.vendor:
            p = doc.add_paragraph()
            p.add_run("Vendor: ").bold = True
            p.add_run(decision.selected.vendor)
        doc.add_paragraph(decision.rationale or "Selected via library scoring and requirement fit.")
        if decision.estimated_monthly_cost_usd is not None:
            doc.add_paragraph(
                f"Indicative monthly cost (baseline): ${decision.estimated_monthly_cost_usd:,.0f}"
            )
        if decision.trade_offs.pros:
            doc.add_paragraph("Advantages:", style="Heading 3")
            for pro in decision.trade_offs.pros:
                doc.add_paragraph(pro, style="List Bullet")
        if decision.trade_offs.cons:
            doc.add_paragraph("Limitations:", style="Heading 3")
            for con in decision.trade_offs.cons:
                doc.add_paragraph(con, style="List Bullet")
        if decision.alternatives:
            doc.add_paragraph("Alternatives considered:", style="Heading 3")
            for alt in decision.alternatives[:5]:
                doc.add_paragraph(
                    f"{alt.name}: {alt.rejection_reason}",
                    style="List Bullet",
                )

    doc.add_heading("4. Request and data flows", 1)
    doc.add_paragraph(
        "Typical synchronous path: client → edge/API tier → application services → "
        "data stores and integrations. Authenticate and authorize at the boundary; "
        "propagate correlation IDs for tracing."
    )
    if requirements.needs_async_processing:
        qname = "message_queue"
        if qname in components.selections:
            doc.add_paragraph(
                f"Asynchronous workloads fan out via {components.selections[qname].selected.name}: "
                "publish after transactional commit, consume with idempotent handlers, "
                "and route failures to a dead-letter strategy."
            )
        else:
            doc.add_paragraph(
                "Async processing is required — introduce an explicit queue/bus selection "
                "and document retry and ordering semantics."
            )

    doc.add_heading("5. Interfaces and APIs", 1)
    doc.add_paragraph(
        "Expose stable, versioned HTTP (or gRPC) contracts. Below are thematic surfaces "
        "derived from functional scope — refine paths and schemas during API design review."
    )
    for fr in requirements.functional_requirements[:12]:
        doc.add_paragraph(
            f"{fr.name}: REST or RPC resources backing «{fr.description[:160]}»",
            style="List Bullet",
        )
    if not requirements.functional_requirements:
        doc.add_paragraph(
            "Define resource models and error envelopes alongside the PRD functional themes."
        )

    doc.add_heading("6. Security architecture", 1)
    nfr = requirements.non_functional_requirements
    doc.add_paragraph(
        "Encryption in transit: TLS for all external and east-west traffic where supported. "
        "Encryption at rest: enable native KMS-backed encryption on managed databases "
        "and object stores."
    )
    if requirements.compliance_needs:
        doc.add_paragraph("Compliance drivers:", style="Heading 3")
        for c in requirements.compliance_needs:
            doc.add_paragraph(f"{c.name}: {c.description}", style="List Bullet")
    else:
        doc.add_paragraph(
            "Map controls to organizational policy (IAM, secrets rotation, audit logging)."
        )

    doc.add_heading("7. Availability and disaster recovery", 1)
    doc.add_paragraph(
        f"Availability target: {nfr.availability_target or 'Align with stakeholder SLOs'}."
    )
    doc.add_paragraph(
        f"RecoveryTime Objective (RTO): {nfr.rto or 'TBD'} · "
        f"Recovery Point Objective (RPO): {nfr.rpo or 'TBD'}."
    )
    doc.add_paragraph(
        "Prefer multi-AZ for stateful services where the vendor supports it; drill failover "
        "and backup restores regularly."
    )

    doc.add_heading("8. Observability", 1)
    doc.add_paragraph(
        "Golden signals: latency, traffic, errors, saturation. Centralize structured logs "
        "with trace correlation; alert on SLO burn rates and dependency health."
    )

    doc.add_heading("9. Capacity and scaling", 1)
    doc.add_paragraph(
        f"Throughput posture: {nfr.throughput_target or 'Define peak and sustained QPS'}. "
        f"Concurrency: {nfr.concurrent_users or 'Model concurrent sessions vs. connection pools'}."
    )
    if total is not None:
        doc.add_paragraph(
            f"Aggregate baseline cost estimate (library): ${total:,.0f}/month — "
            "revisit after load tests."
        )

    _style_normal(doc)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _style_normal(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.size = Pt(11)
