<svelte:options namespace="svg" />

<script lang="ts">
  import type { Fruit } from '../jars'

  let { fruit }: { fruit: Fruit } = $props()
</script>

{#if fruit === 'strawberry'}
  <path d="M0-13C13-15 17 3 0 18C-17 3-13-15 0-13Z" fill="#c0262d" />
  <path d="M-7-8C-9-2-7 6-2 12" stroke="#e05a4f" stroke-width="2.5" fill="none" stroke-linecap="round" />
  <g fill="#f6d77a">
    <circle cx="-5" cy="-3" r="1.2" /><circle cx="4" cy="-5" r="1.2" /><circle cx="0" cy="3" r="1.2" />
    <circle cx="-6" cy="6" r="1.2" /><circle cx="6" cy="4" r="1.2" /><circle cx="1" cy="11" r="1.2" />
    <circle cx="8" cy="-3" r="1.2" />
  </g>
  <path d="M-10-13L0-9L10-13L5-16L0-21L-5-16Z" fill="#4f6b3a" />
  <path d="M0-19V-25" stroke="#4f6b3a" stroke-width="2" stroke-linecap="round" />
{:else if fruit === 'raspberry'}
  <g fill="#c0284a">
    <circle cx="-6" cy="-4" r="4.5" /><circle cx="2" cy="-6" r="4.5" /><circle cx="9" cy="-2" r="4.5" />
    <circle cx="-9" cy="4" r="4.5" /><circle cx="-1" cy="2" r="4.5" /><circle cx="7" cy="6" r="4.5" />
    <circle cx="-5" cy="11" r="4.5" /><circle cx="3" cy="12" r="4.5" />
  </g>
  <g fill="#e4637f">
    <circle cx="-7" cy="-5" r="1.4" /><circle cx="1" cy="-7" r="1.4" /><circle cx="-2" cy="1" r="1.4" />
    <circle cx="-10" cy="3" r="1.4" /><circle cx="6" cy="5" r="1.4" /><circle cx="-6" cy="10" r="1.4" />
  </g>
  <path d="M-8-9L0-12L9-8L3-14L0-19L-4-14Z" fill="#4f6b3a" />
{:else if fruit === 'blueberry'}
  <circle cx="-9" cy="5" r="10" fill="#3b3a78" />
  <circle cx="10" cy="7" r="9" fill="#2e2d63" />
  <circle cx="1" cy="-8" r="10" fill="#46458a" />
  <path d="M1-14l1.5 3 3 .5-2.2 2 .7 3-3-1.5-3 1.5.7-3-2.2-2 3-.5z" fill="#1f1e45" />
  <path d="M-9-1l1.2 2.4 2.4.4-1.8 1.6.6 2.4-2.4-1.2-2.4 1.2.6-2.4-1.8-1.6 2.4-.4z" fill="#1f1e45" />
  <circle cx="-4" cy="-11" r="2.4" fill="#8f8ec4" opacity="0.6" />
  <circle cx="-13" cy="3" r="2" fill="#8f8ec4" opacity="0.6" />
{:else if fruit === 'blackcurrant'}
  <path d="M-18-20C-8-18 4-10 14 6" stroke="#5b4a2e" stroke-width="2" fill="none" stroke-linecap="round" />
  <path d="M-18-20C-26-28-14-34-8-26C-6-22-12-19-18-20Z" fill="#4f6b3a" />
  <g stroke="#5b4a2e" stroke-width="1.4">
    <path d="M-10-16L-12-8" /><path d="M-2-11L-2-2" /><path d="M5-5L8 2" /><path d="M10 0L16 6" />
  </g>
  <circle cx="-12" cy="-5" r="6" fill="#2a1a2e" />
  <circle cx="-2" cy="2" r="6.5" fill="#33203a" />
  <circle cx="9" cy="6" r="6" fill="#2a1a2e" />
  <circle cx="17" cy="11" r="5.5" fill="#33203a" />
  <circle cx="0" cy="13" r="6" fill="#2a1a2e" />
  <g fill="#8c7a95" opacity="0.7">
    <circle cx="-14" cy="-7" r="1.6" /><circle cx="-4" cy="0" r="1.6" /><circle cx="7" cy="4" r="1.6" /><circle cx="-2" cy="11" r="1.6" />
  </g>
{:else if fruit === 'apricot'}
  <circle cx="0" cy="2" r="17" fill="#f2a541" />
  <path d="M-6-13C-11-4-10 9-2 18" stroke="#d9822c" stroke-width="2" fill="none" />
  <ellipse cx="7" cy="5" rx="8" ry="10" fill="#e3782f" opacity="0.6" />
  <circle cx="-8" cy="-5" r="3" fill="#f8c97c" />
  <path d="M-4-14L-3-20" stroke="#6b4a2a" stroke-width="2" />
  <path d="M-3-19C5-27 13-23 8-17C4-14 0-16-3-19Z" fill="#4f6b3a" />
{:else if fruit === 'cherry'}
  <path d="M-7 2C-4-12 2-18 6-22M8 4C8-8 7-16 6-22" stroke="#4f6b3a" stroke-width="2" fill="none" />
  <path d="M6-22C14-26 20-20 14-16C10-14 7-18 6-22Z" fill="#4f6b3a" />
  <circle cx="-8" cy="8" r="9" fill="#8e1426" />
  <circle cx="9" cy="10" r="9" fill="#a5182c" />
  <circle cx="-11" cy="5" r="2.2" fill="#e8a0a8" />
  <circle cx="6" cy="7" r="2.2" fill="#e8a0a8" />
{:else if fruit === 'quince'}
  <path d="M0-16C10-16 12-6 14 2C18 14 10 20 0 20C-10 20-18 14-14 2C-12-6-10-16 0-16Z" fill="#e2b13c" />
  <path d="M-9 0C-10 8-6 14 0 16" stroke="#f3d27a" stroke-width="3" fill="none" stroke-linecap="round" />
  <path d="M0-16L1-22" stroke="#6b4a2a" stroke-width="2" />
  <path d="M1-21C9-27 15-22 10-17C6-15 3-18 1-21Z" fill="#4f6b3a" />
  <g fill="#b8862a"><circle cx="6" cy="6" r="1.2" /><circle cx="9" cy="-2" r="1" /><circle cx="2" cy="12" r="1" /></g>
{:else if fruit === 'rose'}
  <circle cx="0" cy="0" r="17" fill="#d9607a" />
  <path d="M-15-4C-10-16 10-16 15-4C8-9-8-9-15-4Z" fill="#e88aa0" />
  <path d="M-14 6C-8 16 8 16 14 6C8 10-8 10-14 6Z" fill="#c24a66" />
  <circle cx="0" cy="0" r="9" fill="#c9506d" />
  <path d="M-5 0C-5-6 5-6 5 0C5 4 0 5-1 2" stroke="#8f2a45" stroke-width="1.6" fill="none" stroke-linecap="round" />
  <path d="M-22 14C-18 8-10 10-12 16C-14 20-20 19-22 14Z" fill="#e88aa0" />
  <path d="M12-14C18-22 26-18 22-12C19-9 14-11 12-14Z" fill="#4f6b3a" />
{:else if fruit === 'green-walnut'}
  <path d="M-6-18C-2-22 4-22 8-18" stroke="#5b4a2e" stroke-width="2" fill="none" stroke-linecap="round" />
  <circle cx="-7" cy="0" r="13" fill="#6f8f3a" />
  <circle cx="10" cy="6" r="12" fill="#7d9c44" />
  <g fill="#a9c26a" opacity="0.8">
    <circle cx="-11" cy="-4" r="1.6" /><circle cx="-3" cy="5" r="1.4" /><circle cx="6" cy="1" r="1.4" /><circle cx="13" cy="10" r="1.6" />
  </g>
  <path d="M8-18C16-24 24-18 18-12C14-10 10-13 8-18Z" fill="#4f6b3a" />
{:else if fruit === 'plum'}
  <ellipse cx="0" cy="2" rx="14" ry="16" fill="#4b3b6b" />
  <path d="M-2-13C-6-4-6 8-1 17" stroke="#2f2448" stroke-width="1.6" fill="none" />
  <path d="M1-14C8-22 16-20 12-14C9-11 4-12 1-14Z" fill="#4f6b3a" />
  <ellipse cx="6" cy="-3" rx="3" ry="5" fill="#7b6aa0" />
{:else if fruit === 'apple'}
  <rect x="-26" y="10" width="30" height="5" rx="2.5" fill="#8a4b2a" transform="rotate(-12 -11 12)" />
  <rect x="-24" y="16" width="28" height="5" rx="2.5" fill="#a0592f" transform="rotate(-6 -10 18)" />
  <path d="M2-12C10-18 20-12 18 2C17 14 8 20 2 16C-4 20-13 14-14 2C-16-12-6-18 2-12Z" fill="#c43d2f" />
  <path d="M10-6C14-2 14 6 10 11" stroke="#e8b34a" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.8" />
  <path d="M2-12L3-20" stroke="#6b4a2a" stroke-width="2" />
  <path d="M3-18C10-25 18-20 13-14C9-12 6-15 3-18Z" fill="#4f6b3a" />
{:else if fruit === 'fig'}
  <path d="M-4-16C-2-10 12-2 10 10C8 18-12 18-14 8C-16-2-6-8-4-16Z" fill="#6b3550" />
  <path d="M-9 0C-10 6-8 11-3 13" stroke="#8f5274" stroke-width="2.5" fill="none" stroke-linecap="round" />
  <path d="M-4-16L-3-21" stroke="#4f6b3a" stroke-width="2.4" />
  <circle cx="16" cy="12" r="9" fill="#9a6a3a" />
  <path d="M16 4V20M10 8c3 2 3 6 0 8M22 8c-3 2-3 6 0 8" stroke="#6b4422" stroke-width="1.2" fill="none" />
{:else if fruit === 'peach'}
  <circle cx="0" cy="3" r="17" fill="#f4a77a" />
  <path d="M0-12C-4-4-4 8 0 19" stroke="#d9714a" stroke-width="2" fill="none" />
  <ellipse cx="7" cy="6" rx="8" ry="10" fill="#e8667a" opacity="0.55" />
  <circle cx="-8" cy="-3" r="3" fill="#fbd2b6" />
  <path d="M0-14L1-20" stroke="#6b4a2a" stroke-width="2" />
  <path d="M1-19C9-27 18-22 12-16C8-13 4-15 1-19Z" fill="#4f6b3a" />
{:else if fruit === 'cherry-plum'}
  <circle cx="-8" cy="6" r="10" fill="#e8a43c" />
  <circle cx="10" cy="8" r="10" fill="#d4533a" />
  <circle cx="1" cy="-6" r="10" fill="#e9b94a" />
  <path d="M1-16L3-23M-8-4L-10-12M10-2L12-10" stroke="#6b4a2a" stroke-width="1.6" stroke-linecap="round" />
  <circle cx="-3" cy="-9" r="2.4" fill="#f6dc94" opacity="0.8" />
  <circle cx="6" cy="4" r="2.4" fill="#ef9a86" opacity="0.8" />
{:else if fruit === 'forest'}
  <g fill="#2a1a38">
    <circle cx="-9" cy="2" r="6" /><circle cx="-1" cy="-3" r="6" /><circle cx="-3" cy="8" r="6" />
  </g>
  <g fill="#c0284a">
    <circle cx="7" cy="0" r="5.5" /><circle cx="12" cy="8" r="5.5" />
  </g>
  <circle cx="-14" cy="12" r="5.5" fill="#3b3a78" />
  <circle cx="3" cy="13" r="3.2" fill="#d8342f" />
  <path d="M-6-8L2-14L10-8L3-12Z" fill="#4f6b3a" />
  <g fill="#8c7a95" opacity="0.7"><circle cx="-10" cy="0" r="1.4" /><circle cx="-2" cy="-5" r="1.4" /></g>
{:else if fruit === 'pear'}
  <path d="M0-18C6-18 7-8 9-2C16 6 15 18 0 19C-15 18-16 6-9-2C-7-8-6-18 0-18Z" fill="#c9c35a" />
  <path d="M-8 4C-9 10-5 15 0 16" stroke="#e8e394" stroke-width="3" fill="none" stroke-linecap="round" />
  <path d="M0-18L2-25" stroke="#6b4a2a" stroke-width="2" />
  <path d="M2-23C10-29 16-24 11-19C7-17 4-20 2-23Z" fill="#4f6b3a" />
  <path d="M-26 20L-6 18M-26 14L-8 16" stroke="#2f1d14" stroke-width="3" stroke-linecap="round" />
{:else if fruit === 'lingonberry'}
  <path d="M-14-6C-6-12 6-12 14-6" stroke="#4f6b3a" stroke-width="2" fill="none" />
  <path d="M-14-6C-22-12-14-18-9-12C-8-9-11-7-14-6Z" fill="#4f6b3a" />
  <path d="M14-6C22-12 14-18 9-12C8-9 11-7 14-6Z" fill="#4f6b3a" />
  <circle cx="-9" cy="2" r="5.5" fill="#b0182f" />
  <circle cx="1" cy="4" r="5.5" fill="#c21f38" />
  <circle cx="10" cy="2" r="5.5" fill="#a3182f" />
  <circle cx="-4" cy="12" r="5.5" fill="#c21f38" />
  <circle cx="6" cy="13" r="5.5" fill="#b0182f" />
  <g fill="#f0a0aa" opacity="0.8"><circle cx="-11" cy="0" r="1.4" /><circle cx="-1" cy="2" r="1.4" /><circle cx="8" cy="0" r="1.4" /></g>
{:else if fruit === 'orange'}
  <circle cx="0" cy="2" r="17" fill="#ee8a1f" />
  <g fill="#f4a94a" opacity="0.8">
    <circle cx="-7" cy="-5" r="1.3" /><circle cx="4" cy="-8" r="1.3" /><circle cx="9" cy="2" r="1.3" />
    <circle cx="-4" cy="6" r="1.3" /><circle cx="3" cy="12" r="1.3" /><circle cx="-10" cy="5" r="1.3" />
  </g>
  <ellipse cx="-7" cy="-6" rx="3" ry="5" fill="#f9c98a" opacity="0.6" transform="rotate(-30 -7 -6)" />
  <path d="M0-15L1-20" stroke="#6b4a2a" stroke-width="2" />
  <path d="M1-19C9-26 17-21 12-15C8-13 4-15 1-19Z" fill="#4f6b3a" />
{:else if fruit === 'lemon'}
  <path d="M-18 2C-18-8-8-15 2-14C6-14 14-18 18-14C20-10 16-6 18 2C18 12 8 18-2 17C-6 18-14 18-16 12C-18 9-18 5-18 2Z" fill="#f1d23a" />
  <ellipse cx="-6" cy="-3" rx="6" ry="3.5" fill="#fbeb86" opacity="0.7" transform="rotate(-25 -6 -3)" />
  <path d="M0-14L2-19" stroke="#6b4a2a" stroke-width="2" />
  <path d="M2-18C10-25 18-20 13-14C9-12 5-14 2-18Z" fill="#4f6b3a" />
  <path d="M14 14C20 8 28 12 22 18C19 20 16 18 14 14Z" fill="#d8b37a" />
{:else if fruit === 'rosehip'}
  <path d="M-12-20C-6-12-2-6 0 0M4-22C4-12 6-4 8 2" stroke="#5b4a2e" stroke-width="1.8" fill="none" />
  <ellipse cx="-4" cy="8" rx="7" ry="11" fill="#d9481e" transform="rotate(-18 -4 8)" />
  <ellipse cx="11" cy="11" rx="7" ry="11" fill="#c2401c" transform="rotate(12 11 11)" />
  <ellipse cx="-6" cy="4" rx="2" ry="4" fill="#f08a5d" transform="rotate(-18 -6 4)" />
  <path d="M-1-4l-3-4M-1-4l2-5M-1-4l4-2" stroke="#3b2a1a" stroke-width="1.6" stroke-linecap="round" />
  <path d="M8-1l-2-5M8-1l3-4M8-1l5 0" stroke="#3b2a1a" stroke-width="1.6" stroke-linecap="round" />
  <path d="M-12-20C-20-26-24-16-16-14C-13-13-12-17-12-20Z" fill="#4f6b3a" />
{/if}
