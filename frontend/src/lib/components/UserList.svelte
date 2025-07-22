<script>
  let {
    users: user_ids = $bindable([]),
    userDisplayNames = $bindable({}),
    eliminated = $bindable([]),
    mafiosi = $bindable([]),
    medics = $bindable([])
  } = $props()

  user_ids.filter(u => !(u in userDisplayNames)).forEach(u => userDisplayNames[u] = u);
</script>

{#each user_ids as u}
  <div class="user-item">
    <img src="https://avatar.iran.liara.run/public?username={u}" alt="{userDisplayNames[u]}'s avatar" />
    <span class={[eliminated.includes(u) && 'eliminated', mafiosi.includes(u) && 'mafioso', medics.includes(u) && 'medic']}>{userDisplayNames[u]}</span>
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

  .medic {
    color: green;
  }
</style>