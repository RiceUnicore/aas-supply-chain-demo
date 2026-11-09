# Glossar & Abkürzungsverzeichnis

Projektseminar WS 2026/2027 – *Aufbau eines AAS-basierten Cross-Domain Supply Chain Demonstrators*
Professur für Informationsmanagement, HTW Dresden

> **Status:** Erstentwurf, Stand 20.10.2026. Gesammelt aus den Meeting-Notizen (05.10. / 14.10.), der Themenbeschreibung und den Kickoff-Folien. Einträge mit Status *Annahme* oder *offen* müssen im Team bzw. mit den Betreuern geklärt werden.

---

## 1. Konventionen

### 1.1 Umgang mit Abkürzungen

1. **Erstverwendung:** In jedem Dokument wird die Abkürzung bei der ersten Nennung ausgeschrieben: *Asset Administration Shell (AAS)*. Danach wird nur noch die Abkürzung verwendet.
2. **Zwei Verzeichnisse, ein Haupteintrag:** Jede Abkürzung steht in Abschnitt 2. Hat sie einen erklärungsbedürftigen Begriff dahinter, steht die Erklärung in Abschnitt 3 unter der **Langform**. Die Abkürzung verweist dorthin (→).
3. **Schreibweise:** So, wie der Standard sie vorgibt (`AAS`, `DPP`, `eCl@ss`/`ECLASS` siehe 1.3). Plural ohne Apostroph: *DPPs*, nicht *DPP's*.
4. **Sprache:** Fließtext deutsch. Fachbegriffe aus AAS/IDTA bleiben englisch (*Submodel*, *Submodel Template*, *Property*), weil Tools und Spezifikationen sie so führen.
5. **Mehrdeutige Kürzel** werden im Text nie ungeklärt benutzt (z. B. *TU* vs. *TUD*, siehe 2). Im Zweifel ausschreiben.
6. **Neue Abkürzung?** Erst hier eintragen, dann im Dokument verwenden.

---

## 2. Abkürzungsverzeichnis

| Abkürzung | Langform | Kurzerklärung / Verweis | Quelle | Status |
|---|---|---|---|---|
| **AAS** | Asset Administration Shell (Verwaltungsschale) | → Asset Administration Shell | S, T | bestätigt |
| **AASX** | AAS Package File Format | Dateiformat zum Austausch von AAS-Paketen; wird von Package Explorer / AASX Server genutzt | vorgeschlagen | Annahme |
| **AI / KI** | Artificial Intelligence / Künstliche Intelligenz | → AI Chat Bot | S | bestätigt |
| **API** | Application Programming Interface | Programmierschnittstelle; bei AAS Typ 2 z. B. via REST | S | bestätigt |
| **CAD** | Computer-Aided Design | Statische Modelle = Level 1 Digital Model | S | bestätigt |
| **CE** | Conformité Européenne | Konformitätskennzeichen, Teil der Nameplate-Daten | S | bestätigt |
| **CO₂** | Kohlenstoffdioxid | → CO₂-Fußabdruck | T | bestätigt |
| **DMP** | Digitaler Materialpass (Digital Material Passport) | → Digitaler Materialpass | T | bestätigt |
| **DPP** | Digitaler Produktpass (Digital Product Passport) | → Digitaler Produktpass | S, T, M1 | bestätigt |
| **DT** | Digital Twin | → Digitaler Zwilling | vorgeschlagen | Annahme |
| **ECLASS** | (Eigenname, früher eCl@ss) | Standard zur Klassifikation und Beschreibung von Produkten/Merkmalen | S | bestätigt |
| **ERP** | Enterprise Resource Planning | Planungs-/Beschaffungssystem; Zielsystem für AAS-Daten (SAP) | T, S | bestätigt |
| **GLN** | Global Location Number | Eindeutige Standort-/Partnerkennung (Beispiel-Submodel Identification) | S | bestätigt |
| **HTW** | Hochschule für Technik und Wirtschaft Dresden | Im Szenario: letzter Produzent | S, M2 | bestätigt |
| **I4.0** | Industrie 4.0 | Kontext der AAS | S | bestätigt |
| **IDTA** | Industrial Digital Twin Association | Veröffentlicht AAS-Spezifikation und Submodel Templates | S | bestätigt |
| **Influx** | InfluxDB | Zeitreihendatenbank für Prozessdaten im Testbed | S | Annahme |
| **IPCEI** | Important Project of Common European Interest | Rahmen für „IPCEI Semiconductor-AI" | S | bestätigt |
| **ISO/IEC 30173** | – | Norm, aus der die Definition „Digital Twin" zitiert wird | S | bestätigt |
| **LLM** | Large Language Model | Basis des AI Chat Bots | vorgeschlagen | Annahme |
| **MCP** | Model Context Protocol | Anbindung von KI an externe Services/Daten („Reicht ein MCP?") | M1 | Annahme |
| **MES** | Manufacturing Execution System | Fertigungsleitsystem; Zielsystem für AAS-Daten | T | bestätigt |
| **ML** | Machine Learning | z. B. Training von Bewegungsabläufen (Level 3) | S | bestätigt |
| **MS1–MS4** | Meilenstein 1–4 | MS1 Use Case, MS2 Recherche & Projektplan, MS4 grober Abschluss/Präsentation | S | bestätigt |
| **NPD** | New Product Development | Phase im Product Lifecycle | S | bestätigt |
| **OData** | Open Data Protocol | Schnittstelle zu SAP („SAP OData") | S | Annahme |
| **PCF** | Product Carbon Footprint | Berechnung/Angabe des CO₂-Fußabdrucks | vorgeschlagen | Annahme |
| **PLM** | Product Lifecycle Management | Verwaltung des Produktlebenszyklus | S | bestätigt |
| **Prop** | Property | → Submodel Element | S (Package Explorer) | bestätigt |
| **RAG** | Retrieval-Augmented Generation | Möglicher Ansatz für den AI Chat Bot | vorgeschlagen | Annahme |
| **REST** | Representational State Transfer | Schnittstellenstil bei AAS Typ 2 | S | bestätigt |
| **RMA** | Return Merchandise Authorization | Reklamations-/Rückgabeprozess des Kunden | M2 | Annahme |
| **SDK** | Software Development Kit | z. B. BaSyx SDK | S | bestätigt |
| **SM** | Submodel | → Submodel | S (Package Explorer) | bestätigt |
| **SMC** | Submodel Element Collection | → Submodel Element | S (Package Explorer) | bestätigt |
| **SPS / PLC** | Speicherprogrammierbare Steuerung / Programmable Logic Controller | Beispiel-Asset: Siemens S7-1500 | S | bestätigt |
| **TU / TUD** | Technische Universität Dresden | Supplier (Prof. Urbas), Perspektive „TU → DPP" | M1, M2, S | Annahme (Kürzel) |
| **UL** | Underwriters Laboratories | Prüfzeichen im Nameplate-Beispiel | S | bestätigt |
| **WS** | Wintersemester | – | T | bestätigt |

---

## 3. Begriffe

### 3.1 AAS & Digitaler Zwilling

| Begriff | Erklärung | Quelle | Status |
|---|---|---|---|
| **Asset** | (Im)materielles Objekt, Software oder Prozess, das digital repräsentiert wird. | S | bestätigt |
| **Asset Administration Shell (AAS)** | Standardisiertes Modell zur Beschreibung digitaler Zwillinge; umfasst Daten zum gesamten Lebenszyklus, Funktionen und Schnittstellen. Veröffentlicht von der IDTA, Grundlage für DPP und Batteriepass. | S | bestätigt |
| **Submodel** | Fachlich abgegrenzter Teil einer AAS (z. B. Nameplate, Technical Data, Documentation). Jedes Submodel Template ist eine unabhängige Einheit. | S | bestätigt |
| **Submodel Template** | Vordefinierte, offene Vorlage für den Aufbau eines Submodels (IDTA, GitHub); standardisiert Informationen über Unternehmensgrenzen. | S | bestätigt |
| **Submodel Element** | Baustein innerhalb eines Submodels, z. B. *Property* (Einzelwert), *Range*, *File*, *Submodel Element Collection* (Gruppe von Elementen). | S | bestätigt |
| **Nameplate** | Standard-Submodel mit Typschilddaten (Hersteller, Seriennummer, Herkunftsland, Baujahr …). | S | bestätigt |
| **AAS Typ 1** | Informationsaustausch über Kopien; AAS wird von Unternehmen zu Unternehmen geschickt. | S | bestätigt |
| **AAS Typ 2** | Austausch über definierte Schnittstellen (z. B. REST); AAS (partiell/komplett) wird automatisch abgefragt und integriert. | S | bestätigt |
| **AAS Typ 3** | Automatisierte, selbstständige Abfragen; AAS Server holt Daten eigenständig über die „AAS I4.0 Language". | S | bestätigt |
| **Datengetriebene AAS / Repräsentative AAS** | Zwei Designprinzipien: Daten werden aus Systemen in die AAS transportiert bzw. Information aus der AAS an Systeme/Menschen verteilt. Kombination ist valide. | S | bestätigt |
| **Datentransport / Informationstransport** | Richtung des Flusses zur bzw. von der AAS. Die AAS ist ein *Datentransportstandard*, keine Speicherlösung. | S | bestätigt |
| **Digitaler Zwilling** | Virtuelle Repräsentation realer Assets/Prozesse, mit bestimmter Frequenz und Genauigkeit synchronisiert (ISO/IEC 30173:2023). | S | bestätigt |
| **Digital Model / Digital Shadow / Digital Twin** | Reifegrade 1–3: statisches Modell → mit Daten angereichert → bidirektionale Kommunikation mit dem physischen Objekt. | S | bestätigt |
| **Semantische Interoperabilität** | Gemeinsames Verständnis der Bedeutung von Daten über Systemgrenzen hinweg, z. B. durch ECLASS-Referenzen. | S, T | bestätigt |
| **Cost of Ownership** | Gesamtkosten über den Lebenszyklus; AAS liefert dafür strukturierte Betriebs-/Wartungsdaten. | S | bestätigt |

### 3.2 Pässe, Nachhaltigkeit, Rückverfolgbarkeit

| Begriff | Erklärung | Quelle | Status |
|---|---|---|---|
| **Digitaler Produktpass (DPP)** | AAS-basierte digitale Repräsentation eines Produkts mit Produkt-, Nachhaltigkeits- und Rückverfolgbarkeitsdaten. Im Szenario erzeugt jeder Produzent einen eigenen DPP. | T, S | bestätigt |
| **Digitaler Materialpass (DMP)** | AAS-basierte Repräsentation eines Materials (hier: Klebstoff) mit Material-, Nachhaltigkeits- und Rückverfolgbarkeitsinformationen. | T | bestätigt |
| **Batteriepass** | Bereits etablierter Produktpass, ebenfalls AAS-basiert. | S | bestätigt |
| **Traceability / Rückverfolgbarkeit / Tracing** | Zurückverfolgen der Prozesskette, um bei einem Fehler beim Kunden die Ursache zu finden (z. B. Temperaturabweichung beim Aushärten). | M1, M2, T | bestätigt |
| **Prozesskette** | Abfolge der Verarbeitungsschritte vom Material bis zum Produkt. | M1 | bestätigt |
| **Kreislaufwirtschaft (Circular Economy)** | Wiederverwendung/Verwertung statt Entsorgung; Daten dazu: Herkunft, Rohstoffe, Recyclingfähigkeit, Verwertungsoptionen. | T | bestätigt |
| **CO₂-Fußabdruck** | Treibhausgasbilanz des Materials/Produkts als Nachhaltigkeitsinformation. | T | bestätigt |
| **Fehlerfall / Ausschuss** | Abweichung im Prozess, die zu Ausschuss oder trotzdem zu einem verkaufsfähigen Produkt führt. | M2 | bestätigt |

### 3.3 Domäne & Szenario

| Begriff | Erklärung | Quelle | Status |
|---|---|---|---|
| **Cross-Domain Supply Chain** | Lieferkette zwischen Prozessindustrie und diskreter Fertigung. | T | bestätigt |
| **Prozessindustrie** | Stoffumwandelnde Industrie (z. B. Chemie); im Demonstrator durch die TU Dresden/Simulation vertreten. | T | bestätigt |
| **Diskrete Fertigung** | Fertigung zählbarer Teile (z. B. Halbleiter, Automobil); im Demonstrator HTW. | T | bestätigt |
| **Wertschöpfungskette / Lieferkette** | Kette der beteiligten Akteure vom Rohstoff bis zum Kunden. | T | bestätigt |
| **Materialanforderung (Request)** | Digitale Anfrage der diskreten Fertigung an die Prozessindustrie auf Basis eines AAS-Datenmodells. | T | bestätigt |
| **Materialformulierung** | Konkrete Zusammensetzung/Konfiguration des Materials durch den Hersteller. | T | bestätigt |
| **Klebstoff** | Beispielmaterial des Szenarios. Verarbeitung: *Vor* (Erwärmen, Mischen), *während* (Temperatur …), *nach* (Aushärten, Lagern …). | T, M2 | bestätigt |
| **Prozessfenster** | Zulässiger Parameterbereich (z. B. Temperatur, Zeit), abgeleitet aus Materialeigenschaften. | T | bestätigt |
| **Aushärtezeit / Verarbeitungstemperatur / Lagerbedingungen** | Materialabhängige Vorgaben, die direkt aus der AAS in ERP/MES übernommen werden. | T | bestätigt |
| **Szenario / Story** | Konkrete Geschichte für den Demonstrator: Fehler tritt beim Kunden auf, Ursache wird zurückverfolgt. Mittlere Komplexität umsetzen, höhere als Ausblick bewerten. | M2 | bestätigt |
| **Perspektiven** | TU → liefert DPP; HTW → Produktion mit neuem HTW-DPP; Customer → Fehler und Tracing. | M2 | bestätigt |
| **Supplier / Produzent / Kunde** | Rollen im Szenario: TU Dresden (Prof. Urbas) / HTW Dresden (Prof. Reichelt) / Abnehmer des Bauteils. | S, M2 | bestätigt |
| **Handling-Unit („Jumi")** | Handhabungseinheit im Produktionsprozess, evtl. als Simulation. Bedeutung von „Jumi" unklar. | S | offen |
| **Ofen (simuliert)** | Vorgetäuschter Ofen zum Erwärmen des Klebers (zu lang/zu kurz, zu heiß/zu kalt) zur Fehlererzeugung. | S | bestätigt |
| **Fehlerfallgenerierung** | Prozess simulieren und mit einer Standardabweichung Fehlerfälle erzeugen. | M2 | bestätigt |
| **Kopplung der DPPs** | Verknüpfung von DPPs entlang der Kette – für das Szenario ausdrücklich nicht vorgesehen. | M2 | bestätigt |

### 3.4 Systeme, KI & Technik

| Begriff | Erklärung | Quelle | Status |
|---|---|---|---|
| **Demonstrator** | Prototypische Umsetzung des Szenarios (Form – App oder Webapplikation – wurde am 05.10. diskutiert). | T, M1 | bestätigt |
| **Testbed** | Technische Umgebung des Projekts (AAS-Environment, ERP, Influx, Prozess- und Produktdaten). | S | bestätigt |
| **AI Chat Bot** | KI-Assistent, mit dem der Kunde direkt auf den Daten arbeitet (RMA-Prozess, Traceability). | S, M2 | bestätigt |
| **Ontologie** | Formale Beschreibung von Begriffen und Beziehungen; soll Traceability mit dem Chat Bot unterstützen. | S | bestätigt |
| **Mock-Daten („gemoggt")** | Simulierte Daten, wo reale Daten fehlen (z. B. Klebstoffdaten, falls keine Antwort der TU). | M2 | Annahme |
| **Anbindung an externe Services** | Integration externer Systeme, evtl. via MCP. | M1 | offen |
| **Prozessdaten / Produktdaten** | Zeitreihen aus dem Prozess (Influx) bzw. Stammdaten zum Produkt. | S | bestätigt |
| **Standardabweichung** | Statistische Streuung zur Erzeugung realistischer Prozessabweichungen. | M2 | bestätigt |

### 3.5 Tools & Frameworks

| Name | Zweck | Quelle |
|---|---|---|
| **AAS Package Explorer** | Erstellen und Bearbeiten von AAS | S |
| **IDTA AASX Server** | Laufzeitumgebung für AAS (IDTA e. V.) | S |
| **BaSyx** | Laufzeitumgebung für AAS (Fraunhofer IESE) | S |
| **FA³ST** | Laufzeitumgebung für AAS (Fraunhofer IOSB) | S |
| **ECLASS Content Suche** | Suche nach standardisierten Referenzen | S |
| **GitLab** | Dokumentation und Versionierung (z. B. als `*.md`) | S |
| **Semiconductor-X** | Initiative zur Überführung der Semi-Normen in AAS | S |

---

## 4. Offene Punkte

| # | Frage | Wer klärt? |
|---|---|---|
| 1 | Was bedeutet **„Jumi"** (Handling-Unit)? | Betreuer / Paul |
| 2 | Ist **„gemoggt"** = *gemockt*? Welche Daten werden gemockt, wenn von der TU nichts kommt? | Team |
| 3 | Ist **MCP** = Model Context Protocol? „Reicht ein MCP?" | Team |
| 4 | Schreibweise **DMP**: *Material Pass* vs. *Materialpass* – Vorschlag siehe 1.3 | Team |
| 5 | Welche Abkürzung für TU Dresden: *TU* oder *TUD*? | Team |
| 6 | **RMA** bestätigt? (Rolle im Szenario: Kunde reklamiert, Daten werden analysiert) | Team |
| 7 | Sprache des Glossars: aktuell deutsch mit englischen Fachbegriffen | Team |

---

## 5. Pflege

- Datei: `docs/glossary.md` im GitLab-Repository
- Neue Begriffe per Merge Request oder direkt eintragen (Quelle + Status angeben)
- Bei jedem Meeting: neue Abkürzungen aus den Notizen hier ergänzen
- Alphabetische Sortierung in Abschnitt 2 beibehalten
