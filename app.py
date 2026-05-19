
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import hmac

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================
st.set_page_config(
    page_title="OXXO CEDIS · Digital Twin V4.4",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NOW = datetime.now()

# ==================================================
# LOGIN CON STREAMLIT SECRETS
# ==================================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    st.title("Acceso al Dashboard")
    st.caption("Ingresa usuario y contraseña para visualizar el Digital Twin.")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        users = st.secrets["users"]

        if username in users and hmac.compare_digest(password, users[username]):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    return False


if not check_login():
    st.stop()

# ==================================================
# CSS GLOBAL
# ==================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    h1, h2, h3 {
        letter-spacing: -0.03em;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }

    div[data-baseweb="select"] > div {
        border-radius: 12px;
    }

    .section-caption {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: -0.3rem;
        margin-bottom: 1rem;
    }

    .kpi-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    .kpi-card h4 {
        font-size: 0.85rem;
        color: #6b7280;
        margin: 0 0 8px 0;
        font-weight: 600;
    }

    .kpi-card .value {
        font-size: 2rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .kpi-card .delta-good {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        color: #047857;
        background: #d1fae5;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .kpi-card .delta-warn {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        color: #b45309;
        background: #fef3c7;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .kpi-card .delta-bad {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        color: #b91c1c;
        background: #fee2e2;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .soft-panel {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }

    /* Fix: tabs were visually cropped at the top in some browser zoom sizes */
    div[data-testid="stTabs"] {
        overflow: visible !important;
        margin-top: 0.8rem;
    }

    div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
        min-height: 58px !important;
        overflow: visible !important;
        align-items: center !important;
        padding-top: 10px !important;
        padding-bottom: 8px !important;
        gap: 8px !important;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        min-height: 48px !important;
        height: auto !important;
        padding: 12px 18px !important;
        overflow: visible !important;
        border-radius: 12px 12px 0 0 !important;
        white-space: nowrap !important;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"] p {
        font-size: 1rem !important;
        line-height: 1.35rem !important;
        margin: 0 !important;
        overflow: visible !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# DATOS SIMULADOS
# ==================================================
@st.cache_data
def generate_mock_data(seed: int = 19, days_history: int = 45):
    random.seed(seed)

    receiving_a = [f"RA-{i}" for i in range(1, 17)]
    shipping = [f"S-{i}" for i in range(1, 13)]
    receiving_b = [f"RB-{i}" for i in range(1, 13)]

    zones = {
        "Receiving A": receiving_a,
        "Shipping Docks": shipping,
        "Receiving B": receiving_b,
    }

    all_doors = []
    for zone, doors in zones.items():
        for door in doors:
            all_doors.append({"Puerta": door, "Zona": zone})

    door_master = pd.DataFrame(all_doors)

    today_status_weights = {
        "Disponible": 0.38,
        "Ocupada": 0.42,
        "Incidencia": 0.12,
        "Mantenimiento": 0.08,
    }

    door_state_rows = []
    for _, row in door_master.iterrows():
        status = random.choices(
            list(today_status_weights.keys()),
            weights=list(today_status_weights.values()),
            k=1,
        )[0]

        if status == "Disponible":
            truck_id = "-"
            supplier = "-"
            carrier = "-"
            activity = "Sin unidad"
            progress = 0
            wait_min = 0
            unload_min = 0
            pallets_plan = 0
            pallets_done = 0
        else:
            truck_id = f"CAM-{NOW.strftime('%m%d')}-{random.randint(1001, 1099)}"
            supplier = random.choice([
                "Proveedor Norte",
                "Proveedor Centro",
                "Proveedor Bajío",
                "Proveedor Valle",
                "Proveedor Occidente",
                "Proveedor Sureste",
            ])
            carrier = random.choice(["UNIGIS", "Fletera MX", "Transportes Alfa", "Logística Norte"])
            activity = random.choice([
                "Asignado",
                "Descargando",
                "En validación",
                "Liberación pendiente",
                "Documentación pendiente",
            ])
            progress = random.randint(8, 92)
            wait_min = random.randint(8, 90)
            unload_min = random.randint(20, 110)
            pallets_plan = random.randint(16, 30)
            pallets_done = int(pallets_plan * (progress / 100))

            if status == "Incidencia":
                activity = random.choice([
                    "Retraso de unidad",
                    "Diferencia de tarimas",
                    "Documentación incompleta",
                    "Rechazo calidad",
                    "Alerta RDM",
                ])
                progress = random.randint(15, 82)

        door_state_rows.append(
            {
                "Puerta": row["Puerta"],
                "Zona": row["Zona"],
                "Estado puerta": status,
                "Camión": truck_id,
                "Proveedor": supplier,
                "Transportista": carrier,
                "Actividad": activity,
                "% avance": progress,
                "Espera min": wait_min,
                "Descarga min": unload_min,
                "Tarimas plan": pallets_plan,
                "Tarimas recibidas": pallets_done,
                "Última actualización": (NOW - timedelta(minutes=random.randint(1, 35))).strftime("%H:%M"),
            }
        )

    door_state = pd.DataFrame(door_state_rows)

    # Histórico operativo
    records = []
    event_id = 1
    start_date = NOW.date() - timedelta(days=days_history - 1)

    operational_states = [
        "Programado",
        "Llegó",
        "En espera",
        "Asignado",
        "Descargando",
        "En validación",
        "Finalizado",
        "Con incidencia",
    ]

    for d in range(days_history):
        current_date = start_date + timedelta(days=d)
        daily_trucks = max(8, int(random.gauss(42, 8)))
        day_base = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=6)

        for i in range(daily_trucks):
            zone = random.choice(list(zones.keys()))
            door = random.choice(zones[zone])
            ts = day_base + timedelta(minutes=random.randint(0, 780))
            status = random.choices(
                operational_states,
                weights=[0.05, 0.07, 0.11, 0.13, 0.21, 0.12, 0.24, 0.07],
                k=1,
            )[0]

            wait = random.randint(4, 105)
            unload = random.randint(18, 125)
            pallets_plan = random.randint(14, 32)
            progress = 100 if status == "Finalizado" else random.randint(0, 95)
            pallets_done = int(pallets_plan * progress / 100)

            records.append(
                {
                    "ID evento": event_id,
                    "Timestamp": ts,
                    "Fecha": ts.date(),
                    "Hora": ts.strftime("%H:%M"),
                    "Zona": zone,
                    "Puerta": door,
                    "Camión": f"CAM-{current_date.strftime('%m%d')}-{1000+i}",
                    "Proveedor": random.choice([
                        "Proveedor Norte",
                        "Proveedor Centro",
                        "Proveedor Bajío",
                        "Proveedor Valle",
                        "Proveedor Occidente",
                        "Proveedor Sureste",
                    ]),
                    "Estado": status,
                    "Espera min": wait,
                    "Descarga min": unload,
                    "% avance": progress,
                    "Tarimas plan": pallets_plan,
                    "Tarimas recibidas": pallets_done,
                    "Fuera de horario": int(wait > 45 or random.random() < 0.08),
                    "Rechazo calidad": int(random.random() < 0.035),
                    "Rechazo plaga": int(random.random() < 0.015),
                    "Producto incompleto": int(random.random() < 0.045),
                    "Alerta RDM": int(status == "Con incidencia" or random.random() < 0.055),
                    "Config. incorrecta": int(random.random() < 0.035),
                    "Ajuste pendiente": int(random.random() < 0.055),
                    "Ocupación almacenaje %": round(random.uniform(70, 96), 1),
                }
            )
            event_id += 1

    hist = pd.DataFrame(records)
    return door_state, hist


door_df, history_df = generate_mock_data()

# ==================================================
# CLASIFICACIÓN DE INCIDENCIAS Y RESPONSABLES
# ==================================================
def classify_incident(activity: str, status: str):
    """
    Clasificación simulada para enriquecer el análisis individual.
    Cuando existan datos reales, se puede reemplazar por catálogo oficial OXXO/RDM.
    """
    if status != "Incidencia":
        return "Sin incidencia", "No requiere escalamiento", "Monitoreo operativo"

    activity_lower = str(activity).lower()

    if "calidad" in activity_lower or "rechazo" in activity_lower:
        return "Incidencia de calidad", "Responsable de Calidad", "Validar producto, documentar rechazo y notificar a abasto"
    if "tarima" in activity_lower or "diferencia" in activity_lower or "incompleta" in activity_lower:
        return "Diferencia de tarimas / cantidad", "Responsable de Inventarios / RDM", "Conciliar cantidades contra orden de compra y ajustar en sistema"
    if "document" in activity_lower or "factura" in activity_lower:
        return "Documentación incompleta", "Mesa de Control / Administración de recibo", "Solicitar documentos faltantes y bloquear liberación hasta validación"
    if "rdm" in activity_lower:
        return "Alerta RDM", "Responsable RDM / WMS", "Revisar alerta en sistema, validar configuración y cerrar seguimiento"
    if "retraso" in activity_lower or "unidad" in activity_lower or "espera" in activity_lower:
        return "Retraso de unidad / cita", "Coordinador de Patio / Tráfico", "Reprogramar ventana, actualizar prioridad y comunicar impacto operativo"
    if "plaga" in activity_lower:
        return "Incidencia de plaga", "Responsable de Inocuidad / Calidad", "Aislar unidad, registrar evidencia y activar protocolo de rechazo"

    return "Incidencia operativa", "Supervisor de Recibo", "Revisar causa raíz, asignar responsable y documentar cierre"


incident_info = door_df.apply(
    lambda r: classify_incident(r["Actividad"], r["Estado puerta"]),
    axis=1,
    result_type="expand",
)
door_df["Tipo incidencia"] = incident_info[0]
door_df["Responsable incidencia"] = incident_info[1]
door_df["Acción sugerida"] = incident_info[2]



# ==================================================
# FUNCIONES KPI
# ==================================================
def get_period_bounds(option, custom_value, current_time):
    today_start = datetime.combine(current_time.date(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    if option == "En vivo":
        return today_start, current_time, "En vivo · día actual hasta este momento"
    if option == "Hoy":
        return today_start, tomorrow_start, "Hoy"
    if option == "Ayer":
        return today_start - timedelta(days=1), today_start, "Ayer"
    if option == "Últimos 7 días":
        return current_time - timedelta(days=7), current_time, "Últimos 7 días"
    if option == "Semana pasada":
        start_this_week = today_start - timedelta(days=today_start.weekday())
        return start_this_week - timedelta(days=7), start_this_week, "Semana pasada"
    if option == "Rango personalizado":
        if isinstance(custom_value, tuple) and len(custom_value) == 2:
            start = datetime.combine(custom_value[0], datetime.min.time())
            end = datetime.combine(custom_value[1], datetime.min.time()) + timedelta(days=1)
            return start, end, f"{custom_value[0]} a {custom_value[1]}"
    return today_start, tomorrow_start, "Hoy"


def compute_kpis(df):
    total = len(df)
    completed = int((df["Estado"] == "Finalizado").sum()) if total else 0
    in_process = int(df["Estado"].isin(["Asignado", "Descargando", "En validación"]).sum()) if total else 0
    waiting = int((df["Estado"] == "En espera").sum()) if total else 0
    incidents = int(df["Alerta RDM"].sum() + df["Rechazo calidad"].sum() + df["Rechazo plaga"].sum() + df["Producto incompleto"].sum()) if total else 0
    late = int(df["Fuera de horario"].sum()) if total else 0
    avg_wait = round(float(df["Espera min"].mean()), 1) if total else 0
    avg_unload = round(float(df["Descarga min"].mean()), 1) if total else 0
    avg_stay = round(avg_wait + avg_unload + 25, 1) if total else 0
    planned_pallets = int(df["Tarimas plan"].sum()) if total else 0
    received_pallets = int(df["Tarimas recibidas"].sum()) if total else 0
    pallet_compliance = round((received_pallets / planned_pallets) * 100, 1) if planned_pallets else 0
    plan_adherence = round((completed + in_process) / total * 100, 1) if total else 0
    quality_score = round(max(0, 100 - ((incidents / max(1, total)) * 100)), 1) if total else 0
    storage = round(float(df["Ocupación almacenaje %"].mean()), 1) if total else 0

    return {
        "total": total,
        "completed": completed,
        "in_process": in_process,
        "waiting": waiting,
        "incidents": incidents,
        "late": late,
        "avg_wait": avg_wait,
        "avg_unload": avg_unload,
        "avg_stay": avg_stay,
        "planned_pallets": planned_pallets,
        "received_pallets": received_pallets,
        "pallet_compliance": pallet_compliance,
        "plan_adherence": plan_adherence,
        "quality_score": quality_score,
        "storage": storage,
    }


# ==================================================
# FILTRO TEMPORAL GLOBAL
# ==================================================
period_options = ["En vivo", "Hoy", "Ayer", "Últimos 7 días", "Semana pasada", "Rango personalizado"]

with st.sidebar:
    st.header("Parámetros")
    period_option = st.radio("Periodo", period_options, index=0)
    custom_dates = None
    if period_option == "Rango personalizado":
        custom_dates = st.date_input(
            "Rango",
            value=(NOW.date() - timedelta(days=7), NOW.date()),
        )

    st.divider()
    st.caption("Esta versión no usa imagen PNG. El plano se dibuja con HTML/CSS.")

period_start, period_end, period_label = get_period_bounds(period_option, custom_dates, NOW)
filtered_history = history_df[
    (history_df["Timestamp"] >= period_start) &
    (history_df["Timestamp"] < period_end)
].copy()

kpis = compute_kpis(filtered_history)


# ==================================================
# HTML DIGITAL TWIN
# ==================================================
def state_class(status):
    if status == "Disponible":
        return "free"
    if status == "Ocupada":
        return "occupied"
    if status == "Incidencia":
        return "issue"
    if status == "Mantenimiento":
        return "maintenance"
    return "free"


def create_light(door_id, status):
    return f"""
    <div class="dock-light {state_class(status)}" title="{door_id} · {status}"></div>
    """


def create_lights_for_zone(zone_name):
    zone_df = door_df[door_df["Zona"] == zone_name].copy()
    return "".join(create_light(r["Puerta"], r["Estado puerta"]) for _, r in zone_df.iterrows())


receiving_a_lights = create_lights_for_zone("Receiving A")
shipping_lights = create_lights_for_zone("Shipping Docks")
receiving_b_lights = create_lights_for_zone("Receiving B")


digital_twin_css = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: Inter, Arial, Helvetica, sans-serif;
    background: transparent;
}

/* ─── MARCO PRINCIPAL ─────────────────────────────────── */
.twin-frame {
    width: 100%;
    height: 660px;
    position: relative;
    overflow: hidden;
    border: 3px solid #1e293b;
    border-radius: 4px;
    background:
        linear-gradient(rgba(30,41,59,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,41,59,0.035) 1px, transparent 1px),
        #f8f6f0;
    background-size: 28px 28px;
}

/* ─── ETIQUETA OXXO ────────────────────────────────────── */
.oxxo-stamp {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.72rem;
    color: #64748b;
    letter-spacing: 0.12em;
    font-weight: 600;
}

/* ─── PARED EXTERIOR NORTE (top) ──────────────────────── */
.wall-north {
    position: absolute;
    left: 0; top: 0;
    width: 100%; height: 6px;
    background: #1e293b;
}
/* ─── PARED SUR ────────────────────────────────────────── */
.wall-south {
    position: absolute;
    left: 0; bottom: 72px;
    width: 100%; height: 5px;
    background: #1e293b;
}
/* ─── PARED OESTE ──────────────────────────────────────── */
.wall-west {
    position: absolute;
    left: 0; top: 0;
    width: 5px; height: calc(100% - 72px);
    background: #1e293b;
}
/* ─── PARED ESTE ───────────────────────────────────────── */
.wall-east {
    position: absolute;
    right: 0; top: 0;
    width: 5px; height: calc(100% - 72px);
    background: #1e293b;
}

/* ─── SEPARADOR INTERIOR VERTICAL (entre cuerpos) ──────── */
.wall-divider-v {
    position: absolute;
    top: 6px;
    width: 4px;
    background: #334155;
}
.wall-div-mid {
    left: 48.5%;
    height: 390px;
}

/* ─── ÁREA DE WASHING TOTES (franja izquierda vertical) ── */
.washing-strip {
    position: absolute;
    left: 5px;
    top: 6px;
    width: 52px;
    height: calc(100% - 78px);
    border-right: 3px solid #334155;
    background: #eef0f4;
    display: flex;
    align-items: center;
    justify-content: center;
}
.washing-label {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    font-size: 0.7rem;
    font-weight: 900;
    color: #334155;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ─── ZONA SUPERIOR: STORAGE RACKS ─────────────────────── */
/* Región interna después del washing strip */
.storage-zone {
    position: absolute;
    left: 60px;
    top: 6px;
    right: 5px;
    height: 238px;
    background:
        linear-gradient(rgba(30,41,59,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,41,59,0.035) 1px, transparent 1px),
        #f8f6f0;
    background-size: 28px 28px;
    border-bottom: 3px solid #334155;
}

/* Grid de racks — filas densas de celdas rectangulares */
.rack-block {
    position: absolute;
    display: grid;
    gap: 3px 5px;
}
.rack-block.rb-left {
    left: 8px; top: 14px;
    grid-template-columns: repeat(30, 14px);
    grid-template-rows: repeat(5, 22px);
}
.rack-block.rb-right {
    right: 8px; top: 14px;
    grid-template-columns: repeat(20, 14px);
    grid-template-rows: repeat(5, 22px);
}

.rc {
    border: 1.5px solid #c08a20;
    background: rgba(196, 130, 20, 0.10);
    border-radius: 1px;
}

/* ─── RETURNS STATIONS (caja con etiqueta, arriba-izq) ── */
.returns-box {
    position: absolute;
    left: 64px;
    top: 8px;
    width: 200px;
    height: 62px;
    border: 2px solid #334155;
    background: rgba(226,232,240,0.4);
}
.returns-label {
    position: absolute;
    top: -1px; left: 4px;
    background: #1e293b;
    color: #fff;
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 6px;
    letter-spacing: 0.04em;
}

/* ─── LÍNEA HORIZONTAL DIVISORIA (andén principal) ──────── */
.dock-wall-top {
    position: absolute;
    left: 57px;
    top: 244px;
    right: 5px;
    height: 6px;
    background: #1e293b;
}
.dock-wall-bottom {
    position: absolute;
    left: 57px;
    top: 250px;
    right: 5px;
    height: 3px;
    background: #475569;
}

/* ─── ZONA DE ANDENES: contenedor entre las dos líneas ─── */
.dock-zone {
    position: absolute;
    left: 57px;
    top: 253px;
    right: 5px;
    height: 238px;
    background:
        linear-gradient(rgba(30,41,59,0.040) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,41,59,0.040) 1px, transparent 1px),
        #eef2f7;
    background-size: 28px 28px;
    border-bottom: 4px solid #1e293b;
    display: flex;
    align-items: flex-start;
    padding-top: 18px;
}

/* ─── CANALETAS INTERNAS DE ANDENES (líneas verticales) ── */
.dock-slat {
    width: 2px;
    height: 210px;
    background: #94a3b8;
    flex-shrink: 0;
}

/* ─── PUERTAS / DOCK DOORS ──────────────────────────────── */
.dock-slot {
    width: 28px;
    height: 214px;
    margin: 0;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.dock-name {
    width: 34px;
    height: 13px;
    margin-bottom: 3px;
    font-size: 0.45rem;
    line-height: 0.48rem;
    font-weight: 900;
    color: #334155;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
}

.dock-door {
    width: 28px;
    height: 76px;
    border-radius: 3px 3px 0 0;
    border: 1.5px solid rgba(255,255,255,0.7);
    box-shadow: inset 0 0 0 1px rgba(0,0,0,0.14), 0 3px 8px rgba(15,23,42,0.2);
    animation: livePulse 1.8s infinite ease-in-out;
    cursor: pointer;
}
.dock-door.free      { background: #16a34a; animation-duration: 3s; }
.dock-door.occupied  { background: #2563eb; animation-duration: 2s; }
.dock-door.issue     { background: #dc2626; animation-duration: 0.8s; }
.dock-door.maintenance { background: #78716c; animation-duration: 4s; }

@keyframes livePulse {
    0%   { opacity: 0.78; filter: brightness(0.9); }
    50%  { opacity: 1;    filter: brightness(1.15); }
    100% { opacity: 0.78; filter: brightness(0.9); }
}

.mini-truck {
    width: 22px;
    height: 62px;
    margin-top: 7px;
    position: relative;
    border-radius: 4px;
    background: #cbd5e1;
    border: 1px solid #94a3b8;
    box-shadow: 0 4px 7px rgba(15,23,42,0.12);
}
.mini-truck::before {
    content: "";
    position: absolute;
    left: 2px;
    top: -12px;
    width: 18px;
    height: 15px;
    border-radius: 10px 10px 2px 2px;
    background: #facc15;
    border: 1px solid #d97706;
}
.mini-truck::after {
    content: "";
    position: absolute;
    left: 4px;
    top: -5px;
    width: 14px;
    height: 7px;
    border-radius: 2px;
    background: #0f172a;
}
.mini-truck.shipping {
    transform: rotate(180deg);
    margin-top: 12px;
}
.mini-truck .cargo-line {
    position: absolute;
    left: 3px;
    right: 3px;
    height: 2px;
    background: rgba(100,116,139,0.45);
}
.mini-truck .cargo-line.l1 { top: 19px; }
.mini-truck .cargo-line.l2 { top: 38px; }
.mini-truck.hidden {
    visibility: hidden;
}

/* Separadores entre grupos de andenes */
.dock-gap { width: 18px; flex-shrink: 0; }
.dock-gap-large {
    width: 52px;
    height: 238px;
    flex-shrink: 0;
    background: rgba(221,227,236,0.75);
    border-left: 2px solid #94a3b8;
    border-right: 2px solid #94a3b8;
    margin-top: -18px;
}

/* ─── ETIQUETAS FLOTANTES NEGRAS (tipo blueprint) ──────── */
.zone-tag {
    position: absolute;
    background: #0f172a;
    color: #ffffff;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    text-transform: uppercase;
    white-space: nowrap;
}

/* ─── ÁREA EXTERIOR (camiones, muelle exterior) ─────────── */
.exterior-zone {
    position: absolute;
    left: 57px;
    top: 491px;
    right: 5px;
    bottom: 72px;
    background:
        linear-gradient(rgba(30,41,59,0.040) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,41,59,0.040) 1px, transparent 1px),
        #e8ecf1;
    background-size: 28px 28px;
    border-left: 2px solid #94a3b8;
}
.exterior-lines {
    position: absolute;
    left: 0; top: 0;
    width: 100%; height: 100%;
    background-image: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 56px,
        rgba(148,163,184,0.4) 56px,
        rgba(148,163,184,0.4) 58px
    );
}

/* ─── ZONA DE SHIPPING (lado derecho inferior) ─────────── */
.shipping-zone-label {
    position: absolute;
    left: 57px;
    top: 386px;
    font-size: 0.62rem;
    font-weight: 800;
    color: #475569;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ─── SCOPE OF WORK ──────────────────────────────────────── */
.scope-mark {
    position: absolute;
    right: 14px;
    bottom: 78px;
    font-size: 0.65rem;
    font-weight: 900;
    color: #94a3b8;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ─── DISTRIBUTION OFFICE (esquina inferior derecha) ─────── */
.dist-office {
    position: absolute;
    right: 5px;
    bottom: 72px;
    width: 180px;
    height: 66px;
    border: 2.5px solid #1e293b;
    background: rgba(214,220,230,0.5);
}
.dist-office-label {
    position: absolute;
    top: -1px; left: 4px;
    background: #0f172a;
    color: #fff;
    font-size: 0.58rem;
    font-weight: 800;
    padding: 2px 6px;
    letter-spacing: 0.04em;
}

/* ─── LEYENDA INFERIOR ───────────────────────────────────── */
.legend-bar {
    position: absolute;
    left: 0; right: 0;
    bottom: 0;
    height: 68px;
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 0 20px;
    border-top: 2px solid #cbd5e1;
    background: #f1f5f9;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
    color: #334155;
    font-weight: 700;
    font-size: 0.78rem;
}
.legend-dot {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid rgba(17,24,39,0.2);
}
.live-badge {
    margin-left: auto;
    padding: 6px 14px;
    background: #dcfce7;
    color: #15803d;
    border: 1.5px solid #86efac;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.78rem;
}
.update-time {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 600;
}
</style>
"""


def rack_cells(n):
    return "".join("<div class='rc'></div>" for _ in range(n))


def dock_door_html(door_id, status, zone_name):
    cls_map = {
        "Disponible": "free",
        "Ocupada": "occupied",
        "Incidencia": "issue",
        "Mantenimiento": "maintenance",
    }
    cls = cls_map.get(status, "free")
    truck_cls = "mini-truck hidden" if status == "Disponible" else "mini-truck"
    if zone_name == "Shipping Docks" and status != "Disponible":
        truck_cls += " shipping"

    return f"""
    <div class="dock-slot" title="{door_id} · {status}">
        <div class="dock-name">{door_id}</div>
        <div class="dock-door {cls}"></div>
        <div class="{truck_cls}">
            <span class="cargo-line l1"></span>
            <span class="cargo-line l2"></span>
        </div>
    </div>
    """


def dock_slat_html():
    return "<div class='dock-slat'></div>"


def build_dock_row(zone_name):
    """Build the sequence of slat + door + slat for a zone."""
    zone_data = door_df[door_df["Zona"] == zone_name].copy()
    parts = []
    for _, row in zone_data.iterrows():
        parts.append(dock_slat_html())
        parts.append(dock_door_html(row["Puerta"], row["Estado puerta"], zone_name))
    parts.append(dock_slat_html())
    return "".join(parts)


ra_dock_row = build_dock_row("Receiving A")
shipping_dock_row = build_dock_row("Shipping Docks")
rb_dock_row = build_dock_row("Receiving B")

digital_twin_html = digital_twin_css + f"""
<div class="twin-frame">

    <!-- Paredes exteriores -->
    <div class="wall-north"></div>
    <div class="wall-south"></div>
    <div class="wall-west"></div>
    <div class="wall-east"></div>

    <!-- Washing totes: franja izquierda vertical -->
    <div class="washing-strip">
        <span class="washing-label">Washing&nbsp;totes</span>
    </div>

    <!-- Zona superior de almacenaje (racks) -->
    <div class="storage-zone">
        <!-- Caja Returns Stations -->
        <div class="returns-box">
            <span class="returns-label">Returns Stations</span>
        </div>
        <!-- Bloque izquierdo de racks (mayor, al centro-izquierda) -->
        <div class="rack-block rb-left">{rack_cells(150)}</div>
        <!-- Bloque derecho de racks -->
        <div class="rack-block rb-right">{rack_cells(100)}</div>
    </div>

    <!-- Línea divisoria andenes -->
    <div class="dock-wall-top"></div>
    <div class="dock-wall-bottom"></div>

    <!-- ZONA DE ANDENES — fila única horizontal -->
    <div class="dock-zone" id="dock-zone-main">
        <!-- Receiving A (izquierda) -->
        {ra_dock_row}
        <!-- Separación central (hueco entre Receiving A y Shipping) -->
        <div class="dock-gap-large"></div>
        <!-- Shipping Docks (centro) -->
        {shipping_dock_row}
        <!-- Separación -->
        <div class="dock-gap-large"></div>
        <!-- Receiving B (derecha) -->
        {rb_dock_row}
    </div>

    <!-- Etiquetas negras tipo plano -->
    <div class="zone-tag" style="left:64px; top:248px;">Docks Receiving A</div>
    <div class="zone-tag" id="shipping-tag" style="left:50%; transform:translateX(-50%); top:248px;">Shipping Docks</div>
    <div class="zone-tag" style="left:calc(100% - 330px); top:248px;">Docks Receiving B</div>

    <!-- Zona exterior (muelle / patio de camiones) -->
    <div class="exterior-zone">
        <div class="exterior-lines"></div>
    </div>

    <!-- Distribution Office esquina inferior derecha -->
    <div class="dist-office">
        <span class="dist-office-label">Distribution Office</span>
    </div>

    <!-- Scope of work -->
    <div class="scope-mark">SCOPE OF WORK</div>

    <!-- Leyenda inferior -->
    <div class="legend-bar">
        <div class="legend-item"><span class="legend-dot" style="background:#16a34a;"></span>Disponible</div>
        <div class="legend-item"><span class="legend-dot" style="background:#2563eb;"></span>Ocupada</div>
        <div class="legend-item"><span class="legend-dot" style="background:#dc2626;"></span>Incidencia</div>
        <div class="legend-item"><span class="legend-dot" style="background:#78716c;"></span>Mantenimiento</div>
        <span class="update-time">Actualización: {NOW.strftime("%H:%M:%S")}</span>
        <span class="live-badge">Simulated live view</span>
    </div>

    <!-- Sello inferior -->
    <div class="oxxo-stamp">OXXO | Uso Interno · Digital Twin</div>
</div>
"""



# ==================================================
# HELPERS · VISTA OPERATIVA TIPO V3
# ==================================================
def op_status_class(status: str) -> str:
    if status == "Incidencia":
        return "op-issue"
    if status == "Ocupada":
        return "op-occupied"
    if status == "Mantenimiento":
        return "op-maintenance"
    return "op-free"


def op_make_truck_html(row):
    if row["Estado puerta"] == "Disponible":
        return f"""
        <div class="op-truck op-empty">
            <b>Libre</b>
            <span>Sin unidad</span>
            <em>{row['Puerta']}</em>
        </div>
        """

    truck_class = "op-truck op-truck-issue" if row["Estado puerta"] == "Incidencia" else "op-truck"
    return f"""
    <div class="{truck_class}">
        <b>{row['Camión']}</b>
        <span>{row['Actividad']}</span>
        <em>{row['Puerta']}</em>
    </div>
    """


def op_make_door_html(row):
    cls = op_status_class(row["Estado puerta"])
    return f"""
    <div class="op-door {cls}" title="{row['Puerta']} · {row['Estado puerta']} · {row['Actividad']}">
        <b>{row['Puerta']}</b>
        <span>{row['Estado puerta']}</span>
        <em>{int(row['% avance'])}%</em>
    </div>
    """


def op_segment_html(zone_name: str, subtitle: str, selected_door_list=None, selected_status_list=None):
    zdf = door_df[door_df["Zona"] == zone_name].copy()

    if selected_door_list:
        zdf = zdf[zdf["Puerta"].isin(selected_door_list)]

    if selected_status_list:
        zdf = zdf[zdf["Estado puerta"].isin(selected_status_list)]

    if zdf.empty:
        return f"""
        <div class="op-zone-panel">
            <div class="op-zone-head">
                <h3>{zone_name}</h3>
                <span>{subtitle}</span>
            </div>
            <div class="op-empty-message">No hay puertas con los filtros seleccionados.</div>
        </div>
        """

    trucks_html = "".join(op_make_truck_html(row) for _, row in zdf.iterrows())
    doors_html = "".join(op_make_door_html(row) for _, row in zdf.iterrows())

    total = len(zdf)
    occupied = int((zdf["Estado puerta"] == "Ocupada").sum())
    issue = int((zdf["Estado puerta"] == "Incidencia").sum())
    maintenance = int((zdf["Estado puerta"] == "Mantenimiento").sum())
    available = int((zdf["Estado puerta"] == "Disponible").sum())
    pct = round(((occupied + issue) / total) * 100, 1) if total else 0

    process_label = "Recepción / descarga / validación" if "Receiving" in zone_name else "Consolidación / carga / liberación"

    return f"""
    <div class="op-zone-panel">
        <div class="op-zone-head">
            <div>
                <h3>{zone_name}</h3>
                <small>{subtitle}</small>
            </div>
            <span>{pct}% ocupación</span>
        </div>

        <div class="op-zone-kpis">
            <div><b>{total}</b><small>Puertas</small></div>
            <div><b>{occupied}</b><small>Ocupadas</small></div>
            <div><b>{issue}</b><small>Incidencias</small></div>
            <div><b>{available}</b><small>Libres</small></div>
        </div>

        <div class="op-zone-label">EXTERIOR · CAMIONES</div>
        <div class="op-truck-row">{trucks_html}</div>

        <div class="op-zone-label">LÍNEA DE ANDENES / PUERTAS</div>
        <div class="op-door-grid">{doors_html}</div>

        <div class="op-process-area">
            {process_label}<br>
            <small>Área operativa modelada digitalmente</small>
        </div>
    </div>
    """


OPERATIVE_BLUEPRINT_CSS = """
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Inter, Arial, Helvetica, sans-serif;
    background: transparent;
}
.op-zone-panel {
    width: 100%;
    min-height: 560px;
    background-color: #0f2742;
    background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 40px 40px, 40px 40px, 10px 10px, 10px 10px;
    border: 2px solid #8fb7dc;
    border-radius: 18px;
    padding: 18px;
    color: #e8f4ff;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.25);
}
.op-zone-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid rgba(232,244,255,0.55);
    padding-bottom: 10px;
    margin-bottom: 12px;
}
.op-zone-head h3 {
    margin: 0;
    color: #ffffff;
    font-size: 1.15rem;
    letter-spacing: -0.02em;
}
.op-zone-head small {
    color: #b9d9f5;
    font-size: 0.78rem;
}
.op-zone-head span {
    color: #d7ecff;
    font-size: 0.82rem;
    font-weight: 800;
    border: 1px solid rgba(215,236,255,0.45);
    border-radius: 999px;
    padding: 6px 10px;
    background: rgba(255,255,255,0.04);
}
.op-zone-kpis {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 14px;
}
.op-zone-kpis div {
    border: 1px solid rgba(215,236,255,0.35);
    border-radius: 12px;
    padding: 8px 6px;
    text-align: center;
    background: rgba(255,255,255,0.04);
}
.op-zone-kpis b {
    display: block;
    color: #ffffff;
    font-size: 1.1rem;
}
.op-zone-kpis small {
    color: #b9d9f5;
    font-size: 0.64rem;
}
.op-zone-label {
    text-align: center;
    color: #b9d9f5;
    font-size: 0.72rem;
    font-weight: 900;
    margin: 12px 0 7px;
    letter-spacing: 0.06em;
}
.op-truck-row, .op-door-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
}
.op-truck {
    width: 92px;
    height: 56px;
    border: 1.5px solid #fef3c7;
    background: rgba(254,243,199,0.22);
    border-radius: 9px;
    color: #fff7df;
    font-size: 0.58rem;
    text-align: center;
    padding: 6px 4px;
    overflow: hidden;
}
.op-truck b, .op-truck span, .op-truck em {
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.op-truck.op-empty {
    border-color: rgba(255,255,255,0.32);
    background: rgba(255,255,255,0.05);
    color: rgba(232,244,255,0.45);
}
.op-truck-issue {
    border-color: #fecaca;
    background: rgba(248,113,113,0.30);
}
.op-door {
    width: 84px;
    height: 70px;
    border: 1.8px solid #d7ecff;
    border-radius: 9px;
    text-align: center;
    font-size: 0.64rem;
    padding: 8px 4px;
    color: #ffffff;
    box-shadow: 0 8px 16px rgba(0,0,0,0.16);
}
.op-door b, .op-door span, .op-door em {
    display: block;
}
.op-door b {
    font-size: 0.72rem;
}
.op-door span {
    font-size: 0.62rem;
}
.op-door em {
    font-size: 0.62rem;
    font-style: normal;
}
.op-free {
    background: rgba(5,150,105,0.82);
}
.op-occupied {
    background: rgba(37,99,235,0.86);
}
.op-issue {
    background: rgba(190,18,60,0.90);
}
.op-maintenance {
    background: rgba(107,114,128,0.86);
}
.op-process-area {
    margin-top: 16px;
    min-height: 120px;
    border: 1.4px dashed rgba(215,236,255,0.65);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #d7ecff;
    background: rgba(255,255,255,0.025);
    font-size: 0.86rem;
    padding: 12px;
}
.op-process-area small {
    color: #b9d9f5;
}
.op-empty-message {
    min-height: 420px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #b9d9f5;
    border: 1px dashed rgba(215,236,255,0.45);
    border-radius: 14px;
}
</style>
"""

# ==================================================
# TABS
# ==================================================
tab_general, tab_exec, tab_operativa, tab_historica = st.tabs(
    ["Vista general · Digital Twin", "Vista ejecutiva", "Vista operativa", "Vista histórica"]
)


# ==================================================
# VISTA GENERAL
# ==================================================
with tab_general:
    st.header("Vista general operativa · digital twin")
    st.markdown(
        "<div class='section-caption'>Plano conceptual construido con código. No utiliza imagen PNG. "
        "La vista se enfoca únicamente en Receiving y Shipping.</div>",
        unsafe_allow_html=True,
    )

    components.html(digital_twin_html, height=750, scrolling=False)

    st.markdown("### Indicadores generales del área")
    c1, c2, c3, c4, c5 = st.columns(5)

    total_doors = len(door_df)
    occupied_doors = int((door_df["Estado puerta"] == "Ocupada").sum())
    issue_doors = int((door_df["Estado puerta"] == "Incidencia").sum())
    free_doors = int((door_df["Estado puerta"] == "Disponible").sum())
    maintenance_doors = int((door_df["Estado puerta"] == "Mantenimiento").sum())
    occ_pct = round((occupied_doors + issue_doors) / total_doors * 100, 1)

    c1.metric("Puertas totales", total_doors)
    c2.metric("Ocupación", f"{occ_pct}%")
    c3.metric("Disponibles", free_doors)
    c4.metric("Incidencias", issue_doors)
    c5.metric("Mantenimiento", maintenance_doors)


# ==================================================
# VISTA EJECUTIVA
# ==================================================
with tab_exec:
    st.header("Vista ejecutiva")
    st.caption(f"Periodo seleccionado: {period_label} · última actualización {NOW.strftime('%d/%m/%Y %H:%M:%S')}")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Proveedores plan", kpis["total"])
    k2.metric("% apego al plan", f"{kpis['plan_adherence']}%")
    k3.metric("Tarimas recibidas", f"{kpis['received_pallets']}/{kpis['planned_pallets']}")
    k4.metric("Calidad recibo", f"{kpis['quality_score']}%")

    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Estadía prom.", f"{kpis['avg_stay']} min")
    k6.metric("Espera prom.", f"{kpis['avg_wait']} min")
    k7.metric("Incidencias", kpis["incidents"])
    k8.metric("Ocupación almacenaje", f"{kpis['storage']}%")

    st.markdown("### Alertas ejecutivas")
    alerts = []
    if kpis["waiting"] > 6:
        alerts.append("Cola de espera superior al umbral deseado.")
    if kpis["late"] > 5:
        alerts.append("Proveedores fuera de horario están afectando el apego al plan.")
    if kpis["incidents"] > 8:
        alerts.append("Nivel alto de incidencias operativas y RDM.")
    if kpis["storage"] > 90:
        alerts.append("Ocupación de almacenaje elevada.")
    if not alerts:
        alerts.append("Sin alertas críticas en este momento.")

    for alert in alerts:
        st.warning(alert)

    ex1, ex2 = st.columns(2)
    with ex1:
        st.subheader("Camiones por estado")
        if filtered_history.empty:
            st.info("Sin registros para el periodo.")
        else:
            status_count = filtered_history["Estado"].value_counts().reset_index()
            status_count.columns = ["Estado", "Total"]
            fig = px.bar(status_count, x="Estado", y="Total")
            st.plotly_chart(fig, use_container_width=True)

    with ex2:
        st.subheader("Actividad por zona")
        if filtered_history.empty:
            st.info("Sin registros para el periodo.")
        else:
            zone_count = filtered_history["Zona"].value_counts().reset_index()
            zone_count.columns = ["Zona", "Total"]
            fig = px.pie(zone_count, names="Zona", values="Total", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)


# ==================================================
# VISTA OPERATIVA
# ==================================================
with tab_operativa:
    st.header("Filtros de análisis operativo")

    f1, f2, f3 = st.columns([1, 1.8, 1])

    with f1:
        selected_zone = st.selectbox(
            "Zona",
            ["Todas", "Receiving A", "Shipping Docks", "Receiving B"],
            index=0,
        )

    base_df = door_df.copy()
    if selected_zone != "Todas":
        base_df = base_df[base_df["Zona"] == selected_zone].copy()

    with f2:
        selected_doors = st.multiselect(
            "Puertas específicas",
            options=base_df["Puerta"].tolist(),
            default=base_df["Puerta"].tolist()[: min(6, len(base_df))],
        )

    with f3:
        selected_status = st.multiselect(
            "Estado puerta",
            options=["Disponible", "Ocupada", "Incidencia", "Mantenimiento"],
            default=["Disponible", "Ocupada", "Incidencia"],
        )

    filtered_doors = base_df.copy()

    if selected_doors:
        filtered_doors = filtered_doors[filtered_doors["Puerta"].isin(selected_doors)].copy()

    if selected_status:
        filtered_doors = filtered_doors[filtered_doors["Estado puerta"].isin(selected_status)].copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Puertas filtradas", len(filtered_doors))
    m2.metric("Ocupadas", int((filtered_doors["Estado puerta"] == "Ocupada").sum()))
    m3.metric("Con incidencia", int((filtered_doors["Estado puerta"] == "Incidencia").sum()))
    m4.metric("Disponibles", int((filtered_doors["Estado puerta"] == "Disponible").sum()))

    st.markdown("### Detalle por zona · layout operativo de andenes")
    st.caption("Esta sección recupera el formato visual tipo blueprint de la V3: andenes azules, incidencias y camiones por zona.")

    if selected_zone == "Todas":
        z1, z2, z3 = st.columns(3)

        with z1:
            components.html(
                OPERATIVE_BLUEPRINT_CSS + op_segment_html(
                    "Receiving A",
                    "Zona de recibo A",
                    selected_door_list=selected_doors if selected_doors else None,
                    selected_status_list=selected_status if selected_status else None,
                ),
                height=600,
                scrolling=True,
            )

        with z2:
            components.html(
                OPERATIVE_BLUEPRINT_CSS + op_segment_html(
                    "Shipping Docks",
                    "Zona de salidas",
                    selected_door_list=selected_doors if selected_doors else None,
                    selected_status_list=selected_status if selected_status else None,
                ),
                height=600,
                scrolling=True,
            )

        with z3:
            components.html(
                OPERATIVE_BLUEPRINT_CSS + op_segment_html(
                    "Receiving B",
                    "Zona de recibo B",
                    selected_door_list=selected_doors if selected_doors else None,
                    selected_status_list=selected_status if selected_status else None,
                ),
                height=600,
                scrolling=True,
            )

    else:
        components.html(
            OPERATIVE_BLUEPRINT_CSS + op_segment_html(
                selected_zone,
                "Vista ampliada de zona seleccionada",
                selected_door_list=selected_doors if selected_doors else None,
                selected_status_list=selected_status if selected_status else None,
            ),
            height=620,
            scrolling=True,
        )

    st.markdown("### Información detallada de puertas seleccionadas")

    st.dataframe(
        filtered_doors[[
            "Puerta",
            "Zona",
            "Estado puerta",
            "Camión",
            "Proveedor",
            "Transportista",
            "Actividad",
            "Tipo incidencia",
            "Responsable incidencia",
            "% avance",
            "Espera min",
            "Descarga min",
            "Tarimas recibidas",
            "Tarimas plan",
            "Última actualización",
        ]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Puerta seleccionada · análisis individual")
    if len(filtered_doors) == 0:
        st.info("No hay puertas con los filtros seleccionados.")
    else:
        selected_single_door = st.selectbox(
            "Selecciona una puerta para ver detalle",
            filtered_doors["Puerta"].tolist(),
        )
        row = door_df[door_df["Puerta"] == selected_single_door].iloc[0]

        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Puerta", row["Puerta"])
        d2.metric("Estado", row["Estado puerta"])
        d3.metric("Avance", f"{row['% avance']}%")
        d4.metric("Espera", f"{row['Espera min']} min")
        d5.metric("Descarga", f"{row['Descarga min']} min")

        if row["Estado puerta"] == "Incidencia":
            st.error(
                f"Incidencia detectada: {row['Tipo incidencia']} · "
                f"Escalar con: {row['Responsable incidencia']} · "
                f"Acción sugerida: {row['Acción sugerida']}"
            )

        st.markdown(
            f"""
            <div class="soft-panel">
                <b>Zona:</b> {row['Zona']}<br>
                <b>Camión:</b> {row['Camión']}<br>
                <b>Proveedor:</b> {row['Proveedor']}<br>
                <b>Transportista:</b> {row['Transportista']}<br>
                <b>Actividad actual:</b> {row['Actividad']}<br>
                <b>Tipo de incidencia:</b> {row['Tipo incidencia']}<br>
                <b>Responsable sugerido:</b> {row['Responsable incidencia']}<br>
                <b>Acción sugerida:</b> {row['Acción sugerida']}<br>
                <b>Tarimas:</b> {row['Tarimas recibidas']} / {row['Tarimas plan']}<br>
                <b>Última actualización:</b> {row['Última actualización']}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================================================
# VISTA HISTÓRICA
# ==================================================
with tab_historica:
    st.header("Vista histórica")
    st.caption(f"Periodo seleccionado: {period_label}")

    h1, h2 = st.columns(2)

    with h1:
        st.subheader("Plan vs ejecución de tarimas")
        pallets_df = pd.DataFrame({
            "Métrica": ["Tarimas planeadas", "Tarimas recibidas", "Pendientes"],
            "Total": [
                kpis["planned_pallets"],
                kpis["received_pallets"],
                max(0, kpis["planned_pallets"] - kpis["received_pallets"]),
            ],
        })
        fig_pallets = px.bar(pallets_df, x="Métrica", y="Total")
        st.plotly_chart(fig_pallets, use_container_width=True)

    with h2:
        st.subheader("Incidencias por tipo")
        if filtered_history.empty:
            st.info("Sin registros para el periodo.")
        else:
            incident_type_df = pd.DataFrame({
                "Tipo": ["Calidad", "Plaga", "Producto incompleto", "Alerta RDM", "Config. incorrecta", "Ajuste pendiente"],
                "Total": [
                    int(filtered_history["Rechazo calidad"].sum()),
                    int(filtered_history["Rechazo plaga"].sum()),
                    int(filtered_history["Producto incompleto"].sum()),
                    int(filtered_history["Alerta RDM"].sum()),
                    int(filtered_history["Config. incorrecta"].sum()),
                    int(filtered_history["Ajuste pendiente"].sum()),
                ],
            })
            fig_incidents = px.bar(incident_type_df, x="Tipo", y="Total")
            st.plotly_chart(fig_incidents, use_container_width=True)

    st.subheader("Base histórica simulada")
    st.dataframe(
        filtered_history[[
            "Timestamp",
            "Zona",
            "Puerta",
            "Camión",
            "Proveedor",
            "Estado",
            "Espera min",
            "Descarga min",
            "% avance",
            "Tarimas plan",
            "Tarimas recibidas",
            "Fuera de horario",
            "Alerta RDM",
        ]].sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


st.divider()
st.caption(
    "V4.4 · Digital twin conceptual construido en código. Próximo paso: ajustar posiciones exactas con medidas reales del CEDIS."
)
