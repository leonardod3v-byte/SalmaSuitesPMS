<script lang="ts">
  let {
    width = 'w-full',
    height = 'h-4',
    rounded = 'rounded-lg'
  }: {
    width?: string,
    height?: string,
    rounded?: string
  } = $props();
</script>

<div class="{width} {height} {rounded} bg-hotel-surface-hover relative overflow-hidden border border-hotel-border/50">
  <div class="absolute inset-0 -translate-x-full animate-shimmer
    bg-linear-to-r from-transparent via-hotel-gold/5 to-transparent">
  </div>
</div>

<style>
  @keyframes shimmer {
    100% { transform: translateX(100%); }
  }
  .animate-shimmer {
    animation: shimmer 2s infinite;
  }
</style>
