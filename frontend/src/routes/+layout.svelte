<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import Sidebar from '$components/ui/Sidebar.svelte';
  import Header from '$components/ui/Header.svelte';
  import Toast from '$components/ui/Toast.svelte';
  import { auth } from '$stores/auth.svelte';

  let { children, data } = $props();

  $effect(() => {
    auth.init(data.user);
  });

  let isPublicPage = $derived(
    $page.url.pathname === '/login' ||
    $page.url.pathname === '/recuperar' ||
    $page.url.pathname === '/'
  );
</script>

<Toast />

{#if isPublicPage}
  <main class="min-h-screen bg-hotel-bg">
    {@render children()}
  </main>
{:else}
  <div class="flex min-h-screen bg-hotel-bg text-hotel-text-primary">
    <div class="z-50">
      <Sidebar />
    </div>
    <div class="flex-1 flex flex-col min-w-0 relative">
      <div class="lg:ml-18 transition-all duration-300">
        <Header />
      </div>
      <main class="flex-1">
        <div class="p-3 lg:p-6 lg:ml-18 mt-12 lg:mt-2 transition-all duration-300">
          <div class="max-w-350 mx-auto">
            {@render children()}
          </div>
        </div>
      </main>
    </div>
  </div>
{/if}