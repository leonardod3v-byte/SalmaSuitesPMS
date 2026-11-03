import { apiFetch } from './api';
import type { ConfiguracionGeneral } from '$lib/types/configuracion';

export function fetchConfiguracion(): Promise<ConfiguracionGeneral> {
    return apiFetch<ConfiguracionGeneral>('/configuracion/configuracion-general/');
}

export function saveConfiguracion(data: Record<string, string>): Promise<{ message: string }> {
    return apiFetch<{ message: string }>('/configuracion/configuracion-general/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}
