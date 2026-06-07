import { apiFetch } from './api';

export type TipoCliente = 
  | 'particular' | 'militar' | 'politico' | 'artista' | 'empresarial'
  | 'deportista' | 'diplomatico' | 'medico' | 'religioso' | 'turista'
  | 'ejecutivo_ventas' | 'comerciante';

export const TIPOS_CLIENTE: Record<TipoCliente, { label: string; color: string; bg: string; text: string }> = {
  particular:        { label: 'Particular',        color: '#7340A0', bg: 'rgba(115,64,160,0.1)', text: '#7340A0' },
  militar:           { label: 'Militar / GN',      color: '#2D6A4F', bg: 'rgba(45,106,79,0.1)',   text: '#2D6A4F' },
  politico:          { label: 'Político / Gov.',   color: '#9B2226', bg: 'rgba(155,34,38,0.1)',    text: '#9B2226' },
  artista:           { label: 'Artista / Medios',  color: '#1E3A5F', bg: 'rgba(30,58,95,0.1)',     text: '#1E3A5F' },
  empresarial:       { label: 'Empresarial',       color: '#B38E5D', bg: 'rgba(179,142,93,0.1)',   text: '#B38E5D' },
  deportista:        { label: 'Deportista',        color: '#1B5E20', bg: 'rgba(27,94,32,0.1)',     text: '#1B5E20' },
  diplomatico:       { label: 'Diplomático',       color: '#4A148C', bg: 'rgba(74,20,140,0.1)',    text: '#4A148C' },
  medico:            { label: 'Médico',            color: '#006064', bg: 'rgba(0,96,100,0.1)',     text: '#006064' },
  religioso:         { label: 'Religioso',         color: '#E65100', bg: 'rgba(230,81,0,0.1)',     text: '#E65100' },
  turista:           { label: 'Turista / Agencia', color: '#37474F', bg: 'rgba(55,71,79,0.1)',     text: '#37474F' },
  ejecutivo_ventas:  { label: 'Ejecutivo de Ventas', color: '#C97B0A', bg: 'rgba(201,123,10,0.1)', text: '#C97B0A' },
  comerciante:       { label: 'Comerciante',       color: '#2C7DA0', bg: 'rgba(44,125,160,0.1)',   text: '#2C7DA0' },
};

export interface ReservaListItem {
  consumos: never[];
  pagos: never[];
  id: number;
  estado: string;
  fecha_entrada: string;
  fecha_salida: string;
  noches: number;
  huesped_nombre: string;
  huesped_documento: string;
  habitacion_numero: string;
  monto_total: number;
  monto_pagado: number;
  saldo_pendiente: number;
  metodo_pago: string;
  created_at: string;
  tipo_cliente: TipoCliente;
  modalidad_pago?: 'contado' | 'abono' | 'credito';
  requiere_factura?: boolean;
}

export interface ReservaPayload {
  habitacion: number;
  huesped: number;
  fecha_entrada: string;
  fecha_salida: string;
  estado: string;
  metodo_pago: string;
  referencia_pago: string;
  monto_total: number;
  monto_pagado: number;
  tipo_cliente?: TipoCliente; 
  notas: string;
  requiere_factura_seniat?: boolean;
  modalidad_pago?: 'contado' | 'abono' | 'credito';
  requiere_factura?: boolean;
  datos_fiscales?: {
    rif: string;
    razon_social: string;
    direccion: string;
  };
}

export const reservacionesApi = {
  list: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return apiFetch<ReservaListItem[]>(`/reservaciones/${query}`);
  },
  get: (id: number) => apiFetch<ReservaListItem>(`/reservaciones/${id}/`),
  create: (data: ReservaPayload) => apiFetch('/reservaciones/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<ReservaPayload>) => apiFetch(`/reservaciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => apiFetch(`/reservaciones/${id}/`, { method: 'DELETE' }),
  registrarNoShow: (id: number, motivo: string) => apiFetch(`/reservaciones/${id}/no-show/`, { method: 'POST', body: JSON.stringify({ motivo }) }),
  agregarConsumo: (id: number, consumo: any) => apiFetch(`/reservaciones/${id}/consumo/`, { method: 'POST', body: JSON.stringify(consumo) }),
  cambiarHabitacion: (id: number, nuevaHabitacionId: number, motivo: string) => apiFetch(`/reservaciones/${id}/cambiar-habitacion/`, { method: 'POST', body: JSON.stringify({ nueva_habitacion_id: nuevaHabitacionId, motivo }) }),
  registrarPago: (id: number, pago: { monto: number; metodo: string; referencia: string; fecha: string }) => apiFetch(`/pagos/`, { method: 'POST', body: JSON.stringify({ reserva: id, ...pago }) }),
  checkin: (id: number) => apiFetch(`/reservaciones/${id}/checkin/`, { method: 'POST' }),
  checkout: (id: number) => apiFetch(`/reservaciones/${id}/checkout/`, { method: 'POST' }),
  cancelar: (id: number) => apiFetch(`/reservaciones/${id}/cancelar/`, { method: 'POST' }),
};

export const METODOS_PAGO = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'tarjeta', label: 'Tarjeta' },
  { value: 'pago_movil', label: 'Pago Móvil' },
];