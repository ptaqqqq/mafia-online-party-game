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
  :global(body) {
    background: url('/city-theme-bg.png') center/cover no-repeat;
    margin: 0;
    padding: 0;
    font-family: 'Georgia', serif;
    height: 100vh;
    overflow: hidden;
  }

  #page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }

  #title {
    text-align: center;
    color: #f4e4bc;
    font-size: 3.5em;
    margin-bottom: 2rem;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
    font-weight: bold;
    letter-spacing: 2px;
  }

  #container {
    background: linear-gradient(135deg, rgba(44, 24, 16, 0.95), rgba(26, 15, 8, 0.95));
    border: 2px solid #8b4513;
    border-radius: 20px;
    padding: 3rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
  }

  #top {
    width: 100%;
  }

  #top input {
    width: 100%;
    box-sizing: border-box;
    padding: 1rem;
    font-size: 1.2em;
    border: 2px solid #8b4513;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    color: #2c1810;
    font-family: 'Georgia', serif;
    transition: all 0.3s ease;
  }

  #top input:focus {
    outline: none;
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
    background: rgba(255, 255, 255, 1);
  }

  #top input::placeholder {
    color: #8b4513;
    opacity: 0.7;
  }

  #bottom {
    width: 100%;
    display: flex;
    gap: 1rem;
  }

  #bottom button {
    flex: 1;
    padding: 1.2rem 2rem;
    font-size: 1.1em;
    font-weight: bold;
    border: 2px solid #8b4513;
    border-radius: 12px;
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Georgia', serif;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  #bottom button:hover {
    background: linear-gradient(135deg, #f4d03f, #d4af37);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(212, 175, 55, 0.4);
  }

  #bottom button:active {
    transform: translateY(0);
    box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3);
  }

  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
    backdrop-filter: blur(5px);
  }

  .modal-content {
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    border: 2px solid #8b4513;
    border-radius: 20px;
    padding: 2.5rem;
    max-width: 450px;
    width: 90%;
    box-sizing: border-box;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8);
  }

  .modal-content h2 {
    color: #d4af37;
    font-size: 1.8em;
    margin: 0 0 1.5rem 0;
    font-family: 'Georgia', serif;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
  }

  .modal-content input {
    width: 100%;
    margin-top: 1rem;
    padding: 1rem;
    box-sizing: border-box;
    font-size: 1.1em;
    border: 2px solid #8b4513;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    color: #2c1810;
    font-family: 'Georgia', serif;
    transition: all 0.3s ease;
  }

  .modal-content input:focus {
    outline: none;
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
    background: rgba(255, 255, 255, 1);
  }

  .modal-content input::placeholder {
    color: #8b4513;
    opacity: 0.7;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .modal-actions button {
    flex: 1;
    padding: 1rem 1.5rem;
    font-size: 1.1em;
    font-weight: bold;
    border: 2px solid #8b4513;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Georgia', serif;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .modal-actions button:first-child {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
  }

  .modal-actions button:first-child:hover {
    background: linear-gradient(135deg, #f4d03f, #d4af37);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(212, 175, 55, 0.4);
  }

  .modal-actions button:last-child {
    background: linear-gradient(135deg, #8b4513, #654321);
    color: #f4e4bc;
  }

  .modal-actions button:last-child:hover {
    background: linear-gradient(135deg, #a0522d, #8b4513);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(139, 69, 19, 0.4);
  }

  .modal-actions button:active {
    transform: translateY(0);
  }

  @media (max-width: 600px) {
    #title {
      font-size: 2.5em;
      margin-bottom: 1.5rem;
    }

    #container {
      padding: 2rem;
      margin: 1rem;
    }

    #bottom {
      flex-direction: column;
    }

    .modal-content {
      padding: 2rem;
      margin: 1rem;
    }

    .modal-actions {
      flex-direction: column;
    }
  }
</style>
