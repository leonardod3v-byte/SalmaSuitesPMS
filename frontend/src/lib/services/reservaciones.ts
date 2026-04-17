import { apiFetch } from './api';

export const TIPOS_CLIENTE = {
  particular:  { label: 'Particular',        color: '#7340A0', bg: 'rgba(115,64,160,0.15)', text: '#A67DD4' },
  militar:     { label: 'Militar / GN',       color: '#2D6A4F', bg: 'rgba(45,106,79,0.15)',  text: '#3D8A66' },
  politico:    { label: 'Político / Gov.',    color: '#9B2226', bg: 'rgba(155,34,38,0.15)',  text: '#C0393E' },
  artista:     { label: 'Artista / Medios',   color: '#1E3A5F', bg: 'rgba(30,58,95,0.15)',   text: '#2E5490' },
  empresarial: { label: 'Empresarial',        color: '#B38E5D', bg: 'rgba(179,142,93,0.15)', text: '#D9C5A3' },
  deportista:  { label: 'Deportista',         color: '#1B5E20', bg: 'rgba(27,94,32,0.15)',   text: '#4CAF50' },
  diplomatico: { label: 'Diplomático',        color: '#4A148C', bg: 'rgba(74,20,140,0.15)',  text: '#9C27B0' },
  medico:      { label: 'Personal Médico',    color: '#006064', bg: 'rgba(0,96,100,0.15)',   text: '#00BCD4' },
  religioso:   { label: 'Religioso',          color: '#E65100', bg: 'rgba(230,81,0,0.15)',   text: '#FF9800' },
  turista:     { label: 'Turista / Agencia',  color: '#37474F', bg: 'rgba(55,71,79,0.15)',   text: '#90A4AE' },
} as const;

export type TipoCliente = keyof typeof TIPOS_CLIENTE;

export interface ReservaListItem {
  id:                 number;
  estado:             string;
  fecha_entrada:      string;
  fecha_salida:       string;
  noches:             number;
  huesped_nombre:     string;
  huesped_documento:  string;
  habitacion_numero:  string;
  monto_total:        string;
  monto_pagado:       string;
  saldo_pendiente:    string;
  metodo_pago:        string;
  tipo_cliente:       TipoCliente;
  created_at:         string;
}

export interface Reserva extends ReservaListItem {
  huesped:              number;
  habitacion:           number;
  hora_check_in:        string | null;
  hora_check_out:       string | null;
  referencia_pago:      string;
  requiere_factura_seniat: boolean;
  datos_factura:        Record<string, string>;
  no_show_motivo:       string;
  no_show_fecha:        string | null;
  notas:                string;
  consumos:             Consumo[];
  huesped_data:         Record<string, unknown>;
  habitacion_data:      Record<string, unknown>;
  creada_por_nombre:    string;
  updated_at:           string;
}

export interface Consumo {
  id:                  number;
  producto:            string;
  cantidad:            number;
  precio_unitario:     string;
  noches_asociadas:    number;
  total:               string;
  nota:                string;
  registrado_por_nombre: string;
  fecha_consumo:       string;
}

export interface ReservaPayload {
  habitacion:             number;
  huesped:                number;
  fecha_entrada:          string;
  fecha_salida:           string;
  estado:                 string;
  metodo_pago:            string;
  referencia_pago:        string;
  monto_total:            number;
  monto_pagado:           number;
  tipo_cliente:           TipoCliente;
  notas:                  string;
  requiere_factura_seniat: boolean;
}

export const reservacionesApi = {
  getAll: (params = '') =>
    apiFetch<ReservaListItem[]>(`/reservaciones/${params}`),

  getById: (id: number) =>
    apiFetch<Reserva>(`/reservaciones/${id}/`),

  create: (data: ReservaPayload) =>
    apiFetch<Reserva>('/reservaciones/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Partial<ReservaPayload>) =>
    apiFetch<Reserva>(`/reservaciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: number) =>
    apiFetch(`/reservaciones/${id}/`, { method: 'DELETE' }),

  registrarNoShow: (id: number, motivo: string) =>
    apiFetch(`/reservaciones/${id}/no-show/`, { method: 'POST', body: JSON.stringify({ motivo }) }),

  agregarConsumo: (id: number, data: Omit<Consumo, 'id' | 'total' | 'registrado_por_nombre' | 'fecha_consumo'>) =>
    apiFetch<Consumo>(`/reservaciones/${id}/consumo/`, { method: 'POST', body: JSON.stringify(data) }),

  cambiarHabitacion: (id: number, nueva_habitacion_id: number, motivo: string) =>
    apiFetch(`/reservaciones/${id}/cambiar-habitacion/`, {
      method: 'POST',
      body: JSON.stringify({ nueva_habitacion_id, motivo }),
    }),

    registrarPago: (id: number, data: { monto: number; metodo: string; referencia: string; fecha: string }) =>
    apiFetch(`/reservaciones/${id}/pagar/`, { 
      method: 'POST', 
      body: JSON.stringify(data) 
    }),
};