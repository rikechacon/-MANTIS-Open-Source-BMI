"""
Gestión de base de datos para MANTIS Dashboard
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Crear directorio data si no existe
os.makedirs("data", exist_ok=True)

# Configuración de base de datos
engine = create_engine("sqlite:///data/mantis.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# MODELOS
# ============================================================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    rol = Column(String)  # admin, operador, investigador
    certificacion_bsl2 = Column(Boolean, default=False)
    fecha_certificacion = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    
    experimentos = relationship("Experimento", back_populates="operador")

class LoteMNT(Base):
    __tablename__ = "lotes_mnt"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    fecha_sintesis = Column(DateTime, default=datetime.utcnow)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Caracterización
    tamano_nm = Column(Float)
    pdi = Column(Float)
    zeta_mV = Column(Float)
    concentracion_particulas_mL = Column(Float)
    
    # Control de calidad
    western_blot_ok = Column(Boolean)
    liberacion_eficiencia = Column(Float)  # %
    estabilidad_7d = Column(Boolean)
    
    # Estado
    estado = Column(String)  # sintetizado, en_uso, agotado, descartado
    fecha_vencimiento = Column(DateTime)
    almacenamiento = Column(String)  # 4C, -20C, -80C, N2_liquido
    
    operador = relationship("Usuario")
    experimentos = relationship("Experimento", back_populates="lote_mnt")

class Experimento(Base):
    __tablename__ = "experimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    lote_mnt_id = Column(Integer, ForeignKey("lotes_mnt.id"))
    
    # Tipo de experimento
    tipo = Column(String)  # in_vitro, in_vivo, patch_clamp, bioluminiscencia, ultrasonido
    
    # Parámetros
    protocolo = Column(String)
    duracion_min = Column(Float)
    temperatura_C = Column(Float)
    
    # Resultados
    exito = Column(Boolean)
    correlacion_r = Column(Float, nullable=True)
    snr_db = Column(Float, nullable=True)
    latencia_ms = Column(Float, nullable=True)
    
    # Incidentes
    incidente = Column(Boolean, default=False)
    descripcion_incidente = Column(Text, nullable=True)
    desviacion_protocolo = Column(Boolean, default=False)
    descripcion_desviacion = Column(Text, nullable=True)
    
    # Notas
    notas = Column(Text, nullable=True)
    
    operador = relationship("Usuario", back_populates="experimentos")
    lote_mnt = relationship("LoteMNT", back_populates="experimentos")
    animales = relationship("AnimalExperimento", back_populates="experimento")

class Animal(Base):
    __tablename__ = "animales"
    
    id = Column(Integer, primary_key=True, index=True)
    id_interno = Column(String, unique=True, index=True)
    especie = Column(String)
    cepa = Column(String)
    sexo = Column(String)
    fecha_nacimiento = Column(DateTime)
    peso_inicial_g = Column(Float)
    
    # Estado
    estado = Column(String)  # aclimatacion, activo, eutanasia, fallecido
    fecha_ingreso = Column(DateTime)
    fecha_salida = Column(DateTime, nullable=True)
    
    experimentos = relationship("AnimalExperimento", back_populates="animal")

class AnimalExperimento(Base):
    __tablename__ = "animales_experimento"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animales.id"))
    experimento_id = Column(Integer, ForeignKey("experimentos.id"))
    
    # Monitoreo
    peso_g = Column(Float)
    score_neurologico = Column(Integer)  # 0-3
    signos_vitales_ok = Column(Boolean)
    
    # Procedimiento
    anestesia_mg_kg = Column(Float, nullable=True)
    microburbujas_uL = Column(Float, nullable=True)
    us_presion_MPa = Column(Float, nullable=True)
    us_duracion_s = Column(Float, nullable=True)
    mnt_particulas = Column(Float, nullable=True)
    
    # Outcome
    eutanasia = Column(Boolean, default=False)
    causa_eutanasia = Column(String, nullable=True)
    
    animal = relationship("Animal", back_populates="experimentos")
    experimento = relationship("Experimento", back_populates="animales")

class Residuo(Base):
    __tablename__ = "residuos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    tipo = Column(String)  # biologico, quimico, punzocortante, radiactivo
    cantidad_kg = Column(Float)
    tratamiento = Column(String)  # autoclave, gestor_externo, decaimiento
    destino_final = Column(String)
    
    notas = Column(Text, nullable=True)
    
    operador = relationship("Usuario")

class Alerta(Base):
    __tablename__ = "alertas"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    nivel = Column(String)  # info, warning, critical
    categoria = Column(String)  # seguridad, equipo, protocolo, animal
    mensaje = Column(Text)
    resuelta = Column(Boolean, default=False)
    fecha_resolucion = Column(DateTime, nullable=True)
    resuelta_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

# ============================================================
# FUNCIONES DE INICIALIZACIÓN
# ============================================================

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Obtiene una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar base de datos al importar
init_db()