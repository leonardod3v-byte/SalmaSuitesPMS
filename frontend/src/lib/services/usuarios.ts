import { apiFetch } from './api';
import type { Usuario } from '$lib/types/usuario';

export function fetchUsuarios(): Promise<Usuario[]> {
    return apiFetch<Usuario[]>('/auth/usuarios/');
}

export function createUsuario(data: {
    username: string;
    password: string;
    role: string;
    nombre_completo: string;
    email?: string;
}): Promise<Usuario> {
    return apiFetch<Usuario>('/auth/usuarios/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function updateUsuario(id: number, data: Partial<Usuario> & { password?: string }): Promise<Usuario> {
    return apiFetch<Usuario>(`/auth/usuarios/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

export function deleteUsuario(id: number): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/auth/usuarios/${id}/`, {
        method: 'DELETE',
    });
}

export function cambiarPassword(oldPassword: string, newPassword: string, confirmPassword: string): Promise<{ message: string }> {
    return apiFetch<{ message: string }>('/auth/cambiar-password/', {
        method: 'POST',
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword, confirm_password: confirmPassword }),
    });
}