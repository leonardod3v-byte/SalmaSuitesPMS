import { apiFetch } from './api';
import type { Reservacion, ReservaListItem, Consumo, Pago, ResumenCheckout } from '$lib/types/reservacion';

// Lista
export function fetchReservaciones(params?: string): Promise<Reservacion[]> {
    const query = params ? `?${params}` : '';
    return apiFetch<Reservacion[]>(`/reservaciones/${query}`);
}

// Calendario
export function fetchReservasCalendario(semanaInicio: string): Promise<ReservaListItem[]> {
    return apiFetch<ReservaListItem[]>(`/reservaciones/?desde=${semanaInicio}&hasta=${semanaInicio}&formato=calendario`);
}

// CRUD
export function fetchReservacion(id: number): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/`);
}

export function createReservacion(data: any): Promise<Reservacion> {
    return apiFetch<Reservacion>('/reservaciones/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Acciones
export function realizarCheckin(id: number): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/checkin/`, { method: 'POST' });
}

export function realizarCheckout(id: number): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/checkout/`, { method: 'POST' });
}

export function cancelarReservacion(id: number, motivo: string, acta?: string): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/cancelar/`, {
        method: 'POST',
        body: JSON.stringify({ motivo, acta }),
    });
}

export function marcarNoshow(id: number, motivo: string, acta?: string): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/noshow/`, {
        method: 'POST',
        body: JSON.stringify({ motivo, acta }),
    });
}

export function fetchResumenCheckout(id: number): Promise<ResumenCheckout> {
    return apiFetch<ResumenCheckout>(`/reservaciones/${id}/resumen-checkout/`);
}

// Consumos
export function fetchConsumos(reservaId: number): Promise<Consumo[]> {
    return apiFetch<Consumo[]>(`/reservaciones/${reservaId}/consumos/`);
}

export function agregarConsumo(reservaId: number, data: any): Promise<Consumo> {
    return apiFetch<Consumo>(`/reservaciones/${reservaId}/consumos/`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Pagos
export function fetchPagos(reservaId: number): Promise<Pago[]> {
    return apiFetch<Pago[]>(`/reservaciones/${reservaId}/pagos/`);
}

export function registrarPago(reservaId: number, data: any): Promise<Pago> {
    return apiFetch<Pago>(`/reservaciones/${reservaId}/pagos/`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Colores para el calendario
export const TIPOS_CLIENTE: Record<string, { label: string; color: string; bg: string; text: string }> = {
    'Particular': { label: 'Particular', color: '#9E9E9E', bg: '#9E9E9E15', text: '#9E9E9E' },
    'Empresario': { label: 'Empresario', color: '#607D8B', bg: '#607D8B15', text: '#607D8B' },
    'Turista': { label: 'Turista', color: '#FF5722', bg: '#FF572215', text: '#FF5722' },
    'Militar': { label: 'Militar', color: '#4CAF50', bg: '#4CAF5015', text: '#4CAF50' },
    'Político': { label: 'Político', color: '#2196F3', bg: '#2196F315', text: '#2196F3' },
    'Artista': { label: 'Artista', color: '#FF9800', bg: '#FF980015', text: '#FF9800' },
    'Deportista': { label: 'Deportista', color: '#E91E63', bg: '#E91E6315', text: '#E91E63' },
    'Diplomático': { label: 'Diplomático', color: '#3F51B5', bg: '#3F51B515', text: '#3F51B5' },
    'Médico': { label: 'Médico', color: '#00BCD4', bg: '#00BCD415', text: '#00BCD4' },
    'Religioso': { label: 'Religioso', color: '#FFEB3B', bg: '#FFEB3B15', text: '#FFEB3B' },
    'Ejecutivo de Ventas': { label: 'Ejecutivo Ventas', color: '#795548', bg: '#79554815', text: '#795548' },
    'Comerciante': { label: 'Comerciante', color: '#8BC34A', bg: '#8BC34A15', text: '#8BC34A' },
};