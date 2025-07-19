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
</script>

<div class="chat-container">
  <div class="messages-container overlay" bind:this={messagesContainer}>
    {#each messages as msg (msg.id)}
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

<style>
  .chat-container {
    width: auto;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: hidden;
    overflow-x: hidden;
    padding: 1rem;
  }
  
  .messages-container {
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
