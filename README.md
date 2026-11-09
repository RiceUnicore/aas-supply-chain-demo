# 🏭 AAS Cross-Domain Supply Chain Demonstrator (HTW Core & MCP-Chatbot)

**Projektseminar WS 2026/2027 – HTW Dresden (Professur für Informationsmanagement)**

Dieses Repository enthält den lauffähigen Prototyp der **HTW-Zone (`core` + `agent`)** für unseren domänenübergreifenden Supply-Chain-Demonstrator (Prozessindustrie / TU Dresden $\rightarrow$ Diskrete Fertigung / HTW Dresden $\rightarrow$ Kunde).

---

## 🎯 Was dieser Stand bereits kann (Features)

1. **AAS- & DMP-Extraktion:** Liest die Materialstammdaten (SAP-Format `MATNR`, `MAKTX`, `CHARG`) sowie das zulässige Prozessfenster (Aushärtetemperatur, Haltezeit, Viskosität, PCF) aus der Klebstoff-AAS (Digital Material Passport – DMP) aus.
2. **InfluxDB-Zeitreihen & Fehlersimulation:** Schreibt und liest Ofen-Temperaturkurven über eine **InfluxDB** (inklusive automatischem **In-Memory-Fallback**, falls lokal kein Docker läuft).
   * **Bauteil `U-1042` (Fehlerfall / RMA-Showcase):** Simuliert einen 8-minütigen Temperaturabfall im Ofen auf `161,2 °C` (unterhalb des DMP-Limits von `165,0 °C`, aber noch oberhalb der internen HTW-Ausschussgrenze von `158,0 °C` $\rightarrow$ Status `SELLABLE_WITH_TOLERANCE`, führt später beim Kunden zum Feldausfall).
   * **Bauteil `U-1043` (Gutteil):** Optimaler Produktionslauf bei `~175,0 °C` (`PASS_OPTIMAL`).
3. **Automatisierter DPP-Builder:** Fusioniert die DMP-Vorgaben mit den InfluxDB-Prozess-KPIs und erzeugt daraus vollautomatisch den **Digitalen Produktpass (DPP)** im AAS-V3-JSON-Format mit vier Submodels:
   * `Nameplate`
   * `MaterialInputs` (inkl. `supplierLotId` & unveränderlichem `SHA-256` Snapshot-Hash des Eingangs-DMP)
   * `ProductionProcess` (gemessene Min-/Max-/Mittelwerte, Zeit außerhalb des Prozessfensters, Qualitätsentscheidung)
   * `CarbonFootprint` (kombinierter CO₂-Fußabdruck)
4. **MCP 2.x Server & Reaktiver KI-Chatbot:** Bindet die vier lesenden Domänen-Tools (`get_dpp`, `get_process_window`, `trace_backward`, `compare_to_window`) über das **Model Context Protocol (MCP)** an. Eine integrierte Weboberfläche zeigt links den reaktiven Chatbot (inkl. Protokollierung der aufgerufenen MCP-Tools) und rechts den generierten DPP im Live-JSON-Inspector.

---

## 📂 Projektstruktur

```text
AAS-Projekt/
├── docs/                   # Konzept- & Architekturdokumentation (Markdown)
│   ├── main-document.md
│   ├── forward-chain-process.md
│   ├── tech-stack.md
│   └── glossary.md
├── core_backend.py         # Hauptanwendung (FastAPI + InfluxDB + DPP-Builder + MCP-Chatbot)
├── docker-compose.yml      # Optionales Setup für eine echte InfluxDB v2.7
├── requirements.txt        # Benötigte Python-Pakete
├── .gitignore              # Ausgeschlossene temporäre Dateien
└── README.md               # Diese Anleitung
```

---

## 🚀 Schnellstart (In 2 Minuten lokal starten)

### Voraussetzungen
* **Python 3.10+** (getestet bis Python 3.14 unter Windows)
* *Optional:* **Docker Desktop** (falls die echte InfluxDB genutzt werden soll – der Code läuft dank integriertem Fallback aber auch **komplett ohne Docker**!)

### Schritt 1: Repository klonen & in den Ordner wechseln
```bash
git clone <EURE-REPO-URL>
cd AAS-Projekt
```

### Schritt 2: Python-Pakete installieren
```bash
pip install -r requirements.txt
```

### Schritt 3 (Optional): Echte InfluxDB per Docker starten
*Hinweis: Wenn ihr Docker nicht installiert oder nicht gestartet habt, könnt ihr diesen Schritt einfach überspringen. Das Backend nutzt dann automatisch die integrierte In-Memory-Simulation.*
```bash
docker compose up -d
```

### Schritt 4: Backend & Chatbot starten
```bash
python core_backend.py
```

---

## 🖥️ Bedienung & Testen im Browser

Sobald `python core_backend.py` läuft, öffnet euren Browser unter:

👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### Was ihr dort testen könnt:
1. **Schnellbefehle unter dem Chatfenster anklicken:**
   * **„📦 DPP für Bauteil U-1042 abrufen“:** Der Agent ruft `MCPServer.call_tool('get_dpp')` auf und lädt rechts im JSON-Inspector den komplett generierten Digitalen Produktpass.
   * **„🔍 Warum ist U-1042 ausgefallen? (RMA-Trace)“:** Der Agent kombiniert reaktiv `trace_backward`, `compare_to_window` und `get_dpp` und deckt den 8-minütigen Temperaturabfall im Aushärteofen samt exakten AAS-Elementpfaden auf.
   * **„🧪 DMP-Prozessfenster abfragen“:** Liest die Soll-Vorgaben der Klebstoff-Charge `CH-2610-412` über `get_process_window` aus.
   * **„✅ Bauteil U-1043 prüfen“:** Zeigt als Gegenbeispiel ein fehlerfrei produziertes Bauteil (`PASS_OPTIMAL`).
2. **Freie Fragen im Chat stellen:** Ihr könnt auch eigene Fragen eintippen (z. B. *„Prüfe die Ursache für den Fehler bei U-1042“*).
3. **Optionales lokales LLM (Ollama):** Falls auf eurem Rechner lokal [Ollama](https://ollama.com/) läuft (`ollama run llama3.2`), erkennt das Backend dies automatisch und lässt das Sprachmodell die Antworten aus den MCP-Daten frei ausformulieren.

---

## 🔌 Verfügbare REST-API-Endpunkte (Swagger UI)

Unter **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** findet ihr die interaktive FastAPI-Dokumentation:
* `GET /` – Startet die Chatbot- & DPP-Inspector-Weboberfläche
* `GET /api/dpp/{unit_id}` – Generiert und liefert das DPP-AAS-JSON für ein Bauteil (z. B. `U-1042` oder `U-1043`)
* `POST /api/chat` – Endpunkt für den reaktiven MCP-KI-Agenten

---

## 📌 Nächste offene Schritte (TODOs im Team)
* [ ] **TUD-Zone (`tud-aas` / `tud-seed`):** Eigenen Eclipse-BaSyx-Container für den Lieferanten-DMP anbinden (statt lokalem Dictionary in `core_backend.py`).
* [ ] **ERP-System (`erp`):** Anbindung des SAP-CAP-/OData-V4-Mocks als führendes *System of Record*.
* [ ] **Ontologie-Graph (`rdflib`):** OWL/SHACL-Graphen in `core` ergänzen.
* [ ] **React-SPA (`web`):** Überführung in das Multi-Perspektiven-Frontend mit React Flow & ECharts.