import { apiFetch } from './api';
import type { Habitacion, HabitacionCreate } from '$lib/types/habitacion';

export function fetchHabitaciones(params?: string): Promise<Habitacion[]> {
    const query = params ? `?${params}` : '';
    return apiFetch<Habitacion[]>(`/habitaciones/${query}`);
}

export function fetchHabitacion(id: number): Promise<Habitacion> {
    return apiFetch<Habitacion>(`/habitaciones/${id}/`);
}

export function createHabitacion(data: HabitacionCreate): Promise<Habitacion> {
    return apiFetch<Habitacion>('/habitaciones/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function updateHabitacion(id: number, data: Partial<HabitacionCreate>): Promise<Habitacion> {
    return apiFetch<Habitacion>(`/habitaciones/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

export function cambiarEstadoHabitacion(id: number, estado: string, notas?: string): Promise<Habitacion> {
    return apiFetch<Habitacion>(`/habitaciones/${id}/cambiar-estado/`, {
        method: 'POST',
        body: JSON.stringify({ estado, notas }),
    });
}

export function fetchDisponibles(): Promise<Habitacion[]> {
    return apiFetch<Habitacion[]>('/habitaciones/disponibles/');
}
