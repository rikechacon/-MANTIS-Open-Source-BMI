# Changelog

Todos los cambios notables en el proyecto MANTIS serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-11-04

### Added
- Aplicación clínica propuesta: Enfermedad de Parkinson (aDBS)
- Dashboard de monitoreo experimental (Python/Streamlit)
- Criterios explícitos de falsación de hipótesis
- Separación de niveles de evidencia (Tabla 2)
- Modelo fenomenológico de gating con parámetros medibles

### Changed
- Backscatter armónico reformulado como hipótesis no demostrada
- Coeficientes η_s, η_c marcados como "a determinar experimentalmente"
- Densidad de MNTs eliminada (sin justificación experimental previa)
- Métricas realistas: 400-600 µm, 30-50 ms, r > 0.7

### Removed
- Valor α = 0.35 (sin fuente)
- Afirmaciones de resultados in silico al nivel de EEG/fMRI
- TRPV1 como "fusible de seguridad garantizado"

### Fixed
- Ci-VSP reemplazado por hipótesis de nanoporo voltage-gated
- Umbral térmico corregido a 43°C (fisiológicamente plausible)
- Clearance objetivo ajustado a 72 h (no 48 h)

## [1.1.0] - 2026-02-15

### Added
- Optimización a 128 elementos para viabilidad hardware
- Corrección de aberración craneal (time-reversal)
- Protocolo de seguridad: TI < 0.7, PCD, CEM43

## [1.0.0] - 2026-01-10

### Added
- Concepto teórico inicial
- Arquitectura de 1024 elementos
- DOI: 10.21203/rs.3.rs-8670918/v1