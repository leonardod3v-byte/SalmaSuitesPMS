<script lang="ts">
    let {
        estado,
    }: {
        estado: string;
    } = $props();

    const clases: Record<string, string> = {
        'Disponible': 'bg-hotel-success/80 border-hotel-success text-white',
        'Ocupada': 'bg-hotel-gold/80 border-hotel-gold text-hotel-bg',
        'Limpieza': 'bg-hotel-info/80 border-hotel-info-light text-white',
        'Mantenimiento': 'bg-hotel-error/80 border-hotel-error text-white',
        'Obra': 'bg-hotel-error/80 border-hotel-error text-white',
    };

    const dots: Record<string, string> = {
        'Disponible': 'bg-white',
        'Ocupada': 'bg-hotel-bg',
        'Limpieza': 'bg-white',
        'Mantenimiento': 'bg-white',
        'Obra': 'bg-white',
    };
</script>

<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border shadow-lg backdrop-blur-sm {clases[estado] || 'bg-hotel-surface/80 border-hotel-border text-white'}">
    <span class="w-1.5 h-1.5 rounded-full {dots[estado] || 'bg-white'}"></span>
    {estado}
</span>
