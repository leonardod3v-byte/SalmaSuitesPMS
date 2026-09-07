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
      href: '/' + arr.slice(0, i + 1).join('/')
    }))
  );

  let userName = $derived(auth.user?.username ?? 'Usuario');
  let userInitial = $derived(userName.charAt(0).toUpperCase());
  let userRole = $derived(auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista');
</script>

<svelte:window onclick={(e) => {
  if (!(e.target as HTMLElement).closest('.dropdown-container')) closeDropdowns();
}} />

<header class="h-16 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-6 bg-hotel-bg/85 backdrop-blur-md border-b border-hotel-border">

  <nav class="hidden sm:flex items-center gap-2 text-sm">
    <a href="/dashboard" data-sveltekit-prefetch class="text-hotel-text-secondary hover:text-hotel-gold transition-colors shrink-0">
      <Icon name="hotel" class="w-5 h-5" />
    </a>
    {#each breadcrumbs as crumb, i}
      <span class="text-hotel-text-tertiary">/</span>
      <a href={crumb.href} data-sveltekit-prefetch
        class="transition-colors {i === breadcrumbs.length - 1 ? 'text-hotel-text-primary font-medium' : 'text-hotel-text-secondary'}">
        {crumb.label}
      </a>
    {/each}
  </nav>

  <span class="sm:hidden text-sm font-medium text-hotel-text-primary truncate">
    {breadcrumbs[breadcrumbs.length - 1]?.label ?? 'Dashboard'}
  </span>

  <div class="flex items-center gap-2 sm:gap-4 dropdown-container">
    
    <div class="relative">
      <button onclick={() => toggleDropdown('profile')} 
              class="flex items-center gap-3 p-1.5 rounded-xl hover:bg-hotel-surface transition-all"
              aria-label="Perfil de usuario">
        <div class="relative">
          <div class="w-8 h-8 rounded-full bg-linear-to-br from-hotel-gold to-hotel-gold-dark text-hotel-bg flex items-center justify-center font-bold text-sm">
            {userInitial}
          </div>
          <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-hotel-success border-2 border-hotel-bg rounded-full"></span>
        </div>
        <div class="hidden md:block text-left leading-tight">
          <p class="text-sm font-medium text-hotel-text-primary">{userName}</p>
          <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-wider">{userRole}</p>
        </div>
      </button>

      {#if activeDropdown === 'profile'}
        <div transition:fly={{ y: 10, duration: 200 }} 
            class="absolute right-0 mt-2 w-56 bg-hotel-surface border border-hotel-border rounded-xl shadow-hotel-lg overflow-hidden">
          <div class="p-4 border-b border-hotel-border bg-hotel-gold/5">
            <p class="text-sm font-bold text-hotel-text-primary">{userName}</p>
            <p class="text-xs text-hotel-text-tertiary truncate">{auth.user?.email}</p>
          </div>
          <div class="p-2 space-y-1">
            <a href="/perfil" class="flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-text-secondary hover:bg-hotel-surface-hover hover:text-hotel-text-primary transition-colors text-sm">
              <Icon name="user" class="w-4 h-4" /> Mi perfil
            </a>
            <button onclick={logout} class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-error hover:bg-hotel-error/10 transition-colors text-sm">
              <Icon name="logout" class="w-4 h-4" /> Cerrar sesión
            </button>
          </div>
        </div>
      {/if}
    </div>

  </div>
</header>