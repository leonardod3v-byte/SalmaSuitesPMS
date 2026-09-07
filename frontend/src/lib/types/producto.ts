export interface Producto {
    id: number;
    nombre: string;
    descripcion: string;
    categoria: string;
    precio_venta: string;
    stock_actual: string;
    stock_minimo: string;
    unidad: string;
    activo: boolean;
    maneja_stock: boolean;
    estado_stock?: 'Normal' | 'Bajo' | 'Agotado';
}
export interface MovimientoInventario {
    id: number;
    producto: number;
    producto_nombre: string;
    tipo: 'entrada' | 'salida' | 'ajuste';
    cantidad: string;
    fecha: string;
    motivo: string;
    usuario_nombre: string;
}