<script>
  import { onMount, tick } from 'svelte';
  import Chat from '$lib/components/Chat.svelte'
    import { fade } from 'svelte/transition';

  let messages = $state([
    { 'id': 1, 'user': 'user_1234', 'text': 'Hello, world!' }
  ]);
  let showChatModal = $state(true);

  let streamedText = $state([
    { 'id': 1, 'text': 'Lorem ipsum dolor sit amet.' },
    { 'id': 2, 'text': 'Wlazł kotek na płotek.' },
    { 'id': 3, 'text': 'Litwo, ojczyzno moja.' },
    { 'id': 4, 'text': 'To be or not to be.' }
  ]);
  /**
    * @type {HTMLDivElement}
    */
  let textStream;

  /**
    * @param {{ id: number; text: string; }} textObj
    */
   export async function addTextToStream(textObj) {
    streamedText.push(textObj);
    tick();
    scrollToBottom(textStream);
  }

  onMount(() => scrollToBottom(textStream))

  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
  }

  let sendMessageHandler = (/** @type {string} */ msgText) => {
    messages.push({ 'id': Date.now(), 'user': 'me', 'text': msgText });
    addTextToStream({ 'id': Date.now(), 'text': msgText });
  };
</script>

{#if showChatModal}
  <div class="modal">
    <Chat {messages} {sendMessageHandler} />
  </div>
{/if}

<main>
  <div class="text-stream overlay" bind:this={textStream}>
    <h1>Game Theme</h1>
    {#each streamedText as streamed (streamed.id)}
      <div class="text-stream-element" transition:fade >
        <p>{streamed.text}</p>
      </div>
    {/each}
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

  main {
    display: flex;
    flex-direction: row;
    height: 90%;
    padding: 1rem;
    margin: 1rem;
  }

  .text-stream {
    display: flex;
    flex-direction: column;
    overflow-y: hidden;
    max-height: 100%;
    max-width: 50%;
  }
</style>
