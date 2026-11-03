import { apiFetch } from './api';
import type { Ocupacion } from '$lib/types/configuracion';

export function fetchOcupaciones(): Promise<Ocupacion[]> {
    return apiFetch<Ocupacion[]>('/configuracion/ocupaciones/');
}

export function createOcupacion(data: { nombre: string; color: string }): Promise<Ocupacion> {
    return apiFetch<Ocupacion>('/configuracion/ocupaciones/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function updateOcupacion(id: number, data: Partial<Ocupacion>): Promise<Ocupacion> {
    return apiFetch<Ocupacion>(`/configuracion/ocupaciones/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

export function deleteOcupacion(id: number): Promise<void> {
    return apiFetch<void>(`/configuracion/ocupaciones/${id}/`, {
        method: 'DELETE',
    });
}
