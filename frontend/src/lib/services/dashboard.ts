import { apiFetch } from './api';

export const dashboardApi = {
    getStats: () => apiFetch('/dashboard/stats/'),
    getOcupacionSemanal: () => apiFetch('/dashboard/ocupacion-semanal/'),
    getHabitacionesGrid: () => apiFetch('/dashboard/habitaciones-grid/'),
    getActividades: () => apiFetch('/dashboard/actividades/'),
    getAlertas: () => apiFetch('/dashboard/alertas/')
};