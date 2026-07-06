# Hermes Skills

Community skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

## Usage

```bash
hermes skills tap add vystartasv/skills
hermes skills browse
hermes skills install <skill-id>
```

## Skills

### Self-improvement
| Skill | Description |
|-------|-------------|
| `correction-steering-capture` | Capture user corrections in real-time, extract root cause, apply fix |
| `intent-clarification` | Clean user input, handle ambiguity, flag judgement calls |
| `hermes-skillopt` | Automated skill optimizer — tests, scores, and improves skills |
| `memory-ops` | Interactive memory search and management |

### Software Development
| Skill | Description |
|-------|-------------|
| `systematic-debugging` | 4-phase root cause debugging with feedback loop rule |
| `test-driven-development` | Strict RED-GREEN-REFACTOR with mandatory verify steps |
| `repo-docs` | Standard open-source repo documentation templates |
| `scrapling` | Anti-bot web scraping (Cloudflare bypass, MCP server) |
| `local-llm-client` | Build reliable HTTP clients for local model servers |
| `github-workflow` | Complete GitHub operations via gh CLI + curl fallbacks |

### Agent Infrastructure
| Skill | Description |
|-------|-------------|
| `context-packer` | Repo pruner for local models: 2521 → 8 files |
| `agent-researcher` | Deep research via structured APIs and delegation |
| `agent-reach` | Internet platform access for agents (Twitter, YouTube, Reddit, etc.) |
| `native-mcp` | Connect MCP servers (stdio/HTTP) from Hermes |

### macOS
| Skill | Description |
|-------|-------------|
| `macos-computer-use` | Drive macOS desktop in background (screenshots, clicks, typing) |
| `macos-privacy-permissions` | Grant TCC permissions to CLI tools |
| `macos-python-homebrew` | Manage Python versions via Homebrew |

### DevOps
| Skill | Description |
|-------|-------------|
| `git-housekeeping` | Clean, shrink, and maintain git repos with filter-repo |

### Research
| Skill | Description |
|-------|-------------|
| `fact-checking` | Verify claims via primary source triangulation |
| `paper-critique` | Structured academic paper review and analysis |

### Productivity
| Skill | Description |
|-------|-------------|
| `markitdown` | Convert documents/files to Markdown via Microsoft MarkItDown |

### Note-taking
| Skill | Description |
|-------|-------------|
| `obsidian` | Read, search, create, edit Obsidian notes + CLI integration |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Skills must be universal — no personal paths, keys, or project-specific references.
