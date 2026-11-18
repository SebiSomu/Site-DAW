<script lang="ts">
  let { page, pages, href }: { page: number; pages: number; href: (page: number) => string } = $props()
</script>

{#if pages > 1}
  <nav class="pager" aria-label="Pages">
    {#if page > 1}
      <a href={href(page - 1)} rel="prev">Previous page</a>
    {/if}
    <span>Page {page} of {pages}</span>
    {#if page < pages}
      <a href={href(page + 1)} rel="next">Next page</a>
    {/if}
  </nav>
{/if}

<style>
  .pager {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--space-md) var(--space-lg);
    font-weight: 700;
  }
</style>
