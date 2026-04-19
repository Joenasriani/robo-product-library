# Robo Product Library

Private master repository for RoboMarket AI agents, reusable skills, robot protocols, RAG products, and marketplace delivery assets.

## Repository Structure

- [`agents/`](./agents/) — AI agent products (8 inquiry-ready domain agents + 2 internal infrastructure agents)
- [`ai_products/`](./ai_products/) — AI product lines outside `agents/` (RAG suite + legacy Tender Analyzer app)
- [`protocols/`](./protocols/) — canonical robot protocol products and GCC localization packs
- [`marketplace/`](./marketplace/) — storefront catalogs, listings, product pages, and downloadable bundles
- [`skills/`](./skills/) — reusable prompt and execution skill modules
- [`shared/`](./shared/) — cross-repo governance and shared documentation
- [`archive/`](./archive/) — paused/deprecated work

## Product Index

### Agent products (`agents/`)
- Tender Analyzer GCC
- Sales Outreach Agent
- Lead Research Agent
- Enterprise RFP Response Assistant
- Social Content Ops Agent
- Robot Demo Video Generator
- Claw Hub Installer Agent
- Tender Monitoring Agent
- AI Agent Download Center
- Protocol Marketplace Agent

See full metadata (status, ports, priorities): [`AGENTS_LIST.md`](./AGENTS_LIST.md).

### RAG products (`ai_products/rag/`)
- Simple RAG Chain
- Tool-Use RAG
- Ollama RAG
- RAG as a Service
- Advanced RAG

See detailed product docs: [`ai_products/rag/README.md`](./ai_products/rag/README.md).

### Protocol products (`protocols/products/`)
Canonical protocol manifests are indexed in:
- [`protocols/products/index.yaml`](./protocols/products/index.yaml)
- [`marketplace/protocols/catalog.yaml`](./marketplace/protocols/catalog.yaml)

## Navigation

- Agent catalog: [`agents/README.md`](./agents/README.md)
- Marketplace docs: [`marketplace/README.md`](./marketplace/README.md)
- Protocol docs: [`protocols/README.md`](./protocols/README.md)
- Skills overview: [`skills/README.md`](./skills/README.md)
- Shared docs: [`shared/README.md`](./shared/README.md)
