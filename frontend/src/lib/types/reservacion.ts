export interface HuespedBasico {
    id: number;
    tipo_documento: string;
    numero_documento: string;
    nombres: string;
    apellidos: string;
    fecha_nacimiento: string;
    edad: number;
    nacionalidad: string;
    estado_civil: string;
    telefono: string;
    email: string;
    direccion: string;
    alergias: string;
    ocupacion_nombre?: string;
    ocupacion_color?: string;
}

export interface Acompanante {
    id: number;
    id_huesped: number;
    rol: 'Titular' | 'Acompañante';
    huesped_detalle: HuespedBasico;
}

export interface Reservacion {
    id: number;
    id_huesped_titular: number;
    id_habitacion: number;
    fecha_entrada: string;
    fecha_salida: string;
    numero_noches: number;
    total_habitacion: string;
    estado: 'Confirmada' | 'EnCurso' | 'Finalizada' | 'Cancelada' | 'NoShow';
    modalidad_pago: 'Contado' | 'Abono' | 'Crédito';
    metodo_pago_inicial: string | null;
    numero_referencia_inicial: string;
    requiere_factura: boolean;
    acta: string;
    motivo_cancelacion: string;
    monto_total_consumos: string;
    monto_total_final: string;
    monto_pagado: string;
    saldo_pendiente: string;
    fecha_checkin_real: string | null;
    fecha_checkout_real: string | null;
    huesped_nombre?: string;
    huesped_documento?: string;
    huesped_titular_detalle?: HuespedBasico;
    habitacion_numero?: string;
    ocupacion_nombre?: string;
    ocupacion_color?: string;
    acompanantes?: Acompanante[];
}

export interface ReservaListItem {
    id: number;
    fecha_entrada: string;
    fecha_salida: string;
    estado: string;
    habitacion_numero: string;
    huesped_nombre: string;
    huesped_documento: string;
    ocupacion_nombre?: string;
    ocupacion_color?: string;
    empresa_nombre?: string;
}

export interface Consumo {
    id: number;
    id_reservacion: number;
    fecha_hora: string;
    descripcion: string;
    cantidad: number;
    precio_unitario: number;
    total: string;
    tipo_consumo: string;
    producto_id: number | null;
    producto_nombre: string | null;
    producto_precio: string | null;
}

export interface Pago {
    id: number;
    id_reservacion: number;
    fecha_hora: string;
    monto: string;
    metodo_pago: 'Efectivo' | 'Tarjeta' | 'PagoMovil';
    numero_referencia: string;
}

export interface ResumenCheckout {
    total_habitacion: string;
    total_consumos: string;
    total_final: string;
    monto_pagado: string;
    saldo_pendiente: string;
}
