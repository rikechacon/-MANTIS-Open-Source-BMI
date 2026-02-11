# Hardware Specifications: MANTIS v1.0

Este documento detalla los componentes físicos necesarios para la implementación del sistema de decodificación neuronal no invasiva.

## 1. Unidad de Adquisición de Datos (DAQ)
* **Plataforma:** FPGA Open-Source (Recomendado: **OpenUS** o **Red Pitaya STEMlab 125-14**).
* **Capacidad de Canales:** 128 canales independientes (multiplexados para Tx/Rx).
* **Tasa de Muestreo:** ≥ 40 MS/s (Mega Samples por segundo) para capturar armónicos hasta 15 MHz.
* **Interfaz:** Ethernet Gigabit / PCIe para transferencia de datos en tiempo real.

## 2. Phased Array Ultrasónico
* **Tipo:** Sonda Lineal Phased Array.
* **Elementos:** 128 elementos piezoeléctricos.
* **Frecuencia Central ($f_0$):** 5.0 MHz.
* **Ancho de Banda:** >60% para detección clara de $2f_0$ (10 MHz) y $3f_0$ (15 MHz).
* **Pitch:** $\lambda/2$ (aprox. 0.15 mm a 5 MHz) para evitar lóbulos de rejilla y optimizar el enfoque.

## 3. Estación de Procesamiento (Workstation)
* **GPU:** NVIDIA RTX 3080 o superior (mínimo 10GB VRAM) para procesamiento CUDA del Transformer (TTHA).
* **CPU:** Mínimo 8 núcleos (Ryzen 7 / Core i7) para gestión de buffers.
* **RAM:** 32 GB DDR4/DDR5.

## 4. Utilería de Laboratorio (Validación)
* **Fantoma:** Cubo de gel de agar con atenuación de 0.5 dB/cm/MHz.
* **Control Óptico:** Microscopio de fluorescencia para validación de nanotransductores mediante Quasar 670 (Solo fase in vitro).