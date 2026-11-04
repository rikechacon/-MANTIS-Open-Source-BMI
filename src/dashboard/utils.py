"""
Funciones auxiliares para MANTIS Dashboard
"""

import hashlib
import secrets
from datetime import datetime
from typing import Optional
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch

# ============================================================
# SEGURIDAD
# ============================================================

def hash_password(password: str) -> str:
    """Hashea una contraseña con salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        salt, hash_hex = hashed.split(":")
        hashed_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed_check.hex() == hash_hex
    except:
        return False

# ============================================================
# EXPORTACIÓN DE REPORTES
# ============================================================

def exportar_experimentos_pdf(experimentos: pd.DataFrame, filename: str = "reporte_experimentos.pdf"):
    """Exporta lista de experimentos a PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    elements.append(Paragraph("Reporte de Experimentos MANTIS v1.2", styles['Title']))
    elements.append(Paragraph(f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Tabla
    data = [["ID", "Fecha", "Operador", "Tipo", "Éxito", "Correlación"]]
    
    for _, row in experimentos.iterrows():
        data.append([
            str(row.get("id", "")),
            row.get("fecha", "").strftime("%Y-%m-%d") if hasattr(row.get("fecha", ""), "strftime") else str(row.get("fecha", "")),
            str(row.get("operador", "")),
            str(row.get("tipo", "")),
            "Sí" if row.get("exito") else "No",
            f"{row.get('correlacion_r', 0):.2f}" if pd.notna(row.get("correlacion_r")) else "N/A"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)

def exportar_experimentos_excel(experimentos: pd.DataFrame, filename: str = "reporte_experimentos.xlsx"):
    """Exporta lista de experimentos a Excel"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        experimentos.to_excel(writer, sheet_name='Experimentos', index=False)

# ============================================================
# VALIDACIONES
# ============================================================

def validar_parametros_ultrasonido(presion_MPa: float, duracion_s: float, ti: float, mi: float) -> dict:
    """Valida parámetros de ultrasonido contra límites de seguridad"""
    alertas = []
    
    if presion_MPa > 0.5:
        alertas.append({"nivel": "critical", "mensaje": f"Presión {presion_MPa} MPa excede límite (0.5 MPa)"})
    
    if ti > 0.7:
        alertas.append({"nivel": "critical", "mensaje": f"TI {ti} excede límite (0.7)"})
    
    if mi > 0.5:
        alertas.append({"nivel": "warning", "mensaje": f"MI {mi}接近 límite (0.5)"})
    
    if duracion_s > 120:
        alertas.append({"nivel": "warning", "mensaje": f"Duración {duracion_s}s es larga"})
    
    return {
        "valido": len([a for a in alertas if a["nivel"] == "critical"]) == 0,
        "alertas": alertas
    }

def validar_parametros_parche_clamp(resistencia_GOhm: float, corriente_pA: float) -> dict:
    """Valida parámetros de patch-clamp"""
    alertas = []
    
    if resistencia_GOhm < 1.0:
        alertas.append({"nivel": "critical", "mensaje": f"Resistencia {resistencia_GOhm} GΩ < 1 GΩ (sello pobre)"})
    
    if abs(corriente_pA) < 50:
        alertas.append({"nivel": "warning", "mensaje": f"Corriente {corriente_pA} pA muy baja"})
    
    return {
        "valido": len([a for a in alertas if a["nivel"] == "critical"]) == 0,
        "alertas": alertas
    }

# ============================================================
# ESTADÍSTICAS
# ============================================================

def calcular_estadisticas_experimentos(experimentos: pd.DataFrame) -> dict:
    """Calcula estadísticas resumidas de experimentos"""
    if experimentos.empty:
        return {
            "total": 0,
            "exito_pct": 0,
            "correlacion_promedio": 0,
            "por_tipo": {},
            "por_mes": {}
        }
    
    total = len(experimentos)
    exito_pct = (experimentos["exito"].sum() / total) * 100
    correlacion_promedio = experimentos["correlacion_r"].mean()
    
    por_tipo = experimentos.groupby("tipo").size().to_dict()
    
    experimentos["mes"] = experimentos["fecha"].dt.to_period("M")
    por_mes = experimentos.groupby("mes").size().to_dict()
    
    return {
        "total": total,
        "exito_pct": exito_pct,
        "correlacion_promedio": correlacion_promedio,
        "por_tipo": por_tipo,
        "por_mes": {str(k): v for k, v in por_mes.items()}
    }

def calcular_estadisticas_animales(animales: pd.DataFrame) -> dict:
    """Calcula estadísticas de animales"""
    if animales.empty:
        return {
            "total": 0,
            "activos": 0,
            "eutanasia": 0,
            "supervivencia_promedio_dias": 0
        }
    
    total = len(animales)
    activos = len(animales[animales["estado"] == "activo"])
    eutanasia = len(animales[animales["eutanasia"] == True])
    
    # Calcular supervivencia promedio
    animales_con_salida = animales[animales["fecha_salida"].notna()]
    if not animales_con_salida.empty:
        supervivencia = (animales_con_salida["fecha_salida"] - animales_con_salida["fecha_ingreso"]).dt.days.mean()
    else:
        supervivencia = 0
    
    return {
        "total": total,
        "activos": activos,
        "eutanasia": eutanasia,
        "supervivencia_promedio_dias": supervivencia
    }