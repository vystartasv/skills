---
name: paper-critique
description: "Read, analyse, and critically review academic papers — assess novelty, verify claims, check baselines, evaluate credibility, and produce structured reviews."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [paper-review, research, academic, arxiv, critical-analysis]
    related_skills: [copywriting, fact-checking]
---

# Paper Critique — Structured Academic Review

## Overview

A systematic pipeline for reading a paper, assessing its claims, and producing a structured critical review. This is not a summary — it's an evaluation of credibility, novelty, and practical value.

## When to Use

- User sends an arXiv link or asks "review this paper"
- User asks "how real is this?" or "is this a breakthrough?"
- User needs a critical assessment before engaging on social media
- User needs to understand where a paper sits in the broader research landscape

## Pipeline

### Phase 1: Gather

Fetch the paper from multiple sources in parallel:

1. **arXiv abstract page** — title, authors, submission date, venue, license
2. **HTML version** (arxiv.org/html/ID) — full text with figures
3. **PDF** (arxiv.org/pdf/ID) — fallback if HTML unavailable

Key data points to extract:
- Title, authors, affiliation (if any)
- Venue: main conference? workshop? arXiv-only?
- License (CC BY-NC-ND = non-commercial, can't build on)
- Submission date (is it recent?)
- **The actual method** — not just the abstract's framing

### Phase 2: Cross-Reference

Check the paper's claims against external sources:

1. **Code availability** — search GitHub for the method name, author name, paper title
2. **Citations** — Google Scholar or Semantic Scholar for citation count
3. **Baselines** — does the paper use standard benchmarks and standard metrics?
4. **Related work** — search for prior methods that the paper claims to be novel against

### Phase 3: Analyse

Assess the paper across these dimensions:

**Architecture vs Framing**
- Is the architecture genuinely new, or is it an existing architecture dressed in new terminology?
- The key test: describe the method in one equation.

**Metric honesty**
- Does the paper report standard metrics or bespoke ones?
- Standard benchmarks have standard metrics. If they use "validation loss" instead, they may be hiding poor task performance.

**Delta magnitude**
- Small deltas (<2% absolute) on established benchmarks = within noise or marginal
- Large deltas (>5% absolute) on ALL benchmarks = suspicious unless accompanied by code release

**Venue signal**
- Top conference (NeurIPS, ICML, ICLR) = peer-reviewed, higher bar
- Workshop = lower bar, single-track review
- arXiv-only = not yet peer-reviewed

**Author signal**
- Multiple authors from known labs = reproducibility backing
- Single "Independent Researcher" = no lab support for code/data release
- No code + single author + workshop = treat empirical claims as unverified

### Phase 4: Structure the Review

Deliver a structured critical review covering:

1. **What it does** — one-paragraph plain-language explanation
2. **Your understanding check** — correct the user's mental model if needed
3. **Green flags** — what's actually novel/valuable
4. **Red flags** — metric choices, missing baselines, no code, weak venue, small deltas
5. **The "why not before" answer** — if the method is old architecture, explain why
6. **Verdict** — straightforward assessment

## Pitfalls

1. **Don't take headlines at face value.** Always check the metric. Loss is cheap; task performance is hard.
2. **Don't confuse therapeutic framing with algorithmic novelty.** A 2-layer MLP is not a neural ODE just because you call the gradient a "vector field."
3. **Don't trust "outperforms LoRA" without checking what the LoRA baseline looks like.**
4. **Don't assume no code = bad paper.** But do treat empirical results as unverifiable until code appears.
5. **Don't forget to check the license.** CC BY-NC-ND means you can't legally build on it commercially.
6. **Don't write the social media comment before finishing the full analysis.**
7. **Never fabricate personal baselines or experiments.** Default to neutral questions.
