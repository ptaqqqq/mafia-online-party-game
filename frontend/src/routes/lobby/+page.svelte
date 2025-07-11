<script>
  import { onMount, tick } from 'svelte';
  // dummy data
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
  let chatContainer;
  
  onMount(() => scrollToBottom(chatContainer))

  async function sendMessage() {
    if (!newMessage.trim()) return;
    messages = [...messages, { id: Date.now(), user: 'me', text: newMessage }];
    await tick();
    scrollToBottom(chatContainer)
  }

  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
  }
</script>

<main>
  <!-- Lobby Info -->
  <div class="lobby-info overlay">
    {#each Object.entries(lobbySettings) as [key, value]}
      <p><strong>{key}:</strong> {value}</p>
    {/each}
  </div>
  
  <!-- Chat Messages -->
  <div class="chat-container overlay" bind:this={chatContainer}>
    {#each messages as msg}
      <div class="message-card">
        <strong>{msg.user}</strong>
        <p>{msg.text}</p>
      </div>
    {/each}
  </div>

  <!-- User List -->
  <div class="user-list overlay">
    {#each users as u}
      <div class="user-item">
        <img src="https://avatar.iran.liara.run/public?username={u}" alt="avatar" />
        <span>{u}</span>
      </div>
    {/each}
  </div>

  <!-- Input -->
   <div class="input-area overlay">
    <input
      type="text"
      placeholder="Type your message here..."
      bind:value={newMessage}
      onkeydown={(e) => e.key === 'Enter' && sendMessage()}
    />
    <button class="send-btn" onclick={sendMessage}>
      ↩
    </button>
   </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: sans-serif;
    height: 100vh;
    overflow: hidden;
  }

  main {
    background: url('/city-theme-bg.png') center/cover no-repeat;
    position: relative;
    width: 100%;
    height: 100%;
  }

  .overlay {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(6px);
    border-radius: 1rem;
    padding: 1rem;
  }

  .lobby-info {
    position: absolute;
    top: 2rem;
    left: 2rem;
    width: 200px;
  }

  .chat-container {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    max-height: 60%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .message-card {
    background: white;
    border-radius: 0.75rem;
    padding: 0.75rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  .message-card strong {
    display: block;
    margin-bottom: 0.25rem;
  }

  .user-list {
    position: absolute;
    top: 2rem;
    right: 2rem;
    width: 200px;
    max-height: 70%;
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
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    width: 500px;
    gap: 0.5rem;
  }

  .input-area input {
    flex: 1;
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
    width: 3.5rem;
    font-size: 1.25rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #28a745;
    color: white;
  }
</style>
