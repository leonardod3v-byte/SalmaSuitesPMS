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

  type MenuKey = 'dashboard' | 'habitaciones' | 'huespedes' | 'empresas' | 'reservaciones' | 'inventario' | 'reportes' | 'user' | 'config';
  const menuPrincipal: { key: MenuKey; label: string; href: string }[] = [
    { key: 'dashboard',   label: 'Dashboard',    href: '/dashboard' },
    { key: 'habitaciones', label: 'Habitaciones', href: '/habitaciones' },
    { key: 'huespedes',    label: 'Huéspedes',    href: '/huespedes' },
    { key: 'empresas',     label: 'Empresas',     href: '/empresas' },
    { key: 'reservaciones', label: 'Reservas', href: '/reservaciones' },
    { key: 'inventario',   label: 'Inventario',   href: '/inventario' },
    { key: 'reportes',     label: 'Reportes',     href: '/reportes' },
  ];
  const menuAdmin: { key: MenuKey; label: string; href: string }[] = [
    { key: 'user',     label: 'Usuarios',     href: '/usuarios' },
    { key: 'config',       label: 'Configuración', href: '/configuracion' },
  ];

  function isActive(href: string): boolean {
    return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
  }
</script>

<!-- Botón móvil -->
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

    <!-- Logo -->
    <div class="h-16 flex items-center shrink-0 border-b border-hotel-border px-5">
      <a href="/dashboard" data-sveltekit-prefetch class="flex items-center gap-3 w-full group">
        <div class="w-10 h-10 flex items-center justify-center shrink-0 overflow-hidden transition-colors">
          <img src="/favicon.svg" alt="Logo SalmaSuites" class="w-full h-full object-contain" />
        </div>
        {#if !collapsed}
          <span transition:fade class="ml-3 font-display font-bold italic text-hotel-text-primary">
            SalmaSuites<span class="text-hotel-gold">PMS</span>
          </span>
        {/if}
      </a>
    </div>

    <!-- Navegación principal -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden select-none custom-scrollbar">
      {#each menuPrincipal as item (item.key)}
        {@const active = isActive(item.href)}
        <div class="relative group/item">
          <a
            href={item.href}
            data-sveltekit-prefetch
            onclick={() => (mobileOpen = false)}
            class="flex items-center gap-4 px-3 py-2.5 rounded-xl transition-all duration-200 relative
              {active
                ? 'bg-hotel-gold/10 text-hotel-gold'
                : 'text-hotel-text-secondary hover:bg-hotel-surface hover:text-hotel-text-primary'}"
          >
            <!-- Indicador activo lateral -->
            {#if active}
              <span class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-hotel-gold"></span>
            {/if}

            <div class="shrink-0 w-6 h-6 flex items-center justify-center">
              <Icon name={item.key} class="w-5 h-5" />
            </div>
            {#if !collapsed}
              <span class="font-medium text-sm truncate whitespace-nowrap overflow-hidden">
                {item.label}
              </span>
            {/if}
          </a>

          <!-- Tooltip cuando está colapsado -->
          {#if collapsed}
            <div class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 rounded-lg bg-hotel-surface border border-hotel-border text-hotel-text-primary text-xs font-bold whitespace-nowrap opacity-0 group-hover/item:opacity-100 pointer-events-none transition-opacity z-100 shadow-xl">
              {item.label}
            </div>
          {/if}
        </div>
      {/each}

      <!-- Divisor y menú admin -->
      {#if auth.user?.role === 'admin'}
        <div class="my-3 border-t border-hotel-border/50"></div>
        {#each menuAdmin as item (item.key)}
          {@const active = isActive(item.href)}
          <div class="relative group/item">
            <a
              href={item.href}
              data-sveltekit-prefetch
              onclick={() => (mobileOpen = false)}
              class="flex items-center gap-4 px-3 py-2.5 rounded-xl transition-all duration-200 relative
                {active
                  ? 'bg-hotel-gold/10 text-hotel-gold'
                  : 'text-hotel-text-secondary hover:bg-hotel-surface hover:text-hotel-text-primary'}"
            >
              {#if active}
                <span class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-hotel-gold"></span>
              {/if}
              <div class="shrink-0 w-6 h-6 flex items-center justify-center">
                <Icon name={item.key} class="w-5 h-5" />
              </div>
              {#if !collapsed}
                <span class="font-medium text-sm truncate whitespace-nowrap overflow-hidden">
                  {item.label}
                </span>
              {/if}
            </a>

            {#if collapsed}
              <div class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 rounded-lg bg-hotel-surface border border-hotel-border text-hotel-text-primary text-xs font-bold whitespace-nowrap opacity-0 group-hover/item:opacity-100 pointer-events-none transition-opacity z-100 shadow-xl">
                {item.label}
              </div>
            {/if}
          </div>
        {/each}
      {/if}
    </nav>

    <!-- Logout -->
    <div class="p-3 border-t border-hotel-border shrink-0 bg-hotel-bg">
      <button
        type="button"
        onclick={logout}
        class="flex items-center gap-4 px-3 py-2.5 rounded-xl transition-all w-full text-hotel-error hover:bg-hotel-error/10"
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

  <!-- Botón colapsar -->
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
