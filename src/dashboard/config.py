"""
Configuración del Dashboard MANTIS
"""

# Base de datos
DATABASE_URL = "sqlite:///data/mantis.db"

# Parámetros de seguridad
MAX_THERMAL_INDEX = 0.7
MAX_MECHANICAL_INDEX = 0.5
MAX_TEMPERATURE = 43.0  # °C
MIN_SEAL_RESISTANCE = 1.0  # GΩ

# Parámetros de MNTs
MNT_SIZE_MIN = 80  # nm
MNT_SIZE_MAX = 150  # nm
MNT_PDI_MAX = 0.25
MNT_ZETA_MIN = -25  # mV
MNT_ZETA_MAX = -15  # mV

# Clearance
CLEARANCE_TARGET_HOURS = 72
CLEARANCE_TARGET_PERCENTAGE = 90  # %

# Alertas
ALERT_EMAIL_ENABLED = False  # Configurar si se desea notificación por email
ALERT_THRESHOLD_DEVIATION = 10  # %

# Versión
MANTIS_VERSION = "1.2"
DASHBOARD_VERSION = "1.0.0"