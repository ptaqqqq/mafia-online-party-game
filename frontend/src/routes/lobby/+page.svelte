<script>
  import { onMount, tick } from 'svelte';
  // dummy data
  let gameTheme = $state('Game Theme')

  let lobbySettings = $state({
    code: 'ABCDEF',
    votingTime: 60,
    mafiosi: 3
  });
  
  let messages = $state([
  { id: 1, user: 'user_1234', text: 'Hello, world!'},
  { id: 2, user: 'user_1234', text: 'Hello, world!'},
  { id: 3, user: 'user_1234', text: 'Hello, world!'},
  { id: 4, user: 'user_1234', text: 'Hello, world!'},
  ]);
  
  let users = Array.from({ length: 10 }, () => 'user_' + Math.floor(Math.random() * 10000));
  let newMessage = $state('');
  /**
     * @type {HTMLDivElement}
     */
  let chatContainer;
  
  onMount(() => scrollToBottom(chatContainer))

  async function sendMessage() {
    if (!newMessage.trim()) return;
    messages.push({ id: Date.now(), user: 'me', text: newMessage });
    newMessage = ''
    await tick();
    scrollToBottom(chatContainer)
  }

  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
  }
</script>

<header>
  <h1 class='game-theme'>{gameTheme}</h1>
</header>

<main>
  <div class="main-area">
    <!-- Lobby Info -->
    <div class="lobby-info overlay">
      {#each Object.entries(lobbySettings) as [key, value]}
        <p><strong>{key}:</strong> {value}</p>
      {/each}
    </div>
    
    <!-- Chat Messages -->
    <div class="chat-area">
      <div class="chat-container overlay" bind:this={chatContainer}>
        {#each messages as msg}
          <div class="message-card">
            <strong>{msg.user}</strong>
            <p>{msg.text}</p>
          </div>
        {/each}
      </div>

      <!-- Input -->
      <div class="input-area overlay">
        <input
          type="text"
          placeholder="Type your message here..."
          aria-label="Type your message"
          bind:value={newMessage}
          onkeydown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button class="send-btn" onclick={sendMessage}>
          ↩
        </button>
      </div>
    </div>

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

  .overlay {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(6px);
    border-radius: 1rem;
    padding: 1rem;
    margin: 1rem;
    height: auto;
    align-self: center;
    border: 1px solid black;
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
    .main-area {
      gap: 1rem;
      grid-template-rows: 20vh 1fr 15vh;
    }
  }

  .lobby-info {
    width: auto;
  }

  .chat-area {
    width: auto;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: hidden;
    overflow-x: hidden;
    padding: 1rem;
  }

  .chat-container {
    width: 99%;
    height: 100%;
    min-height: 10vh;
    max-height: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
  }

  .message-card {
    background: white;
    border-radius: 0.75rem;
    border: 1px solid black;
    padding: 0.75rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  .message-card strong {
    display: block;
    margin-bottom: 0.25rem;
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

  .input-area {
    width: 100%;
    min-height: 2rem;
    display: flex;
    gap: 0.5rem;
    height: 10%;
    padding: 0.75rem;
    margin-top: 0;
  }

  .input-area input {
    flex: 1;
    width: 100%;
    border: none;
    outline: none;
    padding: 0.75rem 1rem;
    border-radius: 0.75rem;
    font-size: 1rem;
    background: rgba(255, 255, 255, 0.9);
  }

  .send-btn {
    border: none;
    border-radius: 0.75rem;
    height: auto;
    font-size: 1.25rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #28a745;
    color: white;
    padding-left: 1rem;
    padding-right: 1rem;
  }
</style>
