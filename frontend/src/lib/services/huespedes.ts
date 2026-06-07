import { apiFetch } from './api';

// ── Tipos ──────────────────────────────────────────────────────────────────

export interface Acompanante {
    nombre:    string;
    documento: string;
    edad:      number;
}

export interface HuespedListItem {
    id:                   number;
    nombre_completo:      string;
    documento_formateado: string;
    telefono:             string;
    email:                string;
    es_vip:               boolean;
    created_at:           string;
}

export interface Huesped extends HuespedListItem {
    tipo_documento:    'V' | 'E' | 'J' | 'G' | 'P';
    numero_documento:  string;
    nombre:            string;
    apellido:          string;
    notas:             string;
    acompanantes:      Acompanante[];
    updated_at:        string;
}

// ⚠️ Sin Pick<Huesped, ...> — declarado directamente para evitar el error SSR
export interface HuespedPayload {
    tipo_documento:   'V' | 'E' | 'J' | 'G' | 'P';
    numero_documento: string;
    nombre:           string;
    apellido:         string;
    telefono:         string;
    email:            string;
    notas:            string;
    acompanantes:     Acompanante[];
}

// ── API ────────────────────────────────────────────────────────────────────

export const huespedesApi = {
    getAll: (params = '') =>
        apiFetch<HuespedListItem[]>(`/huespedes/${params}`),

    getById: (id: number) =>
        apiFetch<{ huesped: Huesped; historial_reservas: unknown[] }>(`/huespedes/${id}/`),

    create: (data: HuespedPayload) =>
        apiFetch<Huesped>('/huespedes/', { method: 'POST', body: JSON.stringify(data) }),

    update: (id: number, data: Partial<HuespedPayload>) =>
        apiFetch<Huesped>(`/huespedes/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),

    toggleVip: (id: number, es_vip: boolean) =>
        apiFetch<Huesped>(`/huespedes/${id}/`, { method: 'PUT', body: JSON.stringify({ es_vip }) }),

    delete: (id: number) =>
        apiFetch(`/huespedes/${id}/`, { method: 'DELETE' }),

    buscarPorDocumento: (documento: string) =>
        apiFetch<{ encontrado: boolean; huesped?: Huesped }>(
            `/huespedes/buscar/?documento=${encodeURIComponent(documento)}`
        ),

    search: (query: string) => {
        return apiFetch<HuespedListItem[]>(`/huespedes/?search=${encodeURIComponent(query)}`);
},
};