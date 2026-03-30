# pymt-learner-agent
Payments Learner is an agentic AI framework designed to simplify the complex world of UK and international payment systems. By orchestrating a team of specialized agents, it transforms dense regulatory standards and technical message formats into clear, actionable knowledge for engineers and financial professionals
# 🎓 UK & EU Payments Learning Agent (DAG-Orchestrated)

An enterprise-grade educational "Swarm" built with the **Google Agent Development Kit (ADK)** and **Gemini 2.0 Flash**. This project moves beyond linear chains by utilizing a **Directed Acyclic Graph (DAG)** architecture to handle the multi-step research, technical validation, and pedagogical synthesis required for UK and SEPA payment rails.

## 🚀 Overview

The **Payments Learner Agent** is designed to train engineers on the complexities of **ISO 20022** and legacy payment systems. By using an agentic DAG, the system ensures that technical data (XML snippets) is validated against internal business rules before being presented to the user.

---

## 🧬 Agentic DAG Architecture

The workflow is structured as a non-linear graph where the **`root_agent`** acts as the Graph Controller, managing the state and transitions between specialized nodes.

### 📍 The Nodes (Agents)

1.  **`payment_researcher` (The Data Miner)**
    * **Role:** Context Retrieval.
    * **Function:** Uses `get_internal_bank_specs` and `WikipediaQueryRun` to fetch high-level rail data (SLA, Currency, Limits).
    * **Output:** `raw_research` state.

2.  **`message_format_expert` (The Schema Architect)**
    * **Role:** Technical Implementation.
    * **Function:** Generates ISO 20022 (`pacs.008`, `pacs.002`) or Legacy (Std 18) snippets. It utilizes the `get_sepa_reason_codes` tool for status mapping.
    * **Output:** `format_data` state.

3.  **`jargon_buster_tutor` (The Pedagogical Sink)**
    * **Role:** Output Synthesis.
    * **Function:** Consumes the validated research and format data to produce a beginner-friendly lesson with analogies and a glossary.

### 🛤️ The DAG Flow (Transitions)

The logic follows a strict **Directed Acyclic** path to prevent infinite loops while allowing for conditional data enrichment:

* **Entry:** User Query → `root_agent`.
* **Step 1:** `root_agent` triggers `payment_researcher`.
* **Step 2:** Research data is passed to `message_format_expert`.
* **Step 3 (Conditional Branch):** * *If SEPA:* The expert focuses on `pacs` XML and IBAN validation.
    * *If BACS:* The expert switches to Fixed-Width Standard 18 logic.
* **Step 4:** Validated technical outputs are passed to `jargon_buster_tutor` for final rendering.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Orchestration:** Google ADK (Agent Development Kit)
* **LLM:** Gemini 2.0 Flash (Optimized for Tool Use & Reasoning)
* **Knowledge Retrieval:** LangChain (Wikipedia API Wrapper)
* **Infrastructure:** Google Cloud (Cloud Run & Cloud Logging)

---

## 📥 Installation & Setup

1.  **Initialize Repository:**
    ```bash
    git init
    git add .
    git commit -m "feat: implement DAG-based payment tutor"
    ```

2.  **Environment Setup:**
    Create a `.env` file:
    ```text
    MODEL=gemini-2.0-flash
    GOOGLE_APPLICATION_CREDENTIALS=service-account.json
    ```

3.  **Dependency Management:**
    ```bash
    pip install -r requirements.txt
    ```

## 🧪 Operational Testing

The DAG can be stress-tested using the following query patterns:

* **Standard Research:** *"How does CHAPS differ from Faster Payments?"*
* **Technical Deep-Dive:** *"Show me the <IntrBkSttlmAmt> tag in a SEPA SCT Inst message."*
* **Error Resolution:** *"Why would a pacs.002 return an RJCT with code MS03?"*

---

## ☁️ Deployment (CI/CD)

To deploy the agent to a serverless environment on **Google Cloud Run**:

```bash
gcloud run deploy payments-tutor \
  --source . \
  --region YOUR_REGION \
  --set-env-vars MODEL=gemini-2.0-flash