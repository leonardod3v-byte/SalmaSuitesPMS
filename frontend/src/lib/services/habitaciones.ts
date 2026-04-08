import { apiFetch } from './api';

export const habitacionesApi = {
    getAll: (params: string = '') => apiFetch<any[]>(`/habitaciones/${params}`),
    getTipos: () => apiFetch<any[]>('/habitaciones/tipos/'),
    
    updateStatus: (id: number | string, estado: string) => 
        apiFetch(`/habitaciones/${id}/`, { 
            method: 'PATCH', 
            body: JSON.stringify({ estado }) 
        }),

    create: (data: object) => apiFetch('/habitaciones/', { method: 'POST', body: JSON.stringify(data) }),
    
    update: (id: number | string, data: object) => 
        apiFetch(`/habitaciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
        
    delete: (id: number | string) => apiFetch(`/habitaciones/${id}/`, { method: 'DELETE' })
};