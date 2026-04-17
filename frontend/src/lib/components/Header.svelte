<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { page } from '$app/stores';
  import { icons } from '$lib/components/Icons.svelte';
  import { fade, fly } from 'svelte/transition';

  // ── Estado ──────────────────────────────────────────────────────────────────
  let activeDropdown = $state<string | null>(null);
  let currentLang = $state('ES');

  const notifications = [
    { id: 1, text: 'Nueva reserva: Suite 301', time: '5 min', unread: true },
    { id: 2, text: 'Check-out pendiente: H-205', time: '15 min', unread: true },
    { id: 3, text: 'Solicitud mantenimiento H-208', time: '1 h', unread: false },
  ];

  // ── Lógica ──────────────────────────────────────────────────────────────────
  const toggleDropdown = (name: string) => {
    activeDropdown = activeDropdown === name ? null : name;
  };

  const closeDropdowns = () => activeDropdown = null;

  const selectLang = (code: string) => {
    currentLang = code;
    closeDropdowns();
  };

  const logout = () => {
    closeDropdowns();
    auth.logout();
  };

  // ── Derivados ───────────────────────────────────────────────────────────────
  let breadcrumbs = $derived(
    $page.url.pathname.split('/').filter(Boolean).map((seg, i, arr) => ({
      label: seg.charAt(0).toUpperCase() + seg.slice(1),
      href: '/' + arr.slice(0, i + 1).join('/')
    }))
  );

  let unreadCount = $derived(notifications.filter(n => n.unread).length);
  let userName = $derived($auth.user?.username ?? 'Usuario');
  let userInitial = $derived(userName.charAt(0).toUpperCase());
  let userRole = $derived($auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista');
</script>

<svelte:window onclick={(e) => {
  if (!(e.target as HTMLElement).closest('.dropdown-container')) closeDropdowns();
}} />

<header class="h-16 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-6 bg-hotel-bg/85 backdrop-blur-md border-b border-hotel-border">
  
  <nav class="hidden sm:flex items-center gap-2 text-sm">
    <a href="/dashboard" class="text-hotel-text-secondary hover:text-hotel-gold transition-colors shrink-0">
      {@html icons.hotel}
    </a>
    {#each breadcrumbs as crumb, i}
      <span class="text-hotel-text-tertiary">/</span>
      <a href={crumb.href} 
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
      <button onclick={() => toggleDropdown('notifications')} 
              class="p-2 rounded-xl text-hotel-text-secondary hover:bg-hotel-surface hover:text-hotel-text-primary transition-all relative">
        {@html icons.bell}
        {#if unreadCount > 0}
          <span class="absolute top-2 right-2 w-2 h-2 bg-hotel-error rounded-full animate-pulse"></span>
        {/if}
      </button>

      {#if activeDropdown === 'notifications'}
        <div transition:fly={{ y: 10, duration: 200 }} 
             class="absolute right-0 mt-2 w-80 bg-hotel-surface border border-hotel-border rounded-xl shadow-hotel-lg overflow-hidden z-50">
          <div class="p-4 border-b border-hotel-border flex justify-between items-center">
            <h3 class="font-medium text-hotel-text-primary">Notificaciones</h3>
            <span class="text-[10px] bg-hotel-gold/15 text-hotel-gold px-2 py-0.5 rounded-full uppercase font-bold">
              {unreadCount} nuevas
            </span>
          </div>
          <div class="max-h-64 overflow-y-auto">
            {#each notifications as notif}
              <div class="p-4 border-b border-hotel-border hover:bg-hotel-surface-hover transition-colors cursor-pointer {notif.unread ? 'bg-hotel-gold/5' : ''}">
                <p class="text-sm text-hotel-text-primary">{notif.text}</p>
                <p class="text-xs text-hotel-text-tertiary mt-1">{notif.time}</p>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <div class="relative">
      <button onclick={() => toggleDropdown('profile')} 
              class="flex items-center gap-3 p-1.5 rounded-xl hover:bg-hotel-surface transition-all">
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
            <p class="text-xs text-hotel-text-tertiary truncate">{$auth.user?.email}</p>
          </div>
          <div class="p-2 space-y-1">
            <a href="/perfil" class="flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-text-secondary hover:bg-hotel-surface-hover hover:text-hotel-text-primary transition-colors text-sm">
              {@html icons.user} Mi perfil
            </a>
            <button onclick={logout} class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-hotel-error hover:bg-hotel-error/10 transition-colors text-sm">
              {@html icons.logout} Cerrar sesión
            </button>
          </div>
        </div>
      {/if}
    </div>

  </div>
</header>