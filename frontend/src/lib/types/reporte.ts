export interface ResumenDiario {
    total_general: string;
    total_efectivo: string;
    total_tarjeta: string;
    total_pago_movil: string;
    cantidad_transacciones: number;
    cerrado: boolean;
    detalle: TransaccionDiaria[];
}

export interface TransaccionDiaria {
    hora: string;
    reserva_id: number;
    huesped: string;
    metodo_pago: string;
    numero_referencia: string;
    monto: string;
}

export interface IngresoPeriodo {
    fecha: string;
    total: string;
    efectivo: string;
    tarjeta: string;
    pago_movil: string;
}