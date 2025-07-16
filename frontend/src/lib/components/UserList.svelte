<script>
  let { 
    users = $bindable([]),
    eliminated = $bindable([]),
    mafiosi = $bindable([])
  } = $props()
</script>

{#each users as u}
  <div class="user-item">
    <img src="https://avatar.iran.liara.run/public?username={u}" alt="{u}'s avatar" />
    <span class={[eliminated.includes(u) && 'eliminated', mafiosi.includes(u) && 'mafioso']}>{u}</span>
  </div>
{/each}

<style>
  .user-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .user-item img {
    border-radius: 50%;
    width: 32px;
    height: 32px;
  }

  .eliminated {
    opacity: 0.5;
  }

  .mafioso {
    color: red;
  }
</style>