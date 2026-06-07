import { apiFetch } from './api';

export const habitacionesApi = {
    /**
     * Obtiene todas las habitaciones (paginadas o con filtros).
     * @param params - query string opcional, ej: "?estado=libre&piso=1"
     */
    getAll: (params: string = '') => apiFetch<any[]>(`/habitaciones/${params}`),

    getTipos: () => apiFetch<any[]>('/habitaciones/tipos/'),

    /**
     * Cambia el estado de una habitación (limpia, sucia, mantenimiento, etc.).
     * Usa el endpoint específico que aplica reglas de negocio (ej. no cambiar si está ocupada).
     * @param id - ID de la habitación
     * @param estado - Nuevo estado (debe ser uno de los valores permitidos)
     */
    updateStatus: (id: number | string, estado: string) =>
        apiFetch(`/habitaciones/${id}/cambiar-estado/`, {
            method: 'POST',
            body: JSON.stringify({ estado })
        }),

    create: (data: object) => apiFetch('/habitaciones/', { method: 'POST', body: JSON.stringify(data) }),

    update: (id: number | string, data: object) =>
        apiFetch(`/habitaciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),

    delete: (id: number | string) => apiFetch(`/habitaciones/${id}/`, { method: 'DELETE' })
};