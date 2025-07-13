<script>
  let { users = $bindable([]) } = $props()
</script>

{#each users as u}
  <div class="user-item">
    <img src="https://avatar.iran.liara.run/public?username={u}" alt="{u}'s avatar" />
    <span>{u}</span>
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
</style>