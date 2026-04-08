import { icons } from '$lib/components/Icons.svelte';

declare global {
  namespace App {
    interface Locals {
      user: {
        id: string;
        role: 'admin' | 'recepcionistas';
        name: string;
      } | null;
    }
    interface PageData {
      user?: {
        id: string;
        role: 'admin' | 'recepcionistas';
        name: string;
      } | null;
    }
  }

  type IconKey = keyof typeof icons;
}

export {};