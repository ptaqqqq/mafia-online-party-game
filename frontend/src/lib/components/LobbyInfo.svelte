<script>
  let { 
    lobbySettings = $bindable({ code: 'ABCDEF', votingTime: 60, mafiosi: 3 })
  } = $props()
</script>

{#each Object.entries(lobbySettings) as [key, value]}
  <p><strong>{key}:</strong> {value}</p>
{/each}