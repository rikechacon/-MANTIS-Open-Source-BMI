% MANTIS_Transducer_Sim.m
% Simulación de propagación acústica para MANTIS v1.0
% Hardware: 128-element Linear Phased Array @ 5 MHz
% Requisitos: k-Wave Toolbox (http://www.k-wave.org)
% Autor: Enrique Chacón-Pinzón

clear all;

% --- 1. Definición del Dominio (Grid) ---
c0 = 1540;              % Velocidad del sonido en tejido [m/s]
f0 = 5e6;               % Frecuencia central: 5 MHz
lambda = c0 / f0;       % Longitud de onda [m]

dx = lambda / 4;        % Resolución de la malla (4 puntos por onda)
Nx = 512;               % Tamaño en X (eje lateral)
Ny = 1024;              % Tamaño en Y (eje profundidad)

kgrid = kWaveGrid(Nx, dx, Ny, dx);

% --- 2. Definición del Medio ---
medium.sound_speed = c0;
medium.density = 1000;  % [kg/m^3]
medium.alpha_coeff = 0.75; % Atenuación [dB/(MHz^y cm)]
medium.alpha_power = 1.5;

% --- 3. Definición del Transductor (128 Elementos) ---
% Creación de una fuente lineal (apertura)
source.p_mask = zeros(Nx, Ny);
num_elements = 128;
element_width = round(lambda / dx); 
pitch = round(lambda / 2 / dx); % Pitch de medio lambda para evitar lóbulos de rejilla
start_index = round(Nx/2 - (num_elements * pitch)/2);

% Colocar elementos en la máscara
for i = 1:num_elements
    pos = start_index + (i-1)*pitch;
    source.p_mask(pos : pos+element_width, 10) = 1; % Posición en Y=10
end

% --- 4. Beamforming (Enfoque) ---
% Definir punto focal
focus_depth = 30e-3;    % 30 mm de profundidad
focus_pos = [0, focus_depth];

% Crear señal de entrada (Tone Burst)
sampling_freq = 50e6;   % 50 MHz
tone_burst_cycles = 5;
source_sig = toneBurst(sampling_freq, f0, tone_burst_cycles);

% Calcular retardos (Beamforming) para enfocar
% (Simplificación geométrica para demostración)
element_positions = (-(num_elements-1)/2 : (num_elements-1)/2) * (c0/f0/2);
delays = sqrt(focus_depth^2 + element_positions.^2) / c0;
delays = delays - min(delays); % Normalizar
source.p = createMultiElementToneBurst(kgrid, source.p_mask, row_freq, delays, source_sig);

% --- 5. Ejecutar Simulación ---
sensor.mask = ones(Nx, Ny); % Grabar campo máximo en todo el dominio
sensor.record = {'p_max'};

input_args = {'DisplayMask', source.p_mask, 'PlotLayout', true, 'PlotPML', false};
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});

% --- 6. Visualización ---
figure;
imagesc(kgrid.x_vec * 1e3, kgrid.y_vec * 1e3, sensor_data.p_max');
colormap(jet);
ylabel('Profundidad [mm]');
xlabel('Posición Lateral [mm]');
title('Perfil de Haz MANTIS (128-ch, 5MHz)');
colorbar;