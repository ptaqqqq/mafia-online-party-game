<script>
  let { 
    users: user_ids = $bindable([]),
    user_display_names = $bindable({}),
    eliminated = $bindable([]),
    mafiosi = $bindable([])
  } = $props()

  user_ids.filter(u => !(u in user_display_names)).forEach(u => user_display_names[u] = u);
</script>

{#each user_ids as u}
  <div class="user-item">
    <img src="https://avatar.iran.liara.run/public?username={u}" alt="{user_display_names[u]}'s avatar" />
    <span class={[eliminated.includes(u) && 'eliminated', mafiosi.includes(u) && 'mafioso']}>{user_display_names[u]}</span>
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