<script lang="ts">
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { browser } from '$app/environment';
  import { icons } from '$lib/components/Icons.svelte';
  import { fade } from 'svelte/transition';

  type IconName = keyof typeof icons;

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

  const menuItems = [
    { key: 'dashboard',   label: 'Dashboard',    href: '/dashboard' },
    { key: 'habitaciones', label: 'Habitaciones', href: '/habitaciones' },
    { key: 'huespedes',    label: 'Huéspedes',    href: '/huespedes' },
    { key: 'reservas',     label: 'Reservas',     href: '/reservas' },
    { key: 'inventario',   label: 'Inventario',   href: '/inventario' },
    { key: 'reportes',     label: 'Reportes',     href: '/reportes' },
    { key: 'config',       label: 'Configuración', href: '/configuracion', adminOnly: true },
  ];
</script>

<button
  type="button"
  onclick={() => (mobileOpen = !mobileOpen)}
  class="lg:hidden fixed top-3 left-3 z-100 w-11 h-11 rounded-xl flex items-center justify-center bg-hotel-surface border border-hotel-border text-hotel-gold shadow-2xl"
>
  {@html mobileOpen ? icons.close : icons.menu}
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
    lg:translate-x-0 {collapsed ? 'w-19' : 'w-64'}" 
>
  <div class="flex flex-col h-full w-full overflow-x-hidden">
    
    <div class="h-16 flex items-center shrink-0 border-b border-hotel-border px-5">
      <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 overflow-hidden">
        <img src="/favicon.svg" alt="Logo SalmaSuites" class="w-full h-full object-contain" />
      </div>
      {#if !collapsed}
        <span transition:fade class="ml-3 font-display font-bold italic text-hotel-text-primary">
          SalmaSuitesPMS
        </span>
      {/if}
    </div>

    <nav class="flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden select-none">
      {#each menuItems as item (item.key)}
        {#if !item.adminOnly || ($auth.user?.role === 'admin')}
          <a
            href={item.href}
            onclick={() => (mobileOpen = false)}
            class="flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 group relative
              {$page.url.pathname === item.href 
                ? 'bg-hotel-gold/10 text-hotel-gold border-hotel-gold/20' 
                : 'text-hotel-text-secondary hover:bg-hotel-surface hover:text-hotel-text-primary border-transparent'} border"
          >
            <div class="shrink-0 w-6 h-6 flex items-center justify-center">
              {@html icons[item.key]}
            </div>

            {#if !collapsed}
              <span class="font-medium text-sm truncate whitespace-nowrap overflow-hidden">
                {item.label}
              </span>
            {/if}

            {#if collapsed}
              <div class="absolute left-16 px-3 py-2 rounded-lg text-[10px] font-bold whitespace-nowrap
                          invisible group-hover:visible opacity-0 group-hover:opacity-100 
                          translate-x-2.5 group-hover:translate-x-0 transition-all z-110
                          bg-hotel-surface border border-hotel-border text-hotel-gold shadow-2xl uppercase tracking-widest">
                {item.label}
              </div>
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
        <div class="shrink-0 w-6 h-6 flex items-center justify-center">{@html icons.logout}</div>
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
  >
    <div class="transition-transform duration-300" style="transform: rotate({collapsed ? '180deg' : '0deg'})">
      {@html icons.flecha}
    </div>
  </button>
</aside>