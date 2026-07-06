---
name: local-llm-client
description: "Build reliable HTTP clients against local model servers (oMLX, Ollama, llama.cpp) — error classification, retry strategy, memory-aware serialization."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [local-llm, http-client, retry, omlx, ollama, llama-cpp]
---

# Local LLM Client Patterns

## When to use

You're writing code that calls a local model server (OpenAI-compatible API on localhost), and you need it to be resilient without hammering the server into OOM.

## Core insight: local vs cloud retry semantics

Cloud APIs (OpenAI, Anthropic) handle scaling — 429/503 are transient. **Local servers have hard resource ceilings.** A `507: would exceed memory ceiling` error won't resolve with retries.

## Error classification

| Bucket | Status | Action |
|--------|--------|--------|
| **Transient** | 429, 500, 502, 503, 504 | Retry with exponential backoff |
| **Fatal** | 507 (OOM) | Fail fast — don't burn retries |
| **Silent** | timeout, connection refused | Best-effort catch, return empty |

## Pattern 1: Retry with backoff (no 507)

```typescript
const RETRYABLE = new Set([429, 500, 502, 503, 504]);

async function withRetry<T>(label: string, fn: () => Promise<T>): Promise<T> {
  const max = Number(process.env.INFER_RETRIES || 4);
  for (let attempt = 0; ; attempt++) {
    try { return await fn(); }
    catch (e: any) {
      const status = e?.status ?? e?.response?.status;
      if (!RETRYABLE.has(status) || attempt >= max) throw e;
      const wait = 1500 * Math.pow(2, attempt);
      console.warn(`[infer] ${label} got ${status}; retry ${attempt+1}/${max} in ${wait/1000}s…`);
      await sleep(wait);
    }
  }
}
```

**Never use 507-specific longer waits.** Fail fast on 507, always.

## Pattern 2: Shared-server serialization lock

When multiple components share one local model server, add a promise-based mutex:

```typescript
let owner: string | null = null;
let queue: { owner: string; resolve: () => void }[] = [];

export const serverLock = {
  async acquire(label: string): Promise<void> {
    if (!owner) { owner = label; return; }
    return new Promise<void>(resolve => {
      queue.push({ owner: label, resolve });
    });
  },
  release(): void {
    if (queue.length > 0) {
      const next = queue.shift()!;
      owner = next.owner;
      next.resolve();
    } else {
      owner = null;
    }
  },
};
```

**Limitation:** An in-process mutex can't prevent a separate OS process from calling the server.

## Pattern 3: Configuration fallback chain

```typescript
function getActiveConfig() {
  try {
    const settings = readJson('~/.config/local-llm/settings.json');
    return {
      baseURL: settings.baseUrl || process.env.LOCAL_LLM_URL || 'http://127.0.0.1:8000/v1',
      model: settings.defaultModel || process.env.LOCAL_LLM_MODEL || 'default-model',
    };
  } catch {
    return {
      baseURL: process.env.LOCAL_LLM_URL || 'http://127.0.0.1:8000/v1',
      model: process.env.LOCAL_LLM_MODEL || 'fallback-model',
    };
  }
}
```

## Pitfalls

- **Don't treat 507 as transient** — it signals the server can't fit another model. Retries don't free memory.
- **Don't use concurrent retry chains** — independent retry logic amplifies load. Coordinate with a lock.
- **Don't assume model stays loaded** — local servers evict idle models. Every call may trigger a reload.
- **Monitor 507 count as a leading indicator** — a spike signals concurrent load conflict.
