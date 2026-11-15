# Trust but Verify: LLM-Assisted GIS Data QC

## 30-Minute Talk Topic List — OpenGIS Standards + Open-Weight LLMs for Local Government GIS

**Audience:** municipal, county, and state GIS professionals
**Constraints:** open-weight LLMs only (Hugging Face Hub / equivalent); no proprietary APIs; free/open data; reproducible on laptop / modest VM / on-prem.

## Topic Table (8–10 Rows)

| # | Topic Title (max 10 words) | Core Idea (2–3 sentences) | Why It Matters to Local Gov (1 sentence) | Demo Sketch (what can be shown live) |
|---|---------------------------|---------------------------|--------------------------------------------|--------------------------------------|
| 1 | ChatGeoAI: Natural Language to PyQGIS with Llama 2 | ChatGeoAI is a peer-reviewed framework built on open-weight Llama 2 that uses NLP, tailored entity recognition, and geospatial ontology mapping to convert natural-language questions into executable PyQGIS scripts. A QGIS demo can take a prompt such as "buffer schools by 500 m and intersect parcels" and produce a reviewable script before running it. Because the LLM is constrained by the ontology and GIS engine, errors are easier to debug. | It lowers the scripting barrier for staff who already use QGIS and public data. | Live QGIS window accepts a natural-language prompt, shows generated PyQGIS code, and runs buffer/intersect on a municipal parcel layer. |
| 2 | Local Open-Weight LLMs for Geographic Question Answering | LLaMA 3.1 8B and Gemma 2 9B IT can run on a laptop or modest VM and answer conversational geographic questions by calling route-optimization APIs (OSRM/Valhalla) via Ollama or a GGUF runner. The demo keeps routing computation deterministic and the LLM responsible only for explanation and citation. | It lets departments prototype resident-facing spatial assistants without sending data to proprietary endpoints. | Jupyter notebook/CLI asks route questions; Ollama answers using JSON returned by a local OSRM/Valhalla endpoint, with source URLs shown. |
| 3 | Catalog-Grounded GeoServer Layer Selection via WMS Capabilities | A resolver reads a GeoServer WMS `GetCapabilities` document and constrains its JSON schema so layer items must be a catalog name rather than free text. Validation drops nonexistent layers, reducing hallucinated map layers in staff or public requests. | It prevents maps referencing layers that don't exist and builds trust in AI-generated map requests. | CLI passes a plain-language request to the resolver; it returns a JSON layer selection validated against a live `GetCapabilities` document. |
| 4 | MCP Servers for Authoritative IGN Geoplateforme Data | Geocontext is an MCP server that queries authoritative French reference geodata on the IGN Géoplateforme without local downloads, filtering responses for LLM context. It anticipates OGC API – Features schema enrichment to help assistants pick the right layers and attributes, though components are experimental and require auditing. | It shows how AI assistants can rely on authoritative government data while reducing hallucinations and local data duplication. | Chat client calls MCP tools to list IGN layers, describe schema fields, and query a filtered GeoJSON subset. |
| 5 | MCP Agents for County or City Open Data Layers | An MCP server exposes local open data as tools: this pattern geocodes an address, then runs spatial or attribute queries against ArcGIS REST or OGC layers, returning structured results with the source URL. The LLM acts as an orchestrator while the source API stays the data authority. | It turns open-data portals into conversational public-service tools while keeping queries accountable to source APIs. | Ask "How many parcels are within 500 ft of this address?" and show geocoding plus layer query with the source URL. |
| 6 | Copernicus Observia-Style AI Data Guidance Portal | Copernicus Observia AI launched on 12 June 2025 as an EEA beta demonstrator to help users find, understand, and use Copernicus products. A scoped data-guide assistant can be emulated over a department's own COG, WMS, and WMTS catalogs using open-weight models and retrieval, without claiming any established air-gapped or proprietary model. | It can reduce support burden and help residents or staff discover relevant public datasets. | Notebook ingests catalog metadata and answers "Which land-cover layer covers my municipality and how do I access it?" |
| 7 | Municipal Open-Data QA Benchmarks with Open Weights | Testing shows open-weight and proprietary models can be close on some standard spatial tasks, yet one open-data analytical QA benchmark reported open-weight models at 60.9–69.2% analytical correctness versus 98.2% for GPT-4.1. Department pilots should use fixed question sets and human adjudication before substituting local sovereign models for proprietary APIs. | It helps departments avoid overclaiming automation quality and set realistic accuracy thresholds. | Side-by-side Jupyter evaluation of LLaMA-3, Mixtral, or Qwen-2 against local GIS questions with scored outputs. |
| 8 | Dynamic WFS 2.0 Discovery Returning GeoJSON URLs | Dynamic OGC WFS 2.0 discovery can expose search, schema description, and query tools, returning both feature properties and a WFS GeoJSON URL consumable by a map viewer. This keeps the LLM inside an open-standards workflow rather than inventing endpoints. | It lets staff discover and visualize authoritative WFS layers without manually constructing OGC requests. | Agent queries WFS, returns a GeoJSON URL, and a Leaflet/OpenLayers map auto-loads the resulting layer. |
| 9 | Guardrails That Stop LLMs Inventing Coordinates | LLMs must not be trusted to invent coordinates; spatial outputs require a named geographic source plus a recorded source identifier. A resolver can call a gazetteer or approved local dataset and attach source IDs to every geometry it returns. | It prevents incorrect map locations from propagating into permits, inspections, or public reports. | Notebook shows an LLM refusing to provide coordinates, then calling a gazetteer tool and returning an ID-linked point. |
| 10 | LLM-Assisted, Deterministic-Gated Data QC | An open-weight model (e.g., LLaMA 3.1 8B under Ollama) proposes candidate QC issues and fixes for parcels, addresses, and permits as structured JSON; PostGIS `ST_*` predicates and schema constraints validate each suggestion before any ticket is raised. Address normalization, cross-field consistency checks, and FGDC/ISO 19115 metadata drafting can all run human-gated, with the deterministic engine acting as the final authority. | It cuts manual QC time while preserving an auditable, reversible approval trail. | Jupyter notebook loads a parcels GeoDataFrame, LLM flags issues in a diff table, PostGIS/`great_expectations` checks confirm, reviewer clicks apply/skip. |

## Generic 30-Minute Slide Outline (applicable to any topic)

- **Problem & audience**: high-friction GIS workflows, uneven technical capacity, and demand for conversational/public-facing geospatial services.
- **OpenGIS primer**: OGC standards (WMS/WMTS/WFS/WCS, OGC API – Features/Maps/Processes), GeoServer, PostGIS, QGIS, Leaflet/OpenLayers, and public data portals.
- **Open-weight LLM primer**: downloadable model weights, local serving with Ollama/llama.cpp/vLLM/TGI, privacy, cost, and governance trade-offs.
- **Integration pattern**: the LLM as orchestrator constrained by catalogs, JSON schemas, deterministic GIS/routing engines, and OGC endpoints; source APIs remain the data authority.
- **Live demo**: one concrete question → grounded tool calls → generated script/query → map output → audit trail/path to reproduction.
- **Governance & accuracy**: coordinate guardrails, provenance, source identifiers, benchmark results, and human review as requirements, not afterthoughts.
- **Q&A & next steps**: pilot scope, data licensing, hardware sizing, and a measurement plan.

## Master List of Libraries & Data Sources

- `PyQGIS` – QGIS Python API for executing spatial scripts — https://qgis.org/pyqgis/
- `QGIS` – open-source desktop GIS used in many government workflows — https://qgis.org/
- `GeoServer` – OGC-compliant WMS/WFS/WCS service stack — https://geoserver.org/
- `langchain` – LLM pipeline and tool orchestration — https://github.com/langchain-ai/langchain
- `llama-cpp` / `llama-cpp-python` – local inference for GGUF models — https://github.com/ggerganov/llama.cpp
- `Ollama` – local model serving and management — https://ollama.com/
- `vLLM` – high-throughput open-model serving — https://github.com/vllm-project/vllm
- `Text Generation Inference (TGI)` – production serving for open models — https://github.com/huggingface/text-generation-inference
- `Hugging Face Hub` – distribution point for open-weight checkpoints — https://huggingface.co/
- `Llama 2 (7B/13B/70B)` – open-weight base model used by ChatGeoAI — https://huggingface.co/meta-llama/Llama-2-7b-hf
- `LLaMA 3.1 8B` – open-weight local model option — https://huggingface.co/meta-llama/Llama-3.1-8B
- `Gemma 2 9B IT` – open-weight local model option — https://huggingface.co/google/gemma-2-9b-it
- `Mistral-7B` – open-weight model option — https://huggingface.co/mistralai/Mistral-7B-v0.1
- `Mixtral 8×7B` – open-weight mixture-of-experts model option — https://huggingface.co/mistralai/Mixtral-8x7B-v0.1
- `Qwen-2` – open-weight model option — https://huggingface.co/Qwen
- `Model Context Protocol (MCP)` – protocol and SDKs for exposing data tools to LLMs — https://modelcontextprotocol.io/
- `WMS 1.3.0 / GetCapabilities` – OGC discovery endpoint used for catalog-grounded layer selection — https://www.ogc.org/standards/wms/
- `WFS 2.0` – OGC standard for vector feature querying and GeoJSON flows — https://www.ogc.org/standards/wfs/
- `OGC API – Features` – standard referenced for schema enrichment — https://ogcapi.ogc.org/features/
- `IGN Géoplateforme` – authoritative French reference geodata source — https://cartes.gouv.fr/
- `Charlotte/Mecklenburg open data (MCP)` – municipal open-data adapter pattern — https://github.com/Lavoiedavidw/Charlotte-City-MCP
- `Copernicus Land Monitoring Service / Observia AI` – open EO products and 12 June 2025 beta guide — https://land.copernicus.eu/en/news/copernicus-observia-ai-launched-to-guide-users-through-copernicus-data
- `OSRM` – open-source routing engine for deterministic route answers — https://project-osrm.org/
- `Valhalla` – open-source routing engine option — https://github.com/valhalla/valhalla
- `Leaflet` – browser map viewer for WFS GeoJSON results — https://leafletjs.com/
- `OpenLayers` – browser map viewer option — https://openlayers.org/
- `Geocontext (IGN)` – MCP server over IGN Géoplateforme data — https://github.com/ignfab/geocontext

## Key caveat from verification

- Appropriate open-weight models were close to proprietary models on some generic spatial tasks, but a targeted open-government-data QA benchmark showed a large correctness gap (60.9–69.2% vs. 98.2% for GPT-4.1). Treat sovereign local models as **audit candidates**, not automatic substitutes.
- ChatGeoAI is presented as a research framework, not a publicly released product — plan to reproduce and adapt.
- Claims that did **not** survive adversarial review (and are excluded): GeoAgent outperforming baselines; open-weight models matching proprietary ones on the municipal benchmark (refuted as task-dependent); GIS-OSS self-hosted platform claims; OGD4All 98% accuracy; proprietary "GPT-5.6" claims; 4-bit quantization quality loss; instruction fine-tuning harm; Act 4 running on-device. Treat any product pitch that repeats these as unverified.