<script>
  let { children } = $props();
</script>

<div class="relative rounded-2xl p-8 overflow-hidden"
     style="background: var(--color-hotel-surface); border: 1px solid var(--color-hotel-border); box-shadow: var(--shadow-hotel-md);">

  <div class="absolute inset-0 pointer-events-none rounded-2xl"
       style="background: linear-gradient(135deg, rgba(179,142,93,0.05) 0%, transparent 50%);"></div>

  <div class="absolute -top-16 -right-16 w-40 h-40 rounded-full blur-3xl pointer-events-none"
       style="background: radial-gradient(circle, rgba(179,142,93,0.08) 0%, transparent 70%);"></div>

  <div class="relative">
    {@render children?.()}
  </div>
</div>