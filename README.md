# ChartQuery for Dify

[ChartQuery](https://www.chartquery.com) renders charts, diagrams, QR codes and barcodes as images. This plugin lets Dify agents, workflows and chatflows turn data into a chart, a description into a diagram, or a link into a QR code, and show the image right in the conversation.

**Author:** chartquery · **Source:** https://github.com/chartquery/dify-plugin-chartquery · **Contact:** contact@chartquery.com

## Tools

| Tool | What it does |
| --- | --- |
| **Create Chart** | A Chart.js v4 chart from its JSON config. 5 credits. |
| **Chart From Prompt** | A chart from a description and optional raw data (CSV, JSON or text). The AI picks the type and layout. 10 credits. |
| **Create Diagram** | A diagram from its source code in Mermaid, D2, PlantUML, Graphviz, BPMN, DBML and more. 5 credits. |
| **Diagram From Prompt** | A diagram from a description; the AI writes it in Mermaid, D2, PlantUML or Graphviz. 10 credits. |
| **QR Code** | A QR code for a link, email, phone number, Wi-Fi network or any text, with color and size. 3 credits. |
| **Barcode** | A barcode in EAN-13, UPC-A, Code 128, ITF-14, GS1-128 and more. 3 credits. |

Each tool shows the image, returns a text message with its links (the image, a page to open, and when they expire), and a JSON message with `render_url`, `view_url`, `embed_url` and `expires_in` for workflow variables. Links last 3 days on the free plan (with a watermark) and 6 months on paid plans. Errors such as an invalid key, missing credits or a rate limit come back as a text message, and the API key never appears in it.

## Setup

1. Create an account and copy your API key at [app.chartquery.com](https://app.chartquery.com).
2. In Dify, install the **ChartQuery** plugin from the Marketplace.
3. Open **Tools → ChartQuery → Authorize** and paste the API key. Dify checks it with a request that costs no credits.
4. Add the tools to an agent, a workflow or a chatflow.

## Requirements

- Dify 1.0.0 or later.
- Outbound HTTPS access to `api.chartquery.com`.
- A ChartQuery API key. Usage counts against your ChartQuery credits; see [www.chartquery.com/pricing](https://www.chartquery.com/pricing).

## Privacy

See [PRIVACY.md](PRIVACY.md).

## Development

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt pytest pyyaml
.venv/bin/pytest
```

The `Package` workflow builds the `.difypkg` with Dify's plugin CLI and attaches it to a GitHub release when the version in `manifest.yaml` changes.
