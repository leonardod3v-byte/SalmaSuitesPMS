<script lang="ts">
    let {
        estado,
    }: {
        estado: 'Normal' | 'Bajo' | 'Agotado' | string;
    } = $props();

    const clases: Record<string, string> = {
        'Normal': 'bg-hotel-success/10 border-hotel-success/30 text-hotel-success-light',
        'Bajo': 'bg-hotel-gold/10 border-hotel-gold/30 text-hotel-gold-light',
        'Agotado': 'bg-hotel-error/10 border-hotel-error/30 text-hotel-error-light',
    };

    const dots: Record<string, string> = {
        'Normal': 'bg-hotel-success',
        'Bajo': 'bg-hotel-gold',
        'Agotado': 'bg-hotel-error',
    };
</script>

<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border {clases[estado] || 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary'}">
    <span class="w-1.5 h-1.5 rounded-full {dots[estado] || 'bg-hotel-text-tertiary'}"></span>
    {estado}
</span>