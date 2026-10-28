<script lang="ts">
  import { router } from '../router/router.svelte'

  interface Props {
    title: string
    description: string
    path?: string
    image?: string
    noindex?: boolean
  }

  const SITE_NAME = "Mum's Homemade Jams"

  let { title, description, path, image = '/images/jar-placeholder.svg', noindex = false }: Props = $props()

  const fullTitle = $derived(title === SITE_NAME ? title : `${title} | ${SITE_NAME}`)
  const canonical = $derived(new URL(path ?? router.url.pathname, window.location.origin).href)
  const imageUrl = $derived(new URL(image, window.location.origin).href)
</script>

<svelte:head>
  <title>{fullTitle}</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={canonical} />
  {#if noindex}
    <meta name="robots" content="noindex" />
  {/if}
  <meta property="og:site_name" content={SITE_NAME} />
  <meta property="og:type" content="website" />
  <meta property="og:title" content={fullTitle} />
  <meta property="og:description" content={description} />
  <meta property="og:url" content={canonical} />
  <meta property="og:image" content={imageUrl} />
</svelte:head>
