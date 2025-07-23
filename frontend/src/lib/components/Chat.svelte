<script>
  import { onMount, tick } from 'svelte';

  let {
    messages = $bindable(),
    sendMessageHandler = (/** @type {string} */ msgText) => { messages.push({ id: Date.now(), user: 'me', text: msgText }); }
  } = $props()
  let newMessage = $state()

  /**
  * @type {HTMLDivElement}
  */
  let messagesContainer;

  onMount(() => scrollToBottom(messagesContainer))

  export async function sendMessage() {
    if (!newMessage.trim()) return;
    sendMessageHandler(newMessage);
    newMessage = '';
    await tick();
    scrollToBottom(messagesContainer);
  }

  // @ts-ignore
  export async function addMessage(msg) {
    messages.push(msg);
    messages = messages;
    await tick();
    scrollToBottom(messagesContainer);
  }

  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
  }

  function getUserAvatar(username) {
    return `https://avatar.iran.liara.run/public?username=${username}`;
  }

  function getMessageTime() {
    return new Date().toLocaleTimeString('pl-PL', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function isSystemMessage(user) {
    return user === 'System' || user === 'Narrator' || user === 'Game';
  }
</script>

<div class="chat-container">
  <div class="chat-header">
    <div class="chat-icon">💬</div>
    <h3>Town Chat</h3>
    <div class="online-indicator">
      <span class="status-dot"></span>
      <span class="status-text">Online</span>
    </div>
  </div>

  <div class="messages-container" bind:this={messagesContainer}>
    {#each messages as msg (msg.id)}
      {#if isSystemMessage(msg.user)}
        <div class="system-message">
          <div class="system-icon">🎭</div>
          <div class="system-text">{msg.text}</div>
        </div>
      {:else}
        <div class="message-card">
          <div class="message-header">
            <div class="user-avatar">
              <img src={getUserAvatar(msg.user)} alt="{msg.user}'s avatar" />
            </div>
            <div class="user-info">
              <div class="username">{msg.user}</div>
              <div class="message-time">{getMessageTime()}</div>
            </div>
          </div>
          <div class="message-content">
            <p>{msg.text}</p>
          </div>
        </div>
      {/if}
    {/each}
  </div>

  <div class="input-area">
    <div class="input-wrapper">
      <input
        type="text"
        placeholder="Type your message here..."
        aria-label="Type your message"
        bind:value={newMessage}
        onkeydown={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button class="send-btn" onclick={sendMessage}>
        <span class="send-icon">📤</span>
      </button>
    </div>
  </div>
</div>

<style>
  .chat-container {
    background: linear-gradient(135deg, rgba(44, 24, 16, 0.95), rgba(26, 15, 8, 0.95));
    border: 2px solid #8b4513;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    font-family: 'Georgia', serif;
  }

  .chat-header {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    padding: 1rem 1.5rem;
    border-bottom: 2px solid #8b4513;
    display: flex;
    align-items: center;
    gap: 1rem;
    border-radius: 18px 18px 0 0;
  }

  .chat-icon {
    font-size: 1.5em;
    animation: bounce 2s infinite;
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
  }

  .chat-header h3 {
    color: #2c1810;
    font-size: 1.3em;
    margin: 0;
    font-weight: bold;
    flex: 1;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  }

  .online-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #2c1810;
    font-size: 0.9em;
    font-weight: bold;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.05));
  }

  .messages-container::-webkit-scrollbar {
    width: 8px;
  }

  .messages-container::-webkit-scrollbar-track {
    background: rgba(139, 69, 19, 0.2);
    border-radius: 4px;
  }

  .messages-container::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    border-radius: 4px;
  }

  .messages-container::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #f4d03f, #d4af37);
  }

  .system-message {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(184, 134, 11, 0.2));
    border: 1px solid #d4af37;
    border-radius: 15px;
    margin: 0.5rem 0;
    animation: slideIn 0.3s ease-out;
  }

  .system-icon {
    font-size: 1.5em;
    flex-shrink: 0;
  }

  .system-text {
    color: #f4e4bc;
    font-style: italic;
    font-size: 1em;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  }

  .message-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 240, 240, 0.95));
    border: 2px solid #8b4513;
    border-radius: 15px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    animation: slideIn 0.3s ease-out;
    position: relative;
    overflow: hidden;
  }

  .message-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(135deg, #d4af37, #b8860b);
  }

  .message-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.8rem;
  }

  .user-avatar {
    flex-shrink: 0;
  }

  .user-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 3px solid #8b4513;
    transition: all 0.3s ease;
  }

  .message-card:hover .user-avatar img {
    border-color: #d4af37;
    transform: scale(1.05);
  }

  .user-info {
    flex: 1;
  }

  .username {
    font-weight: bold;
    color: #2c1810;
    font-size: 1.1em;
    margin-bottom: 0.2rem;
  }

  .message-time {
    font-size: 0.8em;
    color: #8b4513;
    opacity: 0.8;
  }

  .message-content {
    margin-left: 3rem;
  }

  .message-content p {
    margin: 0;
    color: #2c1810;
    line-height: 1.5;
    font-size: 1em;
  }

  .input-area {
    padding: 1.5rem;
    border-top: 1px solid rgba(139, 69, 19, 0.3);
    background: linear-gradient(135deg, rgba(44, 24, 16, 0.8), rgba(26, 15, 8, 0.9));
  }

  .input-wrapper {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .input-area input {
    flex: 1;
    padding: 1rem 1.5rem;
    border: 2px solid #8b4513;
    border-radius: 25px;
    font-size: 1em;
    background: rgba(255, 255, 255, 0.95);
    color: #2c1810;
    font-family: 'Georgia', serif;
    transition: all 0.3s ease;
    outline: none;
  }

  .input-area input:focus {
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
    background: rgba(255, 255, 255, 1);
  }

  .input-area input::placeholder {
    color: #8b4513;
    opacity: 0.7;
  }

  .send-btn {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    border: 2px solid #8b4513;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
  }

  .send-btn:hover {
    background: linear-gradient(135deg, #f4d03f, #d4af37);
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
  }

  .send-btn:active {
    transform: scale(0.95);
  }

  .send-icon {
    font-size: 1.2em;
    color: #2c1810;
  }

  @media (max-width: 600px) {
    .chat-container {
      border-radius: 15px;
    }

    .chat-header {
      padding: 0.8rem 1rem;
      border-radius: 13px 13px 0 0;
    }

    .chat-header h3 {
      font-size: 1.1em;
    }

    .messages-container {
      padding: 1rem;
      gap: 0.8rem;
    }

    .message-card {
      padding: 0.8rem;
    }

    .message-header {
      gap: 0.8rem;
      margin-bottom: 0.6rem;
    }

    .user-avatar img {
      width: 35px;
      height: 35px;
    }

    .message-content {
      margin-left: 2.5rem;
    }

    .input-area {
      padding: 1rem;
    }

    .input-area input {
      padding: 0.8rem 1.2rem;
      font-size: 0.9em;
    }

    .send-btn {
      width: 45px;
      height: 45px;
    }

    .send-icon {
      font-size: 1.1em;
    }
  }
</style>
