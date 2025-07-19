<script lang="ts">
    let username = $state('user_' + Math.floor(Math.random() * 10000));

    let showJoinLobbyModal = $state(false);
    let lobbyCode = $state('');

    function checkUsername() {
      if (!username.trim()) {
        alert('Please enter a valid username.');
        return false;
      }
      return true;
    }

    function cancelJoin() {
      showJoinLobbyModal = false;
      lobbyCode = '';
    }

    function confirmJoin() {
      if (!lobbyCode.trim()) {
        return alert('Please enter a lobby code.');
      }
  
      console.log('Joining lobby:', lobbyCode, 'as', username);

      window.location.assign('/game'+ '?room_id=' + lobbyCode + "&nickname=" + username);
    }

    function joinLobby() {
      if (!checkUsername()) return;
      
      console.log('User choose to join an exisiting lobby')
      showJoinLobbyModal = true;
    }

    function createLobby() {
      if (!checkUsername()) return;

      console.log('User choose to create a new lobby');
      
      let randomCode = (Math.random() + 1).toString(36).substring(7).toUpperCase();
      window.location.assign('/game'+ '?room_id=' + randomCode + "&nickname=" + username);
    }

    function handleEscape(e: KeyboardEvent) {
      if (e.key !== 'Escape') return;
      
      if (showJoinLobbyModal) {
        cancelJoin();
      }
    }
</script>

<svelte:window onkeydown={handleEscape} />

<div id="page">
  <h1 id="title">Play Mafia Online!</h1>

  <div id="container">
    <div id="top">
      <input type="text" bind:value={username} placeholder="Username" />
    </div>
    <div id="bottom">
      <button onclick={joinLobby}>Join lobby</button>
      <button onclick={createLobby}>Create lobby</button>
    </div>
  </div>
</div>

{#if showJoinLobbyModal}
<div class="modal" aria-modal="true" role="dialog">
  <div class="modal-content">
    <h2>Join Lobby</h2>
    <input
      type="text"
      bind:value={lobbyCode}
      placeholder="Enter lobby code"
    />

    <div class="modal-actions">
      <button onclick={confirmJoin}>Join</button>
      <button onclick={cancelJoin}>Cancel</button>
    </div>
  </div>
</div>
{/if}

<style>
  #page {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  #title {
    text-align: center;
  }

  #container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    max-width: 400px;
    width: 100%;
  }

  #top {
    width: 100%;
  }

  #top input {
    width: 100%;
    box-sizing: border-box;
  }

  #bottom {
    width: 100%;
    display: flex;
    gap: 0.5rem;
  }

  #bottom button {
    flex: 1;
  }

  /* modal overlay */
  .modal {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }
  .modal-content {
    background: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    max-width: 360px;
    width: 90%;
    box-sizing: border-box;
    text-align: center;
  }
  .modal-content input {
    width: 100%;
    margin-top: 1rem;
    padding: 0.5rem;
    box-sizing: border-box;
  }
  .modal-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .modal-actions button {
    flex: 1;
    padding: 0.5rem;
  }
</style>
