<script>
  import Chat from '$lib/components/Chat.svelte';
  import LobbyInfo from '$lib/components/LobbyInfo.svelte';

  // dummy data
  let messages = $state([
    { 'id': 1, 'user': 'user_1234', 'text': 'Hello, world!'},
    { 'id': 2, 'user': 'user_1234', 'text': 'Hello, world!'},
    { 'id': 3, 'user': 'user_1234', 'text': 'Hello, world!'},
    { 'id': 4, 'user': 'user_1234', 'text': 'Hello, world!'},
  ])
  let newMessage = $state('');
  let gameTheme = $state('Game Theme')
  let lobbySettings = $state({
    code: 'ABCDEF',
    votingTime: 60,
    mafiosi: 3
  });
  let users = Array.from({ length: 10 }, () => 'user_' + Math.floor(Math.random() * 10000));
</script>

<header>
  <h1 class='game-theme'>{gameTheme}</h1>
</header>

<main>
  <div class="main-area">
    <div class="lobby-info overlay">
      <LobbyInfo {lobbySettings} />
    </div>

    <Chat {messages} />

    <!-- User List -->
    <div class="user-list overlay">
      {#each users as u}
        <div class="user-item">
          <img src="https://avatar.iran.liara.run/public?username={u}" alt="{u}'s avatar" />
          <span>{u}</span>
        </div>
      {/each}
    </div>
  </div>

</main>

<style>
  :global(body) {
    background: url('/city-theme-bg.png') center/cover no-repeat;
    margin: 0;
    padding: 0;
    font-family: sans-serif;
    height: 100vh;
    overflow: hidden;
  }

  :global(.overlay) {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(6px);
    border-radius: 1rem;
    padding: 1rem;
    margin: 1rem;
    height: auto;
    align-self: center;
    border: 1px solid black;
  }

  header {
    position: relative;
    width: 100%;
    height: 5vh;    
    display: flex;
    justify-content: center;
    align-content: center;
  }


  main {
    position: absolute;
    width: 100%;
    height: 90vh;
    /* max-height: 90%; */
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .main-area {
    flex: 1;
    flex-shrink: 0;
    overflow-y: hidden;
    display: grid;
    padding: 1rem;
    margin: 1rem;
    align-items: center;
    width: 90%;
    max-height: 100%;
    height: 100%;
    grid-template-rows: 1fr;
  }

  /* Desktop: fixed sidebars, flexible centre */
  @media (min-width: 800px) {
    .main-area {
      gap: 3rem;
      grid-template-columns:
        /* left  */ 20vw
        /* centre*/ 1fr
        /* right */ 20vw;
    }
    .lobby-info, 
    .user-list {
      transform: translateY(-5vh);
    }
  }

  /* Mobile and tablet: single column */
  @media (max-width: 799px) {
    :global(body) {
      overflow-y: auto;
    }

    .main-area {
      gap: 1rem;
      grid-template-rows: 20vh 1fr 15vh;
    }
  }

  .lobby-info {
    width: auto;
  }

  .user-list {
    width: auto;
    height: auto;
    max-height: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

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
