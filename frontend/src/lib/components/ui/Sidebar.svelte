<script lang="ts">
  import { page } from '$app/stores';
  import { auth } from '$stores/auth.svelte';
  import { browser } from '$app/environment';
  import Icon from '$components/ui/Icons.svelte';
  import { fade } from 'svelte/transition';

  let collapsed = $state(false);
  let mobileOpen = $state(false);

  if (browser) {
    collapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  }

  function toggle() {
    collapsed = !collapsed;
    localStorage.setItem('sidebar-collapsed', String(collapsed));
  }

  const logout = () => auth.logout();

  type MenuKey = 'dashboard' | 'habitaciones' | 'huespedes' | 'reservaciones' | 'inventario' | 'reportes' | 'user' | 'config';
  const menuItems: { key: MenuKey; label: string; href: string; adminOnly?: boolean }[] = [
    { key: 'dashboard',   label: 'Dashboard',    href: '/dashboard' },
    { key: 'habitaciones', label: 'Habitaciones', href: '/habitaciones' },
    { key: 'huespedes',    label: 'Huéspedes',    href: '/huespedes' },
    { key: 'reservaciones', label: 'Reservas', href: '/reservaciones' },
    { key: 'inventario',   label: 'Inventario',   href: '/inventario' },
    { key: 'reportes',     label: 'Reportes',     href: '/reportes' },
    { key: 'user',     label: 'Usuarios',     href: '/usuarios', adminOnly: true },
    { key: 'config',       label: 'Configuración', href: '/configuracion', adminOnly: true },
  ];
</script>

<button
  type="button"
  onclick={() => (mobileOpen = !mobileOpen)}
  class="lg:hidden fixed top-3 left-3 z-100 w-11 h-11 rounded-xl flex items-center justify-center bg-hotel-surface border border-hotel-border text-hotel-gold shadow-2xl"
  aria-label="Abrir menú"
>
  <Icon name={mobileOpen ? 'close' : 'menu'} class="w-5 h-5" />
</button>

{#if mobileOpen}
  <div
    transition:fade={{ duration: 200 }}
    onclick={() => (mobileOpen = false)}
    class="fixed inset-0 z-80 lg:hidden bg-black/70 backdrop-blur-md"
    role="presentation"
  ></div>
{/if}

<aside
  class="fixed left-0 top-0 h-full z-90 transition-all duration-300 ease-in-out bg-hotel-bg border-r border-hotel-border flex flex-col
    {mobileOpen ? 'translate-x-0' : '-translate-x-full'} 
    lg:translate-x-0 {collapsed ? 'w-20' : 'w-64'}" 
>
  <div class="flex flex-col h-full w-full overflow-x-hidden">
    
    <div class="h-16 flex items-center shrink-0 border-b border-hotel-border px-5">
      <a href="/dashboard" data-sveltekit-prefetch class="flex items-center gap-3 w-full">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 overflow-hidden">
          <img src="/favicon.svg" alt="Logo SalmaSuites" class="w-full h-full object-contain" />
        </div>
        {#if !collapsed}
          <span transition:fade class="ml-3 font-display font-bold italic text-hotel-text-primary">
            SalmaSuitesPMS
          </span>
        {/if}
      </a>
    </div>

    <nav class="flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden select-none custom-scrollbar">
      {#each menuItems as item (item.key)}
        {#if !item.adminOnly || (auth.user?.role === 'admin')}
          <a
            href={item.href}
            data-sveltekit-prefetch
            onclick={() => (mobileOpen = false)}
            class="flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 group relative
              {$page.url.pathname === item.href 
                ? 'bg-hotel-gold/10 text-hotel-gold border-hotel-gold/20' 
                : 'text-hotel-text-secondary hover:bg-hotel-surface hover:text-hotel-text-primary border-transparent'} border"
          >
            <div class="shrink-0 w-6 h-6 flex items-center justify-center">
              <Icon name={item.key} class="w-5 h-5" />
            </div>
            {#if !collapsed}
              <span class="font-medium text-sm truncate whitespace-nowrap overflow-hidden">
                {item.label}
              </span>
            {/if}
          </a>
        {/if}
      {/each}
    </nav>

    <div class="p-3 border-t border-hotel-border shrink-0 bg-hotel-bg">
      <button
        type="button"
        onclick={logout}
        class="flex items-center gap-4 px-3 py-3 rounded-xl transition-all w-full text-hotel-error hover:bg-hotel-error/10"
      >
        <div class="shrink-0 w-6 h-6 flex items-center justify-center">
          <Icon name="logout" class="w-5 h-5" />
        </div>
        {#if !collapsed}
          <span class="font-bold text-xs uppercase tracking-wider">Cerrar Sesión</span>
        {/if}
      </button>
    </div>
  </div>

  <button
    type="button"
    onclick={toggle}
    class="hidden lg:flex absolute -right-3 top-20 w-6 h-6 rounded-full
          items-center justify-center shadow-xl hover:scale-110 transition-transform z-100 
          bg-hotel-gold text-hotel-bg border-2 border-hotel-bg"
    aria-label={collapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
  >
    <div class="transition-transform duration-300" style="transform: rotate({collapsed ? '180deg' : '0deg'})">
      <Icon name="flecha" class="w-3 h-3" />
    </div>
  </button>
</aside>