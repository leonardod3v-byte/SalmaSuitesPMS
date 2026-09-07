import { apiFetch } from './api';
import type { ResumenDiario, IngresoPeriodo } from '$lib/types/reporte';

export function fetchDiario(fecha: string): Promise<ResumenDiario> {
    return apiFetch<ResumenDiario>(`/reportes/diario/?fecha=${fecha}`);
}

export function fetchIngresos(inicio: string, fin: string, metodo?: string): Promise<IngresoPeriodo[]> {
    let url = `/reportes/ingresos/?inicio=${inicio}&fin=${fin}`;
    if (metodo) url += `&metodo=${metodo}`;
    return apiFetch<IngresoPeriodo[]>(url);
}

export function confirmarCierre(fecha: string): Promise<any> {
    return apiFetch('/bitacora/cierres/', {
        method: 'POST',
        body: JSON.stringify({ fecha }),
    });
}