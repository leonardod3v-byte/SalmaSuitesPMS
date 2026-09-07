import { apiFetch } from './api';
import type { Producto, MovimientoInventario } from '$lib/types/producto';

// Productos
export function fetchProductos(params?: string): Promise<Producto[]> {
    const query = params ? `?${params}` : '';
    return apiFetch<Producto[]>(`/inventario/productos/${query}`);
}

export function fetchProducto(id: number): Promise<Producto> {
    return apiFetch<Producto>(`/inventario/productos/${id}/`);
}

export function createProducto(data: any): Promise<Producto> {
    return apiFetch<Producto>('/inventario/productos/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function updateProducto(id: number, data: any): Promise<Producto> {
    return apiFetch<Producto>(`/inventario/productos/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

export function deactivateProducto(id: number): Promise<void> {
    return apiFetch<void>(`/inventario/productos/${id}/`, {
        method: 'DELETE',
    });
}

// Movimientos
export function fetchMovimientos(params?: string): Promise<MovimientoInventario[]> {
    const query = params ? `?${params}` : '';
    return apiFetch<MovimientoInventario[]>(`/inventario/movimientos/${query}`);
}

export function registrarEntrada(data: { producto_id: number; cantidad: number; motivo: string }): Promise<MovimientoInventario> {
    return apiFetch<MovimientoInventario>('/inventario/entradas/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export function registrarAjuste(data: { producto_id: number; cantidad: number; motivo: string }): Promise<MovimientoInventario> {
    return apiFetch<MovimientoInventario>('/inventario/ajustes/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Alertas
export function fetchProductosBajos(): Promise<{ productos_bajos: number }> {
    return apiFetch<{ productos_bajos: number }>('/inventario/alertas/bajos/');
}