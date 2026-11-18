<script lang="ts">
  import { hrefWithQuery, positiveInt } from '../../lib/admin'
  import type { LogPage } from '../../lib/api/admin-types'
  import { api, errorMessage } from '../../lib/api/client'
  import AdminGate from '../../lib/components/AdminGate.svelte'
  import Pager from '../../lib/components/Pager.svelte'
  import Seo from '../../lib/components/Seo.svelte'
  import { formatDateTime } from '../../lib/format'
  import { router } from '../../lib/router/router.svelte'
  import { auth } from '../../lib/stores/auth.svelte'

  const LEVELS = ['INFO', 'WARNING', 'ERROR']
  const DATE = /^\d{4}-\d{2}-\d{2}$/

  let result = $state<LogPage | null>(null)
  let error = $state('')

  const isAdmin = $derived(auth.user?.role === 'admin')
  const params = $derived(router.url.searchParams)
  const filters = $derived({
    action: /^[a-z_]{1,60}$/.test(params.get('action') ?? '') ? (params.get('action') as string) : '',
    user_id: positiveInt(params.get('user_id'))?.toString() ?? '',
    level: LEVELS.includes(params.get('level') ?? '') ? (params.get('level') as string) : '',
    date_from: DATE.test(params.get('date_from') ?? '') ? (params.get('date_from') as string) : '',
    date_to: DATE.test(params.get('date_to') ?? '') ? (params.get('date_to') as string) : '',
  })
  const page = $derived(positiveInt(params.get('page')) ?? 1)

  let action = $state('')
  let userId = $state('')
  let level = $state('')
  let dateFrom = $state('')
  let dateTo = $state('')

  $effect(() => {
    action = filters.action
    userId = filters.user_id
    level = filters.level
    dateFrom = filters.date_from
    dateTo = filters.date_to
  })

  $effect(() => {
    if (!isAdmin) return
    const query = { ...filters, page }
    error = ''
    api
      .get<LogPage>('/admin/logs', query)
      .then((body) => (result = body))
      .catch((caught: unknown) => (error = errorMessage(caught)))
  })

  function hrefFor(number: number): string {
    return hrefWithQuery('/admin/activity-log', { ...filters, page: number })
  }

  function apply(event: SubmitEvent): void {
    event.preventDefault()
    router.navigate(
      hrefWithQuery('/admin/activity-log', { action, user_id: userId, level, date_from: dateFrom, date_to: dateTo }),
    )
  }
</script>

<Seo title="Activity log" description="What happened in the shop and who did it." noindex />

<AdminGate>
  <section class="page-stack">
    <h1 class="page-title">Activity log</h1>
    <form class="filters" onsubmit={apply}>
      <label class="field">
        Action
        <select bind:value={action}>
          <option value="">Any action</option>
          {#each result?.actions ?? [] as name (name)}
            <option value={name}>{name}</option>
          {/each}
        </select>
      </label>
      <label class="field">
        User id
        <input type="number" min="1" inputmode="numeric" bind:value={userId} />
      </label>
      <label class="field">
        Level
        <select bind:value={level}>
          <option value="">Any level</option>
          {#each LEVELS as name (name)}
            <option value={name}>{name}</option>
          {/each}
        </select>
      </label>
      <label class="field">
        From
        <input type="date" bind:value={dateFrom} />
      </label>
      <label class="field">
        To
        <input type="date" bind:value={dateTo} />
      </label>
      <p class="filter-actions">
        <button class="button" type="submit">Filter</button>
        <a href="/admin/activity-log">Clear</a>
      </p>
    </form>
    {#if error}
      <p class="status status-error" role="alert">{error}</p>
    {:else if !result}
      <p class="status" aria-live="polite">Reading the log…</p>
    {:else}
      <p class="field-hint">{result.total} {result.total === 1 ? 'entry' : 'entries'}, newest first.</p>
      <div class="paper table-scroll">
        <table class="data-table log">
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Level</th>
              <th scope="col">User</th>
              <th scope="col">IP</th>
              <th scope="col">Action</th>
              <th scope="col">Details</th>
            </tr>
          </thead>
          <tbody>
            {#each result.entries as entry, index (`${entry.timestamp}-${index}`)}
              <tr data-level={entry.level}>
                <td><time datetime={entry.timestamp}>{formatDateTime(entry.timestamp)}</time></td>
                <td>{entry.level}</td>
                <td>{entry.user_id ?? 'Guest'}</td>
                <td>{entry.ip}</td>
                <td><code>{entry.action}</code></td>
                <td class="details">{entry.details}</td>
              </tr>
            {:else}
              <tr><td colspan="6">Nothing matches these filters.</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
      <Pager page={result.page} pages={result.pages} href={hrefFor} />
    {/if}
  </section>
</AdminGate>

<style>
  .filters {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
    align-items: end;
    gap: var(--space-sm) var(--space-md);
    padding: var(--space-md);
    background: var(--color-paper-shade);
  }

  .filters .field {
    min-width: 0;
  }

  .filters select,
  .filters input {
    width: 100%;
    min-width: 0;
  }

  .filter-actions {
    display: flex;
    align-items: center;
    gap: var(--space-md);
  }

  .log {
    min-width: 52rem;
    font-size: var(--text-sm);
  }

  .log td {
    vertical-align: top;
  }

  .log tr[data-level='WARNING'] td:nth-child(2),
  .log tr[data-level='ERROR'] td:nth-child(2) {
    font-weight: 700;
    color: var(--color-error);
  }

  .details {
    overflow-wrap: anywhere;
  }
</style>
