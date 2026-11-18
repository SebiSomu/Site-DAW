<script lang="ts">
  import type { ProductSummary } from '../api/types'
  import { jarLook, jarShape } from '../jars'
  import FruitArt from './FruitArt.svelte'

  let { product }: { product: Pick<ProductSummary, 'slug' | 'name' | 'category'> } = $props()

  const uid = $props.id()
  const look = $derived(jarLook(product))
  const shape = $derived(jarShape(product))

  const centre = $derived(shape.x + shape.width / 2)
  const top = $derived(shape.y)
  const bottom = $derived(shape.y + shape.height)
  const clothWidth = $derived(shape.width - 4)
  const clothLeft = $derived(centre - clothWidth / 2)
  const clothTop = $derived(top - 30)
  const clothBottom = $derived(top - 5)
  const cloth = $derived(clothPath())
  const labelWidth = $derived(Math.min(shape.width - 18, 92))
  const labelY = $derived(top + shape.height * 0.4)
  const labelFit = $derived(look.label.length > 10 ? labelWidth - 12 : undefined)

  function clothPath(): string {
    const scallops = Math.round(clothWidth / 12)
    const step = clothWidth / scallops
    let path = `M${clothLeft} ${clothTop + 6}Q${centre} ${clothTop - 9} ${clothLeft + clothWidth} ${clothTop + 6}L${clothLeft + clothWidth} ${clothBottom}`
    for (let index = 1; index <= scallops; index++) {
      path += `A${step / 2} ${step / 2} 0 0 1 ${(clothLeft + clothWidth - index * step).toFixed(1)} ${clothBottom}`
    }
    return `${path}Z`
  }
</script>

<svg class="jar-art" viewBox="0 0 200 200" role="img" aria-label={`Illustration of a jar of ${product.name}`}>
  <defs>
    <pattern id={`${uid}-cloth`} width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="#fffcf7" />
      <rect width="5" height="10" fill={shape.cloth} opacity="0.45" />
      <rect width="10" height="5" fill={shape.cloth} opacity="0.45" />
    </pattern>
  </defs>
  <rect width="200" height="200" fill={look.tile} />
  <ellipse cx={centre} cy={bottom + 4} rx={shape.width / 2 + 8} ry="6" fill="#3b1f24" opacity="0.1" />
  <rect x={shape.x + 10} y={top - 12} width={shape.width - 20} height="14" rx="3" fill="#d9cfc0" />
  <rect x={shape.x} y={top} width={shape.width} height={shape.height} rx={shape.radius} fill="#efe8de" stroke="#cfc3b2" stroke-width="2" />
  <rect
    x={shape.x + 5}
    y={top + 12}
    width={shape.width - 10}
    height={shape.height - 17}
    rx={Math.max(shape.radius - 5, 3)}
    fill={look.fill}
  />
  <rect x={shape.x + 11} y={top + 18} width="6" height={shape.height * 0.5} rx="3" fill="#fff" opacity="0.35" />
  <g class="jar-lid">
    <path d={cloth} fill={`url(#${uid}-cloth)`} />
    <path
      d={`M${clothLeft + 4} ${clothBottom - 6}Q${centre} ${clothBottom - 1} ${clothLeft + clothWidth - 4} ${clothBottom - 6}`}
      stroke="#8a6a3f"
      stroke-width="2.5"
      fill="none"
    />
    <path
      d={`M${centre + 14} ${clothBottom - 4}c6-6 12-4 8 2M${centre + 14} ${clothBottom - 4}c2 8-2 12-6 9`}
      stroke="#8a6a3f"
      stroke-width="2"
      fill="none"
      stroke-linecap="round"
    />
  </g>
  <g transform={`rotate(-2 ${centre} ${labelY + 17})`}>
    <rect x={centre - labelWidth / 2} y={labelY} width={labelWidth} height="34" rx="3" fill="#fffcf7" />
    <text
      x={centre}
      y={labelY + 24}
      text-anchor="middle"
      font-family="Caveat Variable, cursive"
      font-weight="700"
      font-size="19"
      fill="#3b1f24"
      textLength={labelFit}
      lengthAdjust="spacingAndGlyphs">{look.label}</text
    >
  </g>
  {#if look.fruit}
    <g transform={`translate(${shape.x + shape.width + 4} ${bottom - 8}) scale(1.05)`}>
      <FruitArt fruit={look.fruit} />
    </g>
  {/if}
</svg>

<style>
  .jar-art {
    display: block;
    width: 100%;
    height: auto;
    aspect-ratio: 1;
  }
</style>
