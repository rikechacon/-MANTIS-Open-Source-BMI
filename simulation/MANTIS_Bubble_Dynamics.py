import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN FÍSICA (CONSTANTES) ---
R0 = 2.0e-6         # Radio inicial de la burbuja (2 micras)
rho_L = 998         # Densidad del medio (agua/tejido) [kg/m^3]
P0 = 101325         # Presión ambiental [Pa]
c = 1480            # Velocidad del sonido en el medio [m/s]
mu_L = 0.001        # Viscosidad del medio [Pa.s]
kappa = 1.07        # Índice politrópico del gas (PFH)
sigma_0 = 0.072     # Tensión superficial base (agua) [N/m]
chi = 1.0           # Elasticidad de la carcasa (shell elasticity) [N/m]

# --- PARÁMETROS DE ESTIMULACIÓN (ULTRASONIDO) ---
f_drive = 5.0e6     # Frecuencia de excitación: 5 MHz (In vitro)
P_ac_amp = 100e3    # Presión acústica: 100 kPa (Baja potencia)

# --- MODELO DE MARMOTTANT (Tensión superficial dinámica) ---
def surface_tension(R):
    """
    Modelo de Marmottant para la tensión superficial sigma(R).
    Define tres regímenes: Buckling (Pandeo), Elástico, Ruptura.
    """
    R_buckling = R0  # Simplificación: radio de pandeo cercano a R0
    R_rupture = R_buckling * (1 + sigma_0 / chi)
    
    if R <= R_buckling:
        return 0  # Estado de pandeo (sin tensión)
    elif R >= R_rupture:
        return sigma_0  # Estado de ruptura (tensión de agua pura)
    else:
        return chi * ( (R/R_buckling)**2 - 1 ) # Estado elástico

# --- ECUACIÓN DIFERENCIAL (Rayleigh-Plesset Modificada) ---
def bubble_dynamics(y, t, f_freq, P_amp):
    R = y[0]    # Radio
    R_dot = y[1] # Velocidad de la pared
    
    # Presión acústica externa (Onda sinusoidal)
    P_drive = P_amp * np.sin(2 * np.pi * f_freq * t)
    
    # Términos de la ecuación
    sigma = surface_tension(R)
    
    # Término de amortiguación térmica y viscosa
    term1 = (P0 + 2*sigma/R0) * (R0/R)**(3*kappa) * (1 - (3*kappa*R_dot)/c)
    term2 = -P0 - P_drive - 2*sigma/R - 4*mu_L*R_dot/R
    
    # Aceleración de la pared de la burbuja (R_double_dot)
    R_ddot = (term1 + term2 - 1.5 * rho_L * R_dot**2) / (rho_L * R)
    
    return [R_dot, R_ddot]

# --- SIMULACIÓN ---
def run_simulation(voltage_effect=False):
    """
    Simula la respuesta de la burbuja. 
    Si voltage_effect=True, alteramos la elasticidad (chi) simulando Vm.
    """
    global chi
    original_chi = chi
    
    # Simulación del efecto del voltaje neuronal: Reduce la rigidez de la carcasa
    if voltage_effect:
        chi = 0.5 * original_chi 
        label = "Neurona Activa (Vm Despolarizado)"
    else:
        label = "Neurona Reposo"

    # Tiempo de simulación: 5 microsegundos (suficiente para ver ciclos)
    t = np.linspace(0, 5e-6, 5000) 
    
    # Condiciones iniciales [R, R_dot]
    y0 = [R0, 0.0]
    
    # Resolver ODE
    solution = odeint(bubble_dynamics, y0, t, args=(f_drive, P_ac_amp))
    
    # Restaurar valor original
    chi = original_chi
    
    return t, solution[:, 0], label

# --- EJECUCIÓN Y VISUALIZACIÓN ---
if __name__ == "__main__":
    print("Iniciando simulación física MANTIS (Modelo Marmottant)...")
    
    # 1. Correr simulación en Reposo vs Activa
    t, R_rest, label_rest = run_simulation(voltage_effect=False)
    t, R_active, label_active = run_simulation(voltage_effect=True)
    
    # 2. Calcular señal radiada (Scattered Pressure) ~ Aceleración del volumen
    # P_scat es proporcional a la segunda derivada del volumen V(t)
    # Aproximación simple: P_scat ~ R(t) - R0 para visualización de espectro
    
    # FFT (Análisis de Frecuencia)
    def get_spectrum(signal, dt):
        n = len(signal)
        freq = np.fft.rfftfreq(n, d=dt)
        mag = np.abs(np.fft.rfft(signal))
        return freq, mag

    dt = t[1] - t[0]
    freq, mag_rest = get_spectrum(R_rest - R0, dt)
    freq, mag_active = get_spectrum(R_active - R0, dt)

    # --- PLOTTEO ---
    plt.figure(figsize=(12, 8))
    
    # Gráfica Temporal (Oscilación)
    plt.subplot(2, 1, 1)
    
    plt.plot(t*1e6, R_rest*1e6, 'b', label=label_rest, alpha=0.7)
    plt.plot(t*1e6, R_active*1e6, 'r--', label=label_active)
    plt.ylabel('Radio de la Burbuja (µm)')
    plt.xlabel('Tiempo (µs)')
    plt.title('Dinámica Temporal del MNT (Modelo Marmottant)')
    plt.legend()
    plt.grid(True)
    
    # Gráfica Espectral (Armónicos)
    plt.subplot(2, 1, 2)
    
    # Normalizar para visualización
    plt.plot(freq/1e6, mag_rest, 'b', label=label_rest, alpha=0.7)
    plt.plot(freq/1e6, mag_active, 'r--', label=label_active)
    
    plt.xlim(0, 15) # Ver hasta 3er armónico (15 MHz)
    plt.axvline(x=5, color='k', linestyle=':', label='Fundamental (5 MHz)')
    plt.axvline(x=10, color='g', linestyle=':', label='2do Armónico (10 MHz)')
    plt.ylabel('Amplitud Espectral (u.a.)')
    plt.xlabel('Frecuencia (MHz)')
    plt.title('Firma Espectral: Cambio en Armónicos por Voltaje')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    print("Simulación completada. Observar diferencia en 2do armónico (10 MHz).")