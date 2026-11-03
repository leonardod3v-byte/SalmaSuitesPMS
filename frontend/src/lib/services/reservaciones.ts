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
export function realizarCheckin(id: number, acompanantesExtra: number[] = []): Promise<Reservacion> {
    return apiFetch<Reservacion>(`/reservaciones/${id}/checkin/`, {
        method: 'POST',
        body: JSON.stringify({ acompanantes_extra: acompanantesExtra }),
    });
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

export function fetchSaldo(reservaId: number): Promise<ResumenCheckout> {
    return apiFetch<ResumenCheckout>(`/reservaciones/${reservaId}/saldo/`);
}
