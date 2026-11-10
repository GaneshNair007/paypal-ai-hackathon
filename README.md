# 🛡️ PayPal AI — Autonomous Multi-Agent Consensus Room

> **Autonomous Hackathon Submission engineered end-to-end by JARVIS & OpenJarvis Cognitive Bridge.**  
> Candidate: **Ganesh Nair** ([@GaneshNair007](https://github.com/GaneshNair007) / `nairganesh134@gmail.com`)  
> Target Hackathon: **PayPal AI Hackathon** ($67,500 in Prizes on Devpost)

---

## 🌟 Overview & Key Innovations

Traditional fraud prevention engines rely on static rule tables or opaque monolithic black-box models. 
**PayPal AI Consensus Room** introduces a distributed multi-agent architecture where four autonomous specialist agents evaluate each transaction in parallel, sealing every verdict with a cryptographic SHA-256 Merkle proof:

1. **Analyst Agent**: Examines velocity, geofence hops, and historical behavioral deviations.
2. **Risk Officer Agent**: Evaluates capital exposure, liquidation thresholds, and reserve ratios.
3. **Compliance Agent**: Performs real-time AML/Sanctions screening and Travel Rule Enhanced Due Diligence (EDD).
4. **Cryptographer Agent**: Reconciles the multi-agent consensus ratio and seals an immutable audit block in the ledger.

---

## 🚀 Live Interactive Frontend

The repository includes a sleek glassmorphic HUD simulator served directly at `/`:
- **Live Transaction Ingest**: Test presets for safe micro-settlements vs. high-risk rapid cross-border withdrawals.
- **Agent Cards**: Real-time status indicators across all 4 specialist agents.
- **Consensus Execution Receipt**: Dynamic risk score gauge, consensus ratio, latency benchmarks, and verified Merkle hash.

---

## 💻 Quickstart & Local Execution

### 1. Standard Python Execution
```bash
# Clone the repository
git clone https://github.com/GaneshNair007/paypal-ai-hackathon.git
cd paypal-ai-hackathon

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the test suite (100% Passing)
pytest test_app.py -v

# Start the application server
python main.py
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) to access the interactive Consensus Room.

---

## 🐳 Docker Container Execution

```bash
docker-compose up --build
```
The containerized service will be available at [http://localhost:8080](http://localhost:8080).

---

## ☁️ Cloud Deployment (Render / Railway)

This repository includes a native [`render.yaml`](render.yaml) specification:
1. Connect your GitHub repository to Render.com.
2. Select **Blueprint** and point to `render.yaml`.
3. Automatic deployment provisions the web service instantly.

---

## 📚 Complete Execution Logs & Documentation
- [`research.md`](research.md) — Multi-LLM consensus research comparing DeepSeek, FreeLLMAPI, and security policies.
- [`COMMAND_LOG.md`](COMMAND_LOG.md) — Complete chronological audit trail of all commands and operations executed by JARVIS from scratch.
- [`submission_form.json`](submission_form.json) — Pre-filled Devpost hackathon registration and submission payload.
