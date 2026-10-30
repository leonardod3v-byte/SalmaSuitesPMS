import { apiFetch } from './api';
import type { Empresa } from '$lib/types/empresa';

export function fetchEmpresas(params?: string): Promise<Empresa[]> {
    const query = params ? `?${params}` : '';
    return apiFetch<Empresa[]>(`/empresas/${query}`);
}

export function fetchEmpresa(id: number): Promise<Empresa> {
    return apiFetch<Empresa>(`/empresas/${id}/`);
}

export function createEmpresa(data: any): Promise<Empresa> {
    return apiFetch<Empresa>('/empresas/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function updateEmpresa(id: number, data: any): Promise<Empresa> {
    return apiFetch<Empresa>(`/empresas/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

export function deleteEmpresa(id: number): Promise<any> {
    return apiFetch<any>(`/empresas/${id}/`, {
        method: 'DELETE',
    });
}
