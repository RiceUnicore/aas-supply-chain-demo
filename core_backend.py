"""
core_backend.py (Kompatibel mit mcp 2.x MCPServer & Python 3.14)
Vollständiges FastAPI-Backend inkl. AAS-Extraktion, InfluxDB-Zeitreihen,
DPP-Generator, MCP-Server (mcp 2.x) und reaktivem KI-Chatbot-Webinterface.
"""

import hashlib
import inspect
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Unterstützung für mcp 2.x (MCPServer) sowie Fallback für mcp 1.x (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("HTW-SupplyChain-MCP")
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("HTW-SupplyChain-MCP")

# Optionaler InfluxDB-Client (fällt automatisch auf Simulation zurück, falls DB offline)
try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUX_LIB_AVAILABLE = True
except ImportError:
    INFLUX_LIB_AVAILABLE = False

app = FastAPI(title="HTW Core Backend + MCP 2.x Chatbot", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_TOKEN = "htw-secret-influx-token-2026"
INFLUX_ORG = "htw-dresden"
INFLUX_BUCKET = "process-data"

# Optional: Lokales LLM (Ollama) für freie Textformulierung
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


# =====================================================================
# 1. DEINE BESTEHENDE AAS-SHELL (DMP DES KLEBSTOFFS)
# =====================================================================
EXISTING_DMP_AAS = {
    "assetAdministrationShells": [
        {
            "modelType": "AssetAdministrationShell",
            "idShort": "AAS_Adhesive_1049281_CH-2610-412",
            "id": "https://chemtech-solutions.de/ids/aas/1049281/CH-2610-412",
            "assetInformation": {
                "assetKind": "Instance",
                "globalAssetId": "https://chemtech-solutions.de/ids/asset/1049281_CH-2610-412"
            }
        }
    ],
    "submodels": [
        {
            "modelType": "Submodel",
            "idShort": "Nameplate_ERP",
            "id": "https://chemtech-solutions.de/ids/sm/nameplate_erp/CH-2610-412",
            "submodelElements": [
                {"modelType": "Property", "idShort": "MATNR", "valueType": "xs:string", "value": "000000000001049281"},
                {"modelType": "Property", "idShort": "MAKTX", "valueType": "xs:string", "value": "StructaBond 4K-Epoxid Strukturkleber"},
                {"modelType": "Property", "idShort": "CHARG", "valueType": "xs:string", "value": "CH-2610-412"},
                {"modelType": "Property", "idShort": "ManufacturerName", "valueType": "xs:string", "value": "ChemTech Solutions GmbH (TUD Stub)"}
            ]
        },
        {
            "modelType": "Submodel",
            "idShort": "DigitalMaterialPass",
            "id": "https://chemtech-solutions.de/ids/sm/dmp/CH-2610-412",
            "submodelElements": [
                {"modelType": "Property", "idShort": "CuringTemperature_Celsius", "valueType": "xs:double", "value": "175.0"},
                {"modelType": "Property", "idShort": "MinTemperature_Celsius", "valueType": "xs:double", "value": "165.0"},
                {"modelType": "Property", "idShort": "MaxTemperature_Celsius", "valueType": "xs:double", "value": "190.0"},
                {"modelType": "Property", "idShort": "CuringDuration_Minutes", "valueType": "xs:integer", "value": "22"},
                {"modelType": "Property", "idShort": "Viscosity_Pas", "valueType": "xs:integer", "value": "1280"},
                {"modelType": "Property", "idShort": "ProductCarbonFootprint_kgCO2e", "valueType": "xs:double", "value": "1.88"},
                {"modelType": "Property", "idShort": "RecycledContent_Percent", "valueType": "xs:double", "value": "24.0"}
            ]
        }
    ]
}


# =====================================================================
# 2. AAS-EXTRAKTION & INFLUXDB-ZEITREIHEN-ABFRAGE
# =====================================================================
def extract_from_aas(aas_env: dict, submodel_id_short: str, prop_id_short: str) -> Optional[str]:
    for sm in aas_env.get("submodels", []):
        if sm.get("idShort") == submodel_id_short:
            for elem in sm.get("submodelElements", []):
                if elem.get("idShort") == prop_id_short:
                    return elem.get("value")
    return None


def parse_dmp_parameters() -> dict:
    raw_json = json.dumps(EXISTING_DMP_AAS, sort_keys=True).encode("utf-8")
    snapshot_hash = hashlib.sha256(raw_json).hexdigest()
    return {
        "matnr": extract_from_aas(EXISTING_DMP_AAS, "Nameplate_ERP", "MATNR"),
        "maktx": extract_from_aas(EXISTING_DMP_AAS, "Nameplate_ERP", "MAKTX"),
        "lot_id": extract_from_aas(EXISTING_DMP_AAS, "Nameplate_ERP", "CHARG"),
        "manufacturer": extract_from_aas(EXISTING_DMP_AAS, "Nameplate_ERP", "ManufacturerName"),
        "target_temp_c": float(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "CuringTemperature_Celsius") or 175.0),
        "min_temp_c": float(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "MinTemperature_Celsius") or 165.0),
        "max_temp_c": float(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "MaxTemperature_Celsius") or 190.0),
        "curing_duration_min": int(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "CuringDuration_Minutes") or 22),
        "viscosity_pas": int(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "Viscosity_Pas") or 1280),
        "pcf_kg_co2e": float(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "ProductCarbonFootprint_kgCO2e") or 1.88),
        "recycled_pct": float(extract_from_aas(EXISTING_DMP_AAS, "DigitalMaterialPass", "RecycledContent_Percent") or 24.0),
        "dmp_aas_id": EXISTING_DMP_AAS["assetAdministrationShells"][0]["id"],
        "dmp_sha256": snapshot_hash
    }


def query_influx_process_data(unit_id: str) -> dict:
    """
    Holt die Ofen-Zeitreihen aus der InfluxDB (und schreibt sie beim ersten Aufruf hinein).
    - U-1042: Fehlerfall (8 Minuten Temperaturabfall auf 161.2 °C -> unter DMP-Limit 165 °C,
              aber über HTW-Ausschussgrenze 158 °C -> Feldausfall beim Kunden).
    - Andere Units (z. B. U-1043): Optimaler Durchlauf bei ~175.0 °C.
    """
    dmp = parse_dmp_parameters()
    duration = dmp["curing_duration_min"]
    target = dmp["target_temp_c"]
    min_limit = dmp["min_temp_c"]
    max_limit = dmp["max_temp_c"]
    run_id = "RUN-2026-88" if unit_id.upper() == "U-1042" else "RUN-2026-99"

    base_time = datetime.now(timezone.utc) - timedelta(minutes=duration)
    series = []
    for minute in range(duration):
        ts = (base_time + timedelta(minutes=minute)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if unit_id.upper() == "U-1042" and 10 <= minute < 18:
            temp = 161.2  # 8 Min. Unterschreitung des DMP-Mindestwerts
        else:
            temp = round(target + ((minute % 3) - 1) * 0.4, 1)
        series.append({"minute": minute + 1, "timestamp": ts, "temperature_c": temp})

    influx_source = "InfluxDB Simulation (Fallback aktiv, da Port 8086 offline)"
    if INFLUX_LIB_AVAILABLE:
        try:
            client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=1200)
            if client.ping():
                write_api = client.write_api(write_options=SYNCHRONOUS)
                points = [
                    Point("oven_curing")
                    .tag("unitId", unit_id.upper())
                    .tag("runId", run_id)
                    .tag("supplierLotId", dmp["lot_id"])
                    .field("temperature_c", float(pt["temperature_c"]))
                    .time(pt["timestamp"], WritePrecision.S)
                    for pt in series
                ]
                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)
                influx_source = f"Live InfluxDB ({INFLUX_URL}, Bucket: {INFLUX_BUCKET})"
            client.close()
        except Exception:
            pass

    temps = [pt["temperature_c"] for pt in series]
    min_t, max_t = min(temps), max(temps)
    mean_t = round(sum(temps) / len(temps), 2)
    mins_below = sum(1 for t in temps if t < min_limit)
    mins_above = sum(1 for t in temps if t > max_limit)
    mins_outside = mins_below + mins_above

    htw_scrap_limit = 158.0
    decision = "SCRAP" if min_t < htw_scrap_limit else ("SELLABLE_WITH_TOLERANCE" if mins_outside > 0 else "PASS_OPTIMAL")

    return {
        "unit_id": unit_id.upper(),
        "run_id": run_id,
        "influx_source": influx_source,
        "min_temp_c": min_t,
        "max_temp_c": max_t,
        "mean_temp_c": mean_t,
        "minutes_below_dmp_limit": mins_below,
        "minutes_outside_window": mins_outside,
        "htw_scrap_threshold_c": htw_scrap_limit,
        "quality_decision": decision,
        "time_series": series
    }


def build_dpp_aas(unit_id: str) -> dict:
    """Erstellt aus der AAS-Shell (DMP) + InfluxDB-Daten den Digitalen Produktpass (DPP)."""
    unit_id = unit_id.upper()
    dmp = parse_dmp_parameters()
    kpis = query_influx_process_data(unit_id)
    total_pcf = round(dmp["pcf_kg_co2e"] + 0.42, 2)

    return {
        "assetAdministrationShells": [
            {
                "modelType": "AssetAdministrationShell",
                "idShort": f"DPP_HTW_Product_{unit_id}",
                "id": f"https://htw-dresden.de/ids/aas/dpp/{unit_id}",
                "assetInformation": {
                    "assetKind": "Instance",
                    "globalAssetId": f"https://htw-dresden.de/ids/asset/sensor_housing_{unit_id}",
                    "specificAssetIds": [
                        {"name": "unitId", "value": unit_id},
                        {"name": "runId", "value": kpis["run_id"]},
                        {"name": "supplierLotId", "value": dmp["lot_id"]}
                    ]
                }
            }
        ],
        "submodels": [
            {
                "modelType": "Submodel",
                "idShort": "Nameplate",
                "id": f"https://htw-dresden.de/ids/sm/nameplate/{unit_id}",
                "submodelElements": [
                    {"modelType": "Property", "idShort": "ProductUnitId", "valueType": "xs:string", "value": unit_id},
                    {"modelType": "Property", "idShort": "ProductName", "valueType": "xs:string", "value": "HTW Smart-Sensorgehäuse (Geklebt)"},
                    {"modelType": "Property", "idShort": "ManufacturerName", "valueType": "xs:string", "value": "HTW Dresden - Diskrete Fertigung"}
                ]
            },
            {
                "modelType": "Submodel",
                "idShort": "MaterialInputs",
                "id": f"https://htw-dresden.de/ids/sm/material_inputs/{unit_id}",
                "submodelElements": [
                    {"modelType": "Property", "idShort": "SupplierMaterialName", "valueType": "xs:string", "value": dmp["maktx"]},
                    {"modelType": "Property", "idShort": "SupplierMaterialNumber_MATNR", "valueType": "xs:string", "value": dmp["matnr"]},
                    {"modelType": "Property", "idShort": "SupplierLotId", "valueType": "xs:string", "value": dmp["lot_id"]},
                    {"modelType": "Property", "idShort": "DmpAasReference", "valueType": "xs:string", "value": dmp["dmp_aas_id"]},
                    {"modelType": "Property", "idShort": "DmpSnapshotSha256", "valueType": "xs:string", "value": dmp["dmp_sha256"]}
                ]
            },
            {
                "modelType": "Submodel",
                "idShort": "ProductionProcess",
                "id": f"https://htw-dresden.de/ids/sm/production_process/{unit_id}",
                "submodelElements": [
                    {"modelType": "Property", "idShort": "ProductionRunId", "valueType": "xs:string", "value": kpis["run_id"]},
                    {"modelType": "Property", "idShort": "DataSource", "valueType": "xs:string", "value": kpis["influx_source"]},
                    {"modelType": "Property", "idShort": "TargetCuringTemp_Celsius", "valueType": "xs:double", "value": str(dmp["target_temp_c"])},
                    {"modelType": "Property", "idShort": "AllowedWindowMin_Celsius", "valueType": "xs:double", "value": str(dmp["min_temp_c"])},
                    {"modelType": "Property", "idShort": "MeasuredMinTemp_Celsius", "valueType": "xs:double", "value": str(kpis["min_temp_c"])},
                    {"modelType": "Property", "idShort": "MeasuredMaxTemp_Celsius", "valueType": "xs:double", "value": str(kpis["max_temp_c"])},
                    {"modelType": "Property", "idShort": "MeasuredMeanTemp_Celsius", "valueType": "xs:double", "value": str(kpis["mean_temp_c"])},
                    {"modelType": "Property", "idShort": "TimeOutsideWindow_Minutes", "valueType": "xs:integer", "value": str(kpis["minutes_outside_window"])},
                    {"modelType": "Property", "idShort": "QualityDecision", "valueType": "xs:string", "value": kpis["quality_decision"]}
                ]
            },
            {
                "modelType": "Submodel",
                "idShort": "CarbonFootprint",
                "id": f"https://htw-dresden.de/ids/sm/pcf/{unit_id}",
                "submodelElements": [
                    {"modelType": "Property", "idShort": "AdhesiveUpstreamPCF_kgCO2e", "valueType": "xs:double", "value": str(dmp["pcf_kg_co2e"])},
                    {"modelType": "Property", "idShort": "TotalProductPCF_kgCO2e", "valueType": "xs:double", "value": str(total_pcf)},
                    {"modelType": "Property", "idShort": "AdhesiveRecycledContent_Percent", "valueType": "xs:double", "value": str(dmp["recycled_pct"])}
                ]
            }
        ]
    }


# =====================================================================
# 3. REGISTRIERTE MCP-DOMÄNEN-TOOLS (MCPServer v2.x kompatibel)
# =====================================================================
MCP_TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_mcp_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Registriert die Funktion sowohl im MCPServer (mcp 2.x) als auch für den lokalen Agent-Dispatcher."""
    MCP_TOOL_REGISTRY[func.__name__] = func
    try:
        mcp.tool()(func)
    except Exception:
        pass
    return func


async def invoke_mcp_tool(tool_name: str, **kwargs) -> Any:
    """Ruft ein registriertes MCP-Tool über den MCP-Server bzw. die Tool-Registry auf."""
    func = MCP_TOOL_REGISTRY[tool_name]
    if inspect.iscoroutinefunction(func):
        return await func(**kwargs)
    return func(**kwargs)


@register_mcp_tool
def get_dpp(unit_id: str = "U-1042") -> dict:
    """Gibt den vollständigen Digitalen Produktpass (DPP) eines HTW-Bauteils zurück."""
    return build_dpp_aas(unit_id)


@register_mcp_tool
def get_process_window(lot_id: str = "CH-2610-412") -> dict:
    """Liest das zulässige Prozessfenster aus dem Digitalen Materialpass (DMP) der Klebstoff-Charge."""
    dmp = parse_dmp_parameters()
    return {
        "supplierLotId": dmp["lot_id"],
        "materialName": dmp["maktx"],
        "targetTemp_C": dmp["target_temp_c"],
        "minTemp_C": dmp["min_temp_c"],
        "maxTemp_C": dmp["max_temp_c"],
        "curingDuration_Min": dmp["curing_duration_min"],
        "viscosity_Pas": dmp["viscosity_pas"]
    }


@register_mcp_tool
def trace_backward(unit_id: str = "U-1042") -> dict:
    """Verfolgt ein Bauteil rückwärts über den Produktionslauf (InfluxDB) bis zur Klebstoff-Charge (DMP)."""
    dmp = parse_dmp_parameters()
    kpis = query_influx_process_data(unit_id)
    return {
        "unitId": unit_id.upper(),
        "runId": kpis["run_id"],
        "supplierLotId": dmp["lot_id"],
        "material": dmp["maktx"],
        "dmpSnapshotSha256": dmp["dmp_sha256"],
        "influxSource": kpis["influx_source"],
        "qualityDecision": kpis["quality_decision"]
    }


@register_mcp_tool
def compare_to_window(unit_id: str = "U-1042") -> dict:
    """Vergleicht die InfluxDB-Ofenkurve eines Bauteils mit dem DMP-Prozessfenster zur Fehleranalyse."""
    dmp = parse_dmp_parameters()
    kpis = query_influx_process_data(unit_id)
    return {
        "unitId": unit_id.upper(),
        "runId": kpis["run_id"],
        "supplierLotId": dmp["lot_id"],
        "dmpAllowedWindow_C": [dmp["min_temp_c"], dmp["max_temp_c"]],
        "measuredMinTemp_C": kpis["min_temp_c"],
        "measuredMaxTemp_C": kpis["max_temp_c"],
        "measuredMeanTemp_C": kpis["mean_temp_c"],
        "minutesBelowDmpLimit": kpis["minutes_below_dmp_limit"],
        "htwScrapThreshold_C": kpis["htw_scrap_threshold_c"],
        "qualityDecision": kpis["quality_decision"],
        "aasElementPaths": {
            "dmpMinTemp": "DigitalMaterialPass/MinTemperature_Celsius",
            "dppMeasuredMin": "ProductionProcess/MeasuredMinTemp_Celsius",
            "dppTimeOutside": "ProductionProcess/TimeOutsideWindow_Minutes"
        }
    }


# =====================================================================
# 4. REAKTIVER KI-AGENT (entscheidet anhand der Frage, welche MCP-Tools laufen)
# =====================================================================
class ChatRequest(BaseModel):
    message: str


async def try_ollama_formatting(user_msg: str, tool_results: dict) -> Optional[str]:
    """Falls lokal Ollama läuft, formuliert das Sprachmodell die Antwort aus den MCP-Daten."""
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            prompt = (
                f"Du bist der HTW Supply-Chain Traceability-Agent. Beantworte die Frage des Nutzers "
                f"präzise auf Deutsch anhand dieser MCP-Tool-Daten und nenne die exakten IDs und Werte:\n"
                f"{json.dumps(tool_results, ensure_ascii=False)}\n\nFrage: {user_msg}"
            )
            resp = await client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False}
            )
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content")
    except Exception:
        return None
    return None


@app.post("/api/chat")
async def reactive_ai_chat(req: ChatRequest):
    msg_lower = req.message.lower()
    unit_id = "U-1043" if "1043" in msg_lower else "U-1042"
    lot_id = "CH-2610-412"

    called_tools = []
    tool_outputs = {}
    dpp_data = None

    if any(k in msg_lower for k in ["warum", "fehler", "ausgefallen", "ausfall", "trace", "ursache", "rma", "prüf", "problem"]):
        trace_res = await invoke_mcp_tool("trace_backward", unit_id=unit_id)
        comp_res = await invoke_mcp_tool("compare_to_window", unit_id=unit_id)
        dpp_data = await invoke_mcp_tool("get_dpp", unit_id=unit_id)

        called_tools = [
            f"MCPServer.call_tool('trace_backward', unit_id='{unit_id}')",
            f"MCPServer.call_tool('compare_to_window', unit_id='{unit_id}')",
            f"MCPServer.call_tool('get_dpp', unit_id='{unit_id}')"
        ]
        tool_outputs = {"trace_backward": trace_res, "compare_to_window": comp_res}

        if comp_res["minutesBelowDmpLimit"] > 0:
            reply = (
                f"🔍 **RMA-Ursachenanalyse für Bauteil `{unit_id}` abgeschlossen:**\n\n"
                f"• **Rückverfolgung (Genealogie):** Gefertigt in Produktionslauf `{trace_res['runId']}` "
                f"mit Klebstoff **{trace_res['material']}** (Charge `{trace_res['supplierLotId']}`).\n"
                f"• **Soll-Prozessfenster (aus DMP-AAS):** `{comp_res['dmpAllowedWindow_C'][0]} °C` bis `{comp_res['dmpAllowedWindow_C'][1]} °C` "
                f"(Pfad: `{comp_res['aasElementPaths']['dmpMinTemp']}`).\n"
                f"• **Ist-Messung (aus InfluxDB):** Während der Aushärtung fiel die Ofentemperatur für "
                f"**{comp_res['minutesBelowDmpLimit']} Minuten** auf **`{comp_res['measuredMinTemp_C']} °C`** ab "
                f"(Pfad: `{comp_res['aasElementPaths']['dppMeasuredMin']}`).\n"
                f"• **Warum nicht aussortiert?** Da `{comp_res['measuredMinTemp_C']} °C` noch über der internen HTW-Ausschussgrenze "
                f"von `{comp_res['htwScrapThreshold_C']} °C` lag, wurde das Bauteil als `{comp_res['qualityDecision']}` freigegeben. "
                f"Die unvollständige Vernetzung hat beim Kunden zum Feldausfall geführt."
            )
        else:
            reply = (
                f"✅ **Prüfung für Bauteil `{unit_id}` (Lauf `{trace_res['runId']}`):**\n\n"
                f"Alle InfluxDB-Messwerte (`{comp_res['measuredMinTemp_C']} °C` bis `{comp_res['measuredMaxTemp_C']} °C`) "
                f"lagen zu 100 % innerhalb des DMP-Prozessfensters (`165.0 – 190.0 °C`). Status: `{comp_res['qualityDecision']}`."
            )

    elif any(k in msg_lower for k in ["fenster", "window", "temperatur", "dmp", "kleber", "klebstoff", "charge"]):
        win_res = await invoke_mcp_tool("get_process_window", lot_id=lot_id)
        called_tools = [f"MCPServer.call_tool('get_process_window', lot_id='{lot_id}')"]
        tool_outputs = {"get_process_window": win_res}
        reply = (
            f"🧪 **Prozessfenster aus dem Digitalen Materialpass (Charge `{lot_id}`):**\n\n"
            f"• **Material:** {win_res['materialName']}\n"
            f"• **Soll-Aushärtetemperatur:** `{win_res['targetTemp_C']} °C` (Erlaubtes Fenster: `{win_res['minTemp_C']} – {win_res['maxTemp_C']} °C`)\n"
            f"• **Aushärtedauer:** `{win_res['curingDuration_Min']} Minuten`\n"
            f"• **Viskosität:** `{win_res['viscosity_Pas']} Pa·s`"
        )

    else:
        dpp_data = await invoke_mcp_tool("get_dpp", unit_id=unit_id)
        kpis = query_influx_process_data(unit_id)
        called_tools = [f"MCPServer.call_tool('get_dpp', unit_id='{unit_id}')"]
        tool_outputs = {"get_dpp_summary": kpis}
        reply = (
            f"📦 **Digitaler Produktpass (DPP) für Bauteil `{unit_id}` wurde aus AAS + InfluxDB generiert:**\n\n"
            f"• **AAS-ID:** `{dpp_data['assetAdministrationShells'][0]['id']}`\n"
            f"• **Verwendete Klebstoff-Charge:** `CH-2610-412` (SHA-256 Snapshot im Submodel `MaterialInputs` hinterlegt)\n"
            f"• **InfluxDB-Prozessdaten (`{kpis['run_id']}`):** Min: `{kpis['min_temp_c']} °C` | Mittel: `{kpis['mean_temp_c']} °C` | "
            f"Zeit außerhalb DMP-Fenster: `{kpis['minutes_outside_window']} min`\n"
            f"• **Qualitätsstatus:** `{kpis['quality_decision']}`\n\n"
            f"👉 *Der vollständige DPP im AAS-JSON-Format wurde rechts im Inspector geladen.*"
        )

    llm_text = await try_ollama_formatting(req.message, tool_outputs)
    if llm_text:
        reply = llm_text

    return JSONResponse({
        "reply": reply,
        "mcp_tools_called": called_tools,
        "unit_id": unit_id,
        "dpp": dpp_data or build_dpp_aas(unit_id)
    })


@app.get("/api/dpp/{unit_id}")
async def api_get_dpp(unit_id: str = "U-1042"):
    return build_dpp_aas(unit_id)


# =====================================================================
# 5. REAKTIVE CHATBOT-WEBOBERFLÄCHE (Direkt unter http://127.0.0.1:8000)
# =====================================================================
CHATBOT_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>HTW Dresden | MCP 2.x KI-Chatbot & DPP Inspector</title>
<style>
  :root {
    --bg: #0b1120; --panel: #151f32; --card: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --cyan: #06b6d4; --green: #10b981; --amber: #f59e0b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; height: 100vh; display: flex; flex-direction: column; }
  header { background: #0f172a; border-bottom: 1px solid var(--border); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; }
  header h1 { font-size: 1.15rem; }
  .badge { background: rgba(6,182,212,0.15); border: 1px solid var(--cyan); color: var(--cyan); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
  .layout { display: grid; grid-template-columns: 1.15fr 1fr; gap: 16px; padding: 16px 24px; flex: 1; overflow: hidden; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; display: flex; flex-direction: column; overflow: hidden; }
  .panel-head { padding: 12px 16px; background: rgba(30,41,59,0.8); border-bottom: 1px solid var(--border); font-weight: 600; font-size: 0.95rem; display: flex; justify-content: space-between; }
  .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
  .msg { max-width: 88%; padding: 12px 14px; border-radius: 10px; font-size: 0.9rem; line-height: 1.5; white-space: pre-wrap; }
  .msg.user { align-self: flex-end; background: #0284c7; color: #fff; border-bottom-right-radius: 2px; }
  .msg.bot { align-self: flex-start; background: var(--card); border: 1px solid var(--border); border-bottom-left-radius: 2px; }
  .mcp-trace { margin-top: 8px; padding: 6px 10px; background: #090d16; border-left: 3px solid var(--amber); font-family: monospace; font-size: 0.76rem; color: var(--amber); border-radius: 4px; }
  .quick-prompts { padding: 8px 16px; display: flex; gap: 8px; flex-wrap: wrap; border-top: 1px solid var(--border); background: #0f172a; }
  .chip { background: var(--card); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 6px; font-size: 0.78rem; cursor: pointer; }
  .chip:hover { border-color: var(--cyan); color: var(--cyan); }
  .chat-input { display: flex; padding: 12px 16px; gap: 10px; border-top: 1px solid var(--border); background: #0f172a; }
  .chat-input input { flex: 1; background: var(--card); border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 6px; outline: none; }
  .chat-input button { background: var(--cyan); color: #000; font-weight: 700; border: none; padding: 0 18px; border-radius: 6px; cursor: pointer; }
  pre.json-view { flex: 1; background: #090d16; padding: 14px; overflow: auto; font-family: 'Cascadia Code', Consolas, monospace; font-size: 0.78rem; line-height: 1.45; color: #a7f3d0; }
</style>
</head>
<body>
<header>
  <div style="display:flex; align-items:center; gap:12px;">
    <span class="badge">MCP 2.x + FastAPI + InfluxDB</span>
    <h1>HTW Cross-Domain Supply Chain · Reaktiver KI-Chatbot (RMA & DPP)</h1>
  </div>
  <span style="font-size:0.8rem; color:var(--muted);">Zone HTW: agent ↔ core (MCPServer Tools)</span>
</header>

<div class="layout">
  <section class="panel">
    <div class="panel-head">
      <span>🤖 Reaktiver Traceability- & DPP-Chatbot</span>
      <span style="color:var(--green); font-size:0.8rem;">● MCPServer 2.x aktiv</span>
    </div>
    <div class="chat-messages" id="chat-box">
      <div class="msg bot">Hallo! Ich bin der reaktive KI-Agent der HTW Dresden. Ich habe über <b>MCPServer-Tools (v2.x)</b> lesenden Zugriff auf deine Klebstoff-AAS (DMP), die InfluxDB-Ofendaten und den DPP-Generator.

Klicke unten auf einen Schnellbefehl oder stelle mir eine Frage im Chat!</div>
    </div>
    <div class="quick-prompts">
      <button class="chip" onclick="sendQuick('Gib mir den generierten DPP für Bauteil U-1042 aus')">📦 DPP für Bauteil U-1042 abrufen</button>
      <button class="chip" onclick="sendQuick('Bauteil U-1042 ist beim Kunden ausgefallen. Warum?')">🔍 Warum ist U-1042 ausgefallen? (RMA-Trace)</button>
      <button class="chip" onclick="sendQuick('Wie sieht das Prozessfenster im DMP für Charge CH-2610-412 aus?')">🧪 DMP-Prozessfenster abfragen</button>
      <button class="chip" onclick="sendQuick('Prüfe das fehlerfreie Vergleichsbauteil U-1043')">✅ Bauteil U-1043 prüfen</button>
    </div>
    <form class="chat-input" onsubmit="handleChatSubmit(event)">
      <input type="text" id="user-input" placeholder="Frage stellen, z.B.: Warum ist Bauteil U-1042 ausgefallen?" autocomplete="off" />
      <button type="submit">Senden</button>
    </form>
  </section>

  <section class="panel">
    <div class="panel-head">
      <span>📄 Vom Backend + InfluxDB generierter DPP (AAS V3 JSON)</span>
      <span id="dpp-unit-badge" style="color:var(--cyan); font-family:monospace;">Noch kein Abruf</span>
    </div>
    <pre class="json-view" id="dpp-json-box">// Sobald du den Chatbot links nach einem Bauteil (z. B. U-1042) fragst,
// ruft der Agent reaktiv das MCP-Tool auf, fusioniert die AAS-DMP-Daten
// mit den InfluxDB-Zeitreihen und gibt den Digitalen Produktpass (DPP) hier aus.</pre>
  </section>
</div>

<script>
  const chatBox = document.getElementById('chat-box');
  const userInput = document.getElementById('user-input');
  const dppJsonBox = document.getElementById('dpp-json-box');
  const dppBadge = document.getElementById('dpp-unit-badge');

  function appendMessage(text, role, mcpTools = []) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.innerHTML = text.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>').replace(/`(.*?)`/g, '<code style="color:#38bdf8;">$1</code>');
    if (mcpTools.length > 0) {
      const trace = document.createElement('div');
      trace.className = 'mcp-trace';
      trace.innerHTML = '⚡ <b>Ausgeführte MCP-Tool-Calls:</b><br>' + mcpTools.join('<br>');
      div.appendChild(trace);
    }
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendMessage(text) {
    appendMessage(text, 'user');
    userInput.value = '';
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      appendMessage(data.reply, 'bot', data.mcp_tools_called || []);
      if (data.dpp) {
        dppBadge.textContent = 'DPP: ' + data.unit_id;
        dppJsonBox.textContent = JSON.stringify(data.dpp, null, 2);
      }
    } catch (err) {
      appendMessage('Fehler bei der Anfrage an das Backend: ' + err.message, 'bot');
    }
  }

  function handleChatSubmit(e) {
    e.preventDefault();
    if (userInput.value.trim()) sendMessage(userInput.value.trim());
  }

  function sendQuick(text) {
    sendMessage(text);
  }
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def serve_chatbot_ui():
    return CHATBOT_HTML


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starte HTW Core-Backend + MCP 2.x Chatbot auf http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)