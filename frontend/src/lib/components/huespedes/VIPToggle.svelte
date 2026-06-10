<script lang="ts">
    let {
        categoria = $bindable('Estándar'),
    }: {
        categoria?: string;
    } = $props();

    function toggle() {
        categoria = categoria === 'VIP' ? 'Estándar' : 'VIP';
    }
</script>

<button
    type="button"
    onclick={toggle}
    class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border transition-all duration-300 {categoria === 'VIP'
        ? 'bg-hotel-vip/10 border-hotel-vip/30 text-hotel-vip-light'
        : 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary'}"
    aria-pressed={categoria === 'VIP'}
>
    <svg class="w-4 h-4 {categoria === 'VIP' ? 'text-hotel-vip-light' : 'text-hotel-text-tertiary'}" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
    <span class="text-[10px] font-bold uppercase tracking-wider">{categoria}</span>
</button>