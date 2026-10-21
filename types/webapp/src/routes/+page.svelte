<script lang="ts">
  import { VERSION } from '#lib/version.ts';
</script>

<svelte:head>
  <title>@@NAME@@</title>
</svelte:head>

<main>
  <h1>@@NAME@@</h1>
  <p>@@DESCRIPTION@@</p>
  <p class="version">Version {VERSION}</p>
</main>

<style>
  main {
    max-width: 40rem;
    margin: 4rem auto;
    padding: 0 1.5rem;
    font-family: system-ui, sans-serif;
  }
  .version {
    color: #6b7280;
    font-size: 0.875rem;
  }
</style>
