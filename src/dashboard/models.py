"""
Modelos de datos y validaciones para MANTIS Dashboard
"""

from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, validator
import re

# ============================================================
# MODELOS PYDANTIC PARA VALIDACIÓN
# ============================================================

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "operador"
    certificacion_bsl2: bool = False
    
    @validator("email")
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Email inválido")
        return v
    
    @validator("rol")
    def validate_rol(cls, v):
        if v not in ["admin", "operador", "investigador"]:
            raise ValueError("Rol inválido")
        return v

class LoteMNTCreate(BaseModel):
    codigo: str
    tamano_nm: float
    pdi: float
    zeta_mV: float
    concentracion_particulas_mL: float
    western_blot_ok: bool
    liberacion_eficiencia: float
    almacenamiento: str
    
    @validator("codigo")
    def validate_codigo(cls, v):
        if not re.match(r"^MNT-\d{4}-\d{2}-\d{2}-[A-Z]$", v):
            raise ValueError("Formato: MNT-YYYY-MM-DD-X")
        return v
    
    @validator("tamano_nm")
    def validate_tamano(cls, v):
        if not (80 <= v <= 150):
            raise ValueError("Tamaño fuera de rango (80-150 nm)")
        return v
    
    @validator("pdi")
    def validate_pdi(cls, v):
        if v > 0.25:
            raise ValueError("PDI > 0.25 no aceptable")
        return v
    
    @validator("zeta_mV")
    def validate_zeta(cls, v):
        if not (-25 <= v <= -15):
            raise ValueError("Zeta fuera de rango (-25 a -15 mV)")
        return v
    
    @validator("liberacion_eficiencia")
    def validate_liberacion(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Eficiencia debe estar entre 0 y 100%")
        return v

class ExperimentoCreate(BaseModel):
    codigo: str
    tipo: str
    protocolo: str
    duracion_min: float
    temperatura_C: float
    lote_mnt_id: int
    
    @validator("codigo")
    def validate_codigo(cls, v):
        if not re.match(r"^EXP-\d{4}-\d{4}$", v):
            raise ValueError("Formato: EXP-YYYY-NNNN")
        return v
    
    @validator("tipo")
    def validate_tipo(cls, v):
        tipos_validos = ["in_vitro", "in_vivo", "patch_clamp", "bioluminiscencia", "ultrasonido"]
        if v not in tipos_validos:
            raise ValueError(f"Tipo debe ser uno de: {tipos_validos}")
        return v
    
    @validator("temperatura_C")
    def validate_temperatura(cls, v):
        if not (20 <= v <= 43):
            raise ValueError("Temperatura fuera de rango seguro")
        return v

class AnimalCreate(BaseModel):
    id_interno: str
    especie: str
    cepa: str
    sexo: str
    fecha_nacimiento: datetime
    peso_inicial_g: float
    
    @validator("sexo")
    def validate_sexo(cls, v):
        if v not in ["M", "H"]:
            raise ValueError("Sexo debe ser M o H")
        return v
    
    @validator("peso_inicial_g")
    def validate_peso(cls, v):
        if v <= 0:
            raise ValueError("Peso debe ser positivo")
        return v

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def generar_codigo_lote(fecha: datetime, sufijo: str = "A") -> str:
    """Genera código de lote MNT: MNT-YYYY-MM-DD-X"""
    return f"MNT-{fecha.year}-{fecha.month:02d}-{fecha.day:02d}-{sufijo}"

def generar_codigo_experimento(fecha: datetime, consecutivo: int) -> str:
    """Genera código de experimento: EXP-YYYY-NNNN"""
    return f"EXP-{fecha.year}-{consecutivo:04d}"

def calcular_fecha_vencimiento(almacenamiento: str, fecha_base: datetime = None) -> datetime:
    """Calcula fecha de vencimiento según condiciones de almacenamiento"""
    if fecha_base is None:
        fecha_base = datetime.utcnow()
    
    duraciones = {
        "4C": timedelta(days=7),
        "-20C": timedelta(days=30),
        "-80C": timedelta(days=90),
        "N2_liquido": timedelta(days=180)
    }
    
    return fecha_base + duraciones.get(almacenamiento, timedelta(days=7))

def evaluar_calidad_lote(lote: dict) -> dict:
    """Evalúa calidad de un lote de MNTs"""
    criterios = {
        "tamano": 80 <= lote["tamano_nm"] <= 150,
        "pdi": lote["pdi"] <= 0.25,
        "zeta": -25 <= lote["zeta_mV"] <= -15,
        "western_blot": lote["western_blot_ok"],
        "liberacion": lote["liberacion_eficiencia"] >= 70
    }
    
    todos_ok = all(criterios.values())
    
    return {
        "apto": todos_ok,
        "criterios": criterios,
        "fallas": [k for k, v in criterios.items() if not v]
    }

def calcular_score_neurologico_descripcion(score: int) -> str:
    """Convierte score numérico a descripción"""
    descripciones = {
        0: "Normal",
        1: "Leve (temblor, hipoactividad)",
        2: "Moderado (dificultad para caminar, deshidratación)",
        3: "Severo (convulsiones, parálisis) → EUTANASIA"
    }
    return descripciones.get(score, "Desconocido")

def verificar_criterios_eutanasia(animal: dict) -> bool:
    """Verifica si se deben aplicar criterios de eutanasia"""
    if animal.get("score_neurologico", 0) >= 3:
        return True
    if animal.get("perdida_peso_pct", 0) > 20:
        return True
    if animal.get("automutilacion", False):
        return True
    return False