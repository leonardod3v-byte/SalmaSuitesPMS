import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
  duration: number;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  return {
    subscribe,
    send: (message: string, type: ToastType = 'info', duration = 4000) => {
      const id = Math.floor(Math.random() * 10000);
      update((list) => [...list, { id, message, type, duration }]);
      
      setTimeout(() => {
        update((list) => list.filter((t) => t.id !== id));
      }, duration);
    },
    // Método manual para cerrar
    dismiss: (id: number) => {
      update((list) => list.filter((t) => t.id !== id));
    }
  };
}

export const toast = createToastStore();