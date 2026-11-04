# MANTIS: Molecular-Acoustic Neural Transduction Interface System

[![DOI](https://img.shields.io/badge/DOI-10.21203%2Frs.3.rs--8670918%2Fv1-blue)](https://doi.org/10.21203/rs.3.rs-8670918/v1)
> **Note on Hardware Specs:** > The original preprint (v1) describes a theoretical 1024-element system. 
> This repository and the currently submitted manuscript implement the **optimized 128-element architecture** for immediate hardware feasibility. 
> The simulation code provided here corresponds to the 128-element configuration.
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Prototype](https://img.shields.io/badge/Status-Research%20Prototype-orange.svg)]()

## 🧠 Overview
**MANTIS** is an open-source framework designed to democratize high-resolution Brain-Machine Interfaces (BMI). Unlike invasive implants or low-resolution EEG, MANTIS utilizes **focused ultrasound** and **voltage-sensitive nanotransducers (MNTs)** to decode neural activity through the intact skull with sub-millimeter precision.

This repository contains the simulation code, hardware specifications, and implementation roadmap accompanying the preprint:
> **"Non-invasive neural decoding at millisecond resolution via ultrasound-gated molecular transducers"**
> *Enrique Chacón-Pinzón*
> [Read the full preprint on Research Square](https://doi.org/10.21203/rs.3.rs-8670918/v1)

## 📂 Repository Structure

| Folder | Description |
| :--- | :--- |
| `/docs` | Full implementation roadmap (v1.0), Preprint PDF, and Supplementary Materials. |
| `/simulation` | Python physics engine based on the **Marmottant equation** for modeling nonlinear bubble dynamics. |
| `/hardware` | Specifications for the 128-element phased array and OpenUS/FPGA architecture. |
| `/figures` | High-resolution diagrams of the MANTIS framework and TTHA decoder architecture. |

## 🚀 Key Features
- **Non-Invasive:** Operates through the skull using 1-5 MHz ultrasound.
- **High Resolution:** Decodes neural spikes via nonlinear acoustic harmonics (2f, 3f).
- **Open Hardware:** Designed for 128-element phased arrays using FPGA-based controllers (OpenUS/Red Pitaya).
- **Physics-Driven:** Includes a custom `marmottant_bubble_dynamics.py` engine to simulate voltage-dependent acoustic signatures.

## 🛠️ Getting Started (Simulation)

To run the bubble dynamics simulation and observe the harmonic shift:

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/MANTIS-Open-Source-BMI.git](https://github.com/YOUR_USERNAME/MANTIS-Open-Source-BMI.git)

# Navigate to simulation folder
cd MANTIS-Open-Source-BMI/simulation

# Run the physics engine
python marmottant_bubble_dynamics.py
```
## 📋 Changelog

### v1.2 (Noviembre 2026) - Current
- **Hipótesis conservadoras**: Backscatter armónico marcado como hipótesis no demostrada
- **Eliminación de valores sin fuente**: Coeficientes η_s, η_c ahora son parámetros a medir
- **Aplicación clínica**: Propuesta para Parkinson (aDBS no invasivo)
- **Separación de evidencia**: Tabla explícita modalidades establecidas vs objetivos de diseño
- **Criterios de falsación**: Lista de 4 criterios para rechazar la hipótesis
- **Dashboard de trazabilidad**: Sistema Python/Streamlit para registro experimental

### v1.1 (Febrero 2026)
- Optimización a arquitectura de 128 elementos
- Corrección de aberración craneal implementada
- Protocolo de seguridad térmica y cavitación

### v1.0 (Enero 2026)
- Concepto teórico inicial (1024 elementos)
- DOI: 10.21203/rs.3.rs-8670918/v1
🤝 Roadmap & Collaboration
We are actively seeking collaborators for the Phase II (Wet-Lab Validation):

FPGA Engineering: Optimization of beamforming on OpenUS.

Microfluidics: Synthesis of lipid-shelled nanotransducers.

Neuroscience: In vitro MEA validation.

Please refer to docs/Implementation_Plan_v1.pdf for the detailed project timeline.

📜 Citation
If you use MANTIS in your research, please cite:

Chacón-Pinzón, E. (2026). Non-invasive neural decoding at millisecond resolution via ultrasound-gated molecular transducers. Research Square. DOI: 10.21203/rs.3.rs-8670918/v1
