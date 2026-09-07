import { apiFetch } from './api';
import type { ConfiguracionGeneral, ColorTipoCliente, ColorEstadoHabitacion } from '$lib/types/configuracion';

// Configuración general (clave-valor)
export function fetchConfiguracion(): Promise<ConfiguracionGeneral> {
    return apiFetch<ConfiguracionGeneral>('/configuracion/');
}

export function saveConfiguracion(data: Record<string, string>): Promise<{ message: string }> {
    return apiFetch<{ message: string }>('/configuracion/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Colores por tipo de cliente
export function fetchColoresTipoCliente(): Promise<ColorTipoCliente[]> {
    return apiFetch<ColorTipoCliente[]>('/configuracion/colores-clientes/');
}

export function saveColorTipoCliente(tipo_cliente_profesion: string, color: string): Promise<ColorTipoCliente> {
    return apiFetch<ColorTipoCliente>('/configuracion/colores-clientes/', {
        method: 'POST',
        body: JSON.stringify({ tipo_cliente_profesion, color }),
    });
}

// Colores por estado de habitación
export function fetchColoresEstadoHabitacion(): Promise<ColorEstadoHabitacion[]> {
    return apiFetch<ColorEstadoHabitacion[]>('/configuracion/colores-estados/');
}

export function saveColorEstadoHabitacion(estado: string, color: string): Promise<ColorEstadoHabitacion> {
    return apiFetch<ColorEstadoHabitacion>('/configuracion/colores-estados/', {
        method: 'POST',
        body: JSON.stringify({ estado, color }),
    });
}