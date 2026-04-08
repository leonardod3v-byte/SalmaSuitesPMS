<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    goto('/login', { replaceState: true });
  });
</script>

<svelte:head>
  <title>Cargando... | SalmaSuitesPMS</title>
</svelte:head>

<div class="min-h-screen bg-hotel-bg"></div>