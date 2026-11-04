"""
MANTIS Dashboard - Aplicación Principal
Dashboard de monitoreo y trazabilidad experimental
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import bcrypt

from database import SessionLocal, Usuario, LoteMNT, Experimento, Animal, AnimalExperimento, Residuo, Alerta
from models import UsuarioCreate, LoteMNTCreate, ExperimentoCreate, AnimalCreate
from models import evaluar_calidad_lote, calcular_fecha_vencimiento, verificar_criterios_eutanasia
from utils import hash_password, verify_password, exportar_experimentos_pdf, exportar_experimentos_excel
from utils import calcular_estadisticas_experimentos, calcular_estadisticas_animales
from config import *

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title="MANTIS Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS CSS
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003366;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #003366;
    }
    .alert-critical {
        background-color: #ffe6e6;
        border-left: 4px solid #ff0000;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background-color: #fff9e6;
        border-left: 4px solid #ffaa00;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-info {
        background-color: #e6f3ff;
        border-left: 4px solid #0066cc;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================

@st.cache_resource
def get_db_session():
    return SessionLocal()

def login(username: str, password: str, db: Session) -> Optional[Usuario]:
    """Autentica un usuario"""
    try:
        usuario = db.query(Usuario).filter(Usuario.nombre == username).first()
        if usuario and verify_password(password, usuario.password_hash):
            return usuario
    except Exception:
        db.rollback()
    return None

def logout():
    """Cierra sesión"""
    if "usuario" in st.session_state:
        del st.session_state["usuario"]

# ============================================================
# PÁGINA DE LOGIN
# ============================================================

def pagina_login(db: Session):
    """Página de inicio de sesión"""
    st.markdown('<h1 class="main-header">🧠 MANTIS Dashboard v1.2</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de Monitoreo y Trazabilidad Experimental")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                usuario = login(username, password, db)
                if usuario:
                    st.session_state["usuario"] = {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "rol": usuario.rol,
                        "email": usuario.email
                    }
                    st.success(f"¡Bienvenido, {usuario.nombre}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.markdown("**Usuario de prueba:**")
        st.code("admin / admin123")

# ============================================================
# PÁGINA PRINCIPAL (DASHBOARD)
# ============================================================

def pagina_dashboard(db: Session):
    """Página principal con métricas y gráficos"""
    st.markdown(f"# 🧠 Dashboard MANTIS v{MANTIS_VERSION}")
    st.markdown(f"*Bienvenido, {st.session_state['usuario']['nombre']}*")
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_experimentos = db.query(Experimento).count()
        st.metric("Total Experimentos", total_experimentos)
    
    with col2:
        lotes_activos = db.query(LoteMNT).filter(LoteMNT.estado == "en_uso").count()
        st.metric("Lotes MNT Activos", lotes_activos)
    
    with col3:
        animales_activos = db.query(Animal).filter(Animal.estado == "activo").count()
        st.metric("Animales Activos", animales_activos)
    
    with col4:
        alertas_activas = db.query(Alerta).filter(Alerta.resuelta == False).count()
        st.metric("Alertas Activas", alertas_activas, delta=f"-{alertas_activas}" if alertas_activas > 0 else None)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Experimentos por Tipo")
        experimentos = pd.read_sql(db.query(Experimento).statement, db.bind)
        if not experimentos.empty:
            fig = px.pie(experimentos, names='tipo', title='Distribución por Tipo')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay experimentos registrados")
    
    with col2:
        st.markdown("### Éxito de Experimentos (Últimos 30 días)")
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        experimentos_recientes = pd.read_sql(
            db.query(Experimento).filter(Experimento.fecha >= fecha_limite).statement,
            db.bind
        )
        if not experimentos_recientes.empty:
            exito_count = experimentos_recientes['exito'].sum()
            total_count = len(experimentos_recientes)
            fig = go.Figure(data=[go.Pie(
                labels=['Éxito', 'Fallo'],
                values=[exito_count, total_count - exito_count],
                marker_colors=['#28a745', '#dc3545']
            )])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay experimentos en los últimos 30 días")
    
    # Alertas recientes
    st.markdown("### 🔔 Alertas Recientes")
    alertas = pd.read_sql(
        db.query(Alerta).filter(Alerta.resuelta == False).order_by(Alerta.fecha.desc()).limit(5).statement,
        db.bind
    )
    
    if not alertas.empty:
        for _, alerta in alertas.iterrows():
            nivel_class = f"alert-{alerta['nivel']}"
            st.markdown(f'<div class="{nivel_class}"><strong>[{alerta["nivel"].upper()}]</strong> {alerta["mensaje"]} <br/><small>{alerta["fecha"]}</small></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No hay alertas activas")

# ============================================================
# PÁGINA DE REGISTRO DE EXPERIMENTOS
# ============================================================

def pagina_registro_experimento(db: Session):
    """Página para registrar nuevos experimentos"""
    st.markdown("# 📝 Registrar Experimento")
    st.markdown("---")
    
    # Inicializar estado para mostrar métricas
    if "mostrar_metricas" not in st.session_state:
        st.session_state.mostrar_metricas = False
    
    with st.form("registro_experimento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código", placeholder="EXP-2026-0001")
            tipo = st.selectbox("Tipo", ["in_vitro", "in_vivo", "patch_clamp", "bioluminiscencia", "ultrasonido"])
            protocolo = st.text_input("Protocolo")
            duracion_min = st.number_input("Duración (min)", min_value=0.0, step=0.5)
            temperatura_C = st.number_input("Temperatura (°C)", min_value=20.0, max_value=43.0, value=37.0)
        
        with col2:
            lotes = db.query(LoteMNT).filter(LoteMNT.estado != "descartado").all()
            if lotes:
                lote_options = {f"{l.codigo} ({l.estado})": l.id for l in lotes}
                lote_seleccionado = st.selectbox("Lote MNT", list(lote_options.keys()))
                lote_mnt_id = lote_options[lote_seleccionado] if lote_seleccionado else None
            else:
                st.warning("⚠️ No hay lotes MNT disponibles. Primero crea un lote en 'Gestión Lotes MNT'")
                lote_mnt_id = None
            
            exito = st.checkbox("¿Experimento exitoso?", key="chk_exito")
            incidente = st.checkbox("¿Hubo incidente?", key="chk_incidente")
            desviacion = st.checkbox("¿Desviación del protocolo?", key="chk_desviacion")
        
        # Campos de métricas FUERA del form, controlados por session_state
        if st.session_state.get("mostrar_metricas", False):
            st.markdown("### 📊 Métricas del Experimento")
            col3, col4 = st.columns(2)
            with col3:
                correlacion_r = st.number_input("Correlación r (vs MEA)", min_value=0.0, max_value=1.0, step=0.01, value=0.80, key="corr_r")
                snr_db = st.number_input("SNR (dB)", min_value=0.0, step=0.1, value=10.0, key="snr_db")
            with col4:
                latencia_ms = st.number_input("Latencia (ms)", min_value=0.0, step=1.0, value=40.0, key="lat_ms")
        else:
            correlacion_r = None
            snr_db = None
            latencia_ms = None
        
        # Campos de incidente
        if st.session_state.get("chk_incidente", False):
            descripcion_incidente = st.text_area("Descripción del incidente")
        else:
            descripcion_incidente = None
        
        # Campos de desviación
        if st.session_state.get("chk_desviacion", False):
            descripcion_desviacion = st.text_area("Descripción de la desviación")
        else:
            descripcion_desviacion = None
        
        notas = st.text_area("Notas adicionales")
        
        submit = st.form_submit_button("Registrar Experimento", use_container_width=True)
        
        if submit:
            if not codigo or not protocolo or not lote_mnt_id:
                st.error("Por favor complete todos los campos obligatorios")
            else:
                nuevo_experimento = Experimento(
                    codigo=codigo,
                    operador_id=st.session_state["usuario"]["id"],
                    lote_mnt_id=lote_mnt_id,
                    tipo=tipo,
                    protocolo=protocolo,
                    duracion_min=duracion_min,
                    temperatura_C=temperatura_C,
                    exito=exito,
                    correlacion_r=correlacion_r,
                    snr_db=snr_db,
                    latencia_ms=latencia_ms,
                    incidente=incidente,
                    descripcion_incidente=descripcion_incidente,
                    desviacion_protocolo=desviacion,
                    descripcion_desviacion=descripcion_desviacion,
                    notas=notas
                )
                db.add(nuevo_experimento)
                db.commit()
                
                st.success(f"✅ Experimento {codigo} registrado exitosamente")
                st.balloons()
    
    # Callback para actualizar estado cuando cambia el checkbox
    def actualizar_metricas():
        st.session_state.mostrar_metricas = st.session_state.get("chk_exito", False)
    
    # Observar cambios en el checkbox
    # Nota: esto requiere que el checkbox tenga on_change

# ============================================================
# PÁGINA DE GESTIÓN DE LOTES MNT
# ============================================================

def pagina_gestion_lotes(db: Session):
    """Página para gestionar lotes de MNTs"""
    st.markdown("# 🧪 Gestión de Lotes MNT")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Registrar Nuevo Lote", "Ver Lotes Existentes"])
    
    with tab1:
        st.markdown("### Registrar Nuevo Lote de MNTs")
        
        with st.form("registro_lote"):
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input("Código", placeholder="MNT-2026-11-04-A")
                tamano_nm = st.number_input("Tamaño (nm)", min_value=50.0, max_value=200.0, value=100.0)
                pdi = st.number_input("PDI", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
                zeta_mV = st.number_input("Potencial Zeta (mV)", min_value=-50.0, max_value=0.0, value=-20.0)
            
            with col2:
                concentracion = st.number_input("Concentración (partículas/mL)", min_value=0.0, value=1e9, format="%.2e")
                western_blot_ok = st.checkbox("Western Blot OK")
                liberacion_eficiencia = st.number_input("Eficiencia de Liberación (%)", min_value=0.0, max_value=100.0, value=85.0)
                almacenamiento = st.selectbox("Almacenamiento", ["4C", "-20C", "-80C", "N2_liquido"])
            
            submit = st.form_submit_button("Registrar Lote", use_container_width=True)
            
            if submit:
                # Validar calidad
                lote_data = {
                    "tamano_nm": tamano_nm,
                    "pdi": pdi,
                    "zeta_mV": zeta_mV,
                    "western_blot_ok": western_blot_ok,
                    "liberacion_eficiencia": liberacion_eficiencia
                }
                
                calidad = evaluar_calidad_lote(lote_data)
                
                if not calidad["apto"]:
                    st.error(f"❌ Lote no cumple criterios de calidad: {', '.join(calidad['fallas'])}")
                else:
                    fecha_vencimiento = calcular_fecha_vencimiento(almacenamiento)
                    
                    nuevo_lote = LoteMNT(
                        codigo=codigo,
                        operador_id=st.session_state["usuario"]["id"],
                        tamano_nm=tamano_nm,
                        pdi=pdi,
                        zeta_mV=zeta_mV,
                        concentracion_particulas_mL=concentracion,
                        western_blot_ok=western_blot_ok,
                        liberacion_eficiencia=liberacion_eficiencia,
                        estabilidad_7d=True,
                        estado="sintetizado",
                        fecha_vencimiento=fecha_vencimiento,
                        almacenamiento=almacenamiento
                    )
                    
                    db.add(nuevo_lote)
                    db.commit()
                    
                    st.success(f"✅ Lote {codigo} registrado. Vencimiento: {fecha_vencimiento.strftime('%Y-%m-%d')}")

    with tab2:
        st.markdown("### Lotes Registrados")
        
        lotes = pd.read_sql(db.query(LoteMNT).statement, db.bind)
        
        if not lotes.empty:
            # Mostrar tabla
            st.dataframe(lotes[[
                "codigo", "fecha_sintesis", "tamano_nm", "pdi", "zeta_mV",
                "liberacion_eficiencia", "estado", "fecha_vencimiento"
            ]])
            
            # Exportar
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Exportar a Excel"):
                    exportar_experimentos_excel(lotes, "lotes_mnt.xlsx")
                    st.success("Archivo generado: lotes_mnt.xlsx")
        else:
            st.info("No hay lotes registrados")

# ============================================================
# PÁGINA DE GESTIÓN DE ANIMALES
# ============================================================

def pagina_gestion_animales(db: Session):
    """Página para gestionar animales de experimentación"""
    st.markdown("# 🐀 Gestión de Animales")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Registrar Animal", "Monitoreo Diario"])
    
    with tab1:
        st.markdown("### Registrar Nuevo Animal")
        
        with st.form("registro_animal"):
            col1, col2 = st.columns(2)
            
            with col1:
                id_interno = st.text_input("ID Interno", placeholder="R001")
                especie = st.selectbox("Especie", ["Rata", "Ratón"])
                cepa = st.text_input("Cepa", placeholder="Sprague-Dawley / C57BL/6")
                sexo = st.selectbox("Sexo", ["M", "H"])
            
            with col2:
                fecha_nacimiento = st.date_input("Fecha de Nacimiento")
                peso_inicial_g = st.number_input("Peso Inicial (g)", min_value=0.0, value=250.0)
            
            submit = st.form_submit_button("Registrar Animal", use_container_width=True)
            
            if submit:
                nuevo_animal = Animal(
                    id_interno=id_interno,
                    especie=especie,
                    cepa=cepa,
                    sexo=sexo,
                    fecha_nacimiento=datetime.combine(fecha_nacimiento, datetime.min.time()),
                    peso_inicial_g=peso_inicial_g,
                    estado="aclimatacion",
                    fecha_ingreso=datetime.utcnow()
                )
                
                db.add(nuevo_animal)
                db.commit()
                
                st.success(f"✅ Animal {id_interno} registrado")
    
    with tab2:
        st.markdown("### Monitoreo Diario")
        
        animales_activos = db.query(Animal).filter(Animal.estado == "activo").all()
        
        if animales_activos:
            for animal in animales_activos:
                with st.expander(f"{animal.id_interno} - {animal.especie} ({animal.sexo})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        peso_actual = st.number_input(f"Peso actual (g)", value=animal.peso_inicial_g, key=f"peso_{animal.id}")
                        score = st.slider("Score Neurológico", 0, 3, 0, key=f"score_{animal.id}")
                        
                        # Verificar criterios de eutanasia
                        perdida_peso_pct = ((animal.peso_inicial_g - peso_actual) / animal.peso_inicial_g) * 100
                        if verificar_criterios_eutanasia({"score_neurologico": score, "perdida_peso_pct": perdida_peso_pct}):
                            st.error("⚠️ CRITERIOS DE EUTANASIA APLICABLES")
                    
                    with col2:
                        signos_ok = st.checkbox("Signos vitales OK", key=f"signos_{animal.id}")
                        notas = st.text_area("Notas", key=f"notas_{animal.id}")
                    
                    if st.button("Guardar Monitoreo", key=f"guardar_{animal.id}"):
                        st.info("Monitoreo guardado (funcionalidad en desarrollo)")
        else:
            st.info("No hay animales activos")

# ============================================================
# PÁGINA DE ALERTAS
# ============================================================

def pagina_alertas(db: Session):
    """Página de gestión de alertas"""
    st.markdown("# 🔔 Alertas y Notificaciones")
    st.markdown("---")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_nivel = st.multiselect("Nivel", ["info", "warning", "critical"], default=["warning", "critical"])
    with col2:
        filtro_categoria = st.multiselect("Categoría", ["seguridad", "equipo", "protocolo", "animal"])
    with col3:
        mostrar_resueltas = st.checkbox("Mostrar resueltas")
    
    # Consulta
    query = db.query(Alerta)
    if not mostrar_resueltas:
        query = query.filter(Alerta.resuelta == False)
    if filtro_nivel:
        query = query.filter(Alerta.nivel.in_(filtro_nivel))
    if filtro_categoria:
        query = query.filter(Alerta.categoria.in_(filtro_categoria))
    
    alertas = pd.read_sql(query.order_by(Alerta.fecha.desc()).statement, db.bind)
    
    if not alertas.empty:
        for _, alerta in alertas.iterrows():
            nivel_class = f"alert-{alerta['nivel']}"
            st.markdown(f'''
            <div class="{nivel_class}">
                <strong>[{alerta["nivel"].upper()}] {alerta["categoria"]}</strong><br/>
                {alerta["mensaje"]}<br/>
                <small>📅 {alerta["fecha"]}</small>
            </div>
            ''', unsafe_allow_html=True)
            
            if not alerta["resuelta"]:
                if st.button("Marcar como resuelta", key=f"resolver_{alerta['id']}"):
                    alerta_obj = db.query(Alerta).get(alerta["id"])
                    alerta_obj.resuelta = True
                    alerta_obj.fecha_resolucion = datetime.utcnow()
                    alerta_obj.resuelta_por = st.session_state["usuario"]["id"]
                    db.commit()
                    st.rerun()
    else:
        st.success("✅ No hay alertas que coincidan con los filtros")

# ============================================================
# PÁGINA DE REPORTES
# ============================================================

def pagina_reportes(db: Session):
    """Página de generación de reportes"""
    st.markdown("# 📊 Reportes y Exportación")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Experimentos", "Lotes MNT", "Animales"])
    
    with tab1:
        st.markdown("### Reporte de Experimentos")
        
        fecha_inicio = st.date_input("Fecha inicio", value=datetime.utcnow() - timedelta(days=30))
        fecha_fin = st.date_input("Fecha fin", value=datetime.utcnow())
        
        experimentos = pd.read_sql(
            db.query(Experimento).filter(
                Experimento.fecha >= datetime.combine(fecha_inicio, datetime.min.time()),
                Experimento.fecha <= datetime.combine(fecha_fin, datetime.max.time())
            ).statement,
            db.bind
        )
        
        if not experimentos.empty:
            st.dataframe(experimentos)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Exportar a PDF"):
                    exportar_experimentos_pdf(experimentos)
                    st.success("PDF generado")
            with col2:
                if st.button("📥 Exportar a Excel"):
                    exportar_experimentos_excel(experimentos)
                    st.success("Excel generado")
        else:
            st.info("No hay experimentos en el rango seleccionado")
    
    with tab2:
        st.markdown("### Reporte de Lotes MNT")
        st.info("Funcionalidad en desarrollo")
    
    with tab3:
        st.markdown("### Reporte de Animales")
        st.info("Funcionalidad en desarrollo")

# ============================================================
# NAVEGACIÓN PRINCIPAL
# ============================================================

def main():
    """Función principal de la aplicación"""
    db = get_db_session()
    
    # Verificar autenticación
    if "usuario" not in st.session_state:
        pagina_login(db)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['usuario']['nombre']}")
        st.markdown(f"*{st.session_state['usuario']['rol']}*")
        st.markdown("---")
        
        menu = st.radio(
            "Navegación",
            ["🏠 Dashboard", "📝 Registrar Experimento", "🧪 Gestión Lotes MNT",
             "🐀 Gestión Animales", "🔔 Alertas", "📊 Reportes"],
            index=0
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**MANTIS v{MANTIS_VERSION}**")
        st.markdown(f"Dashboard v{DASHBOARD_VERSION}")
    
    # Routing
    if menu == "🏠 Dashboard":
        pagina_dashboard(db)
    elif menu == "📝 Registrar Experimento":
        pagina_registro_experimento(db)
    elif menu == "🧪 Gestión Lotes MNT":
        pagina_gestion_lotes(db)
    elif menu == "🐀 Gestión Animales":
        pagina_gestion_animales(db)
    elif menu == "🔔 Alertas":
        pagina_alertas(db)
    elif menu == "📊 Reportes":
        pagina_reportes(db)

# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()
