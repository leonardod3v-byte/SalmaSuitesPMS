<script lang="ts">
  import { fade } from 'svelte/transition';
  import Skeleton from './Skeleton.svelte';

  let { 
    type = 'full',
    message = 'Sincronizando...',
    skeletonCount = 4
  }: { 
    type?: 'full' | 'dashboard';
    message?: string;
    skeletonCount?: number;
  } = $props();
</script>

{#if type === 'full'}
  <div transition:fade={{ duration: 200 }} class="fixed inset-0 flex flex-col items-center justify-center bg-hotel-bg z-50">
    <div class="relative w-20 h-20 flex items-center justify-center">
      <div class="absolute inset-0 rounded-full border-4 border-hotel-gold/10"></div>
      <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-hotel-gold animate-spin duration-700"></div>
      <div class="text-hotel-gold opacity-80 animate-pulse">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
        </svg>
      </div>
    </div>
    <p class="mt-6 text-sm tracking-widest font-bold text-hotel-text-secondary uppercase">{message}</p>
  </div>
{:else if type === 'dashboard'}
  <div class="space-y-8 p-4 animate-pulse">
    <Skeleton height="h-32" rounded="rounded-2xl" />
    
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {#each Array(skeletonCount) as _}
        <Skeleton height="h-24" rounded="rounded-xl" />
      {/each}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <Skeleton height="h-80" rounded="rounded-2xl" />
      </div>
      <div>
        <Skeleton height="h-80" rounded="rounded-2xl" />
      </div>
    </div>
  </div>
{/if}