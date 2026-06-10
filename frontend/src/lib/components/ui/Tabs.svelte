<script lang="ts">
    interface Tab {
        key: string;
        label: string;
        count?: number;
    }

    let {
        tabs,
        active,
        onchange
    }: {
        tabs: Tab[];
        active: string;
        onchange?: (key: string) => void;
    } = $props();
</script>

<div class="flex p-1 bg-hotel-bg rounded-xl border border-hotel-border">
    {#each tabs as tab}
        <button
            onclick={() => onchange?.(tab.key)}
            class="px-4 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {active === tab.key ? 'bg-hotel-gold text-hotel-bg shadow-hotel-sm' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}"
        >
            {tab.label}
            {#if tab.count !== undefined}
                <span class="ml-1.5 px-1.5 py-0.5 rounded-full text-[9px] {active === tab.key ? 'bg-hotel-bg/20 text-hotel-bg' : 'bg-hotel-surface text-hotel-text-tertiary'}">
                    {tab.count}
                </span>
            {/if}
        </button>
    {/each}
</div>