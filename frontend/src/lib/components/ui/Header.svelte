<script lang="ts">
  import { auth } from '$stores/auth.svelte';
  import { page } from '$app/stores';
  import Icon from '$components/ui/Icons.svelte';
  import { fly } from 'svelte/transition';

  let activeDropdown = $state<string | null>(null);

  const toggleDropdown = (name: string) => {
    activeDropdown = activeDropdown === name ? null : name;
  };

  const closeDropdowns = () => activeDropdown = null;

  const logout = () => {
    closeDropdowns();
    auth.logout();
  };

  let breadcrumbs = $derived(
    $page.url.pathname.split('/').filter(Boolean).map((seg, i, arr) => ({
      label: seg.charAt(0).toUpperCase() + seg.slice(1),
      href: '/' + arr.slice(0, i + 1).join('/'),
      isLast: i === arr.length - 1,
    }))
  );

  let userName = $derived(auth.user?.username ?? 'Usuario');
  let userInitial = $derived(userName.charAt(0).toUpperCase());
  let userRole = $derived(auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista');
</script>

<svelte:window onclick={(e) => {
  if (!(e.target as HTMLElement).closest('.dropdown-container')) closeDropdowns();
}} />

<header class="h-16 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-6 bg-hotel-bg/85 backdrop-blur-md border-b border-hotel-border min-w-0">

  <!-- Breadcrumbs desktop -->
  <nav class="hidden lg:flex items-center gap-1.5 text-sm min-w-0 overflow-hidden">
    <a href="/dashboard" data-sveltekit-prefetch class="text-hotel-text-tertiary hover:text-hotel-gold transition-colors shrink-0 p-1 rounded-md hover:bg-hotel-surface">
      <Icon name="hotel" class="w-4 h-4" />
    </a>
    {#each breadcrumbs as crumb, i}
      <Icon name="chevron-right" class="w-3 h-3 text-hotel-text-tertiary/50 shrink-0" />
      <a href={crumb.href} data-sveltekit-prefetch
        class="transition-colors truncate px-1 py-0.5 rounded-md {crumb.isLast
          ? 'text-hotel-text-primary font-bold'
          : 'text-hotel-text-secondary hover:text-hotel-text-primary hover:bg-hotel-surface'}">
        {crumb.label}
      </a>
    {/each}
  </nav>

  <!-- Breadcrumb móvil -->
  <span class="lg:hidden text-sm font-bold text-hotel-text-primary truncate ml-12 mr-4">
    {breadcrumbs[breadcrumbs.length - 1]?.label ?? 'Dashboard'}
  </span>

  <div class="flex items-center gap-2 sm:gap-3 dropdown-container shrink-0">

    <!-- Separador -->
    <div class="hidden sm:block w-px h-6 bg-hotel-border/50"></div>

    <!-- Perfil -->
    <div class="relative">
      <button onclick={() => toggleDropdown('profile')}
              class="flex items-center gap-3 p-1 rounded-xl hover:bg-hotel-surface transition-all group"
              aria-label="Perfil de usuario">
        <div class="relative">
          <div class="w-9 h-9 rounded-full bg-linear-to-br from-hotel-gold to-hotel-gold-dark text-hotel-bg flex items-center justify-center font-bold text-sm ring-2 ring-transparent group-hover:ring-hotel-gold/30 transition-all">
            {userInitial}
          </div>
          <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-hotel-success border-2 border-hotel-bg rounded-full"></span>
        </div>
        <div class="hidden sm:block text-left leading-tight">
          <p class="text-sm font-bold text-hotel-text-primary">{userName}</p>
          <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-wider">{userRole}</p>
        </div>
        <Icon name="chevron" class="hidden sm:block w-3 h-3 text-hotel-text-tertiary group-hover:text-hotel-gold transition-colors" />
      </button>

      {#if activeDropdown === 'profile'}
        <div transition:fly={{ y: 10, duration: 200 }}
            class="absolute right-0 mt-2 w-64 bg-hotel-surface border border-hotel-border rounded-xl shadow-hotel-lg overflow-hidden z-50">
          <!-- Header del dropdown -->
          <div class="p-4 border-b border-hotel-border bg-linear-to-br from-hotel-gold/5 to-transparent">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-linear-to-br from-hotel-gold to-hotel-gold-dark text-hotel-bg flex items-center justify-center font-bold text-sm">
                {userInitial}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-bold text-hotel-text-primary truncate">{userName}</p>
                <p class="text-[10px] text-hotel-text-tertiary truncate">{auth.user?.email}</p>
              </div>
            </div>
          </div>
          <!-- Opciones -->
          <div class="p-2 space-y-0.5">
            <a href="/perfil" class="flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-text-secondary hover:bg-hotel-surface-hover hover:text-hotel-text-primary transition-colors text-sm">
              <Icon name="user" class="w-4 h-4" /> Mi perfil
            </a>
            <a href="/configuracion" class="flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-text-secondary hover:bg-hotel-surface-hover hover:text-hotel-text-primary transition-colors text-sm">
              <Icon name="config" class="w-4 h-4" /> Configuración
            </a>
            <div class="my-1 border-t border-hotel-border/50"></div>
            <button onclick={logout} class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-error hover:bg-hotel-error/10 transition-colors text-sm font-medium">
              <Icon name="logout" class="w-4 h-4" /> Cerrar sesión
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</header>
