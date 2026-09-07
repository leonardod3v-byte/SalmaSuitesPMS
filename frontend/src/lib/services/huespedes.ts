import { apiFetch } from "./api";
import type { Huesped, HuespedCreate } from "$lib/types/huesped";

export function fetchHuespedes(params?: string): Promise<Huesped[]> {
    const query = params ? `?${params}` : "";
    return apiFetch<Huesped[]>(`/huespedes/${query}`);
}

export function fetchHuesped(id: number): Promise<Huesped> {
    return apiFetch<Huesped>(`/huespedes/${id}/`);
}

export function createHuesped(data: HuespedCreate): Promise<Huesped> {
    return apiFetch<Huesped>("/huespedes/", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export function updateHuesped(
    id: number,
    data: Partial<HuespedCreate>,
    ): Promise<Huesped> {
    return apiFetch<Huesped>(`/huespedes/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}

export function checkDisponibilidad(
    id: number,
    ): Promise<{ disponible: boolean }> {
    return apiFetch<{ disponible: boolean }>(`/huespedes/${id}/disponibilidad/`);
}

export function getExportUrl(): string {
    const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
    return `${API_URL}/huespedes/exportar/`;
}