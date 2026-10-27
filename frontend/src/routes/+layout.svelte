<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page as pageStore } from '$app/stores';
  import { goto } from '$app/navigation';
  import Sidebar from '$components/ui/Sidebar.svelte';
  import Header from '$components/ui/Header.svelte';
  import Toast from '$components/ui/Toast.svelte';
  import { auth, type User } from '$stores/auth.svelte';
  import { apiFetch } from '$lib/services/api';

  let { children } = $props();

  let isPublicPage = $derived(
    $pageStore.url.pathname === '/login' ||
    $pageStore.url.pathname === '/recuperar' ||
    $pageStore.url.pathname === '/'
  );

  onMount(async () => {
    if (isPublicPage) {
      auth.init(null);
      return;
    }

    const tokenLocal = localStorage.getItem('auth_token');
    if (!tokenLocal) {
      auth.init(null);
      goto('/login', { replaceState: true });
      return;
    }

    if (auth.user) {
      return;
    }

    try {
      const user = await apiFetch<User>('/auth/profile/');
      auth.init(user);
    } catch (err: any) {
      if (err.message?.includes('Sesión expirada') || err.message?.includes('401')) {
        localStorage.removeItem('auth_token');
        auth.init(null);
        goto('/login', { replaceState: true });
      }
    }
  });
</script>

<Toast />

{#if isPublicPage}
  <main class="min-h-screen bg-hotel-bg">
    {@render children()}
  </main>
{:else}
  <div class="flex min-h-screen bg-hotel-bg text-hotel-text-primary">
    <div class="z-50"><Sidebar /></div>
    <div class="flex-1 flex flex-col min-w-0 relative">
      <div class="lg:ml-18 transition-all duration-300"><Header /></div>
      <main class="flex-1">
        <div class="p-3 lg:p-6 lg:ml-18 mt-12 lg:mt-2 transition-all duration-300">
          <div class="max-w-350 mx-auto">{@render children()}</div>
        </div>
      </main>
    </div>
  </div>
{/if}
