<script>
  import { onMount, tick } from "svelte";
  import { fade } from "svelte/transition";
  import Chat from "$lib/components/Chat.svelte";
  import LobbyInfo from "$lib/components/LobbyInfo.svelte";
  import UserList from "$lib/components/UserList.svelte";

  /// Text stream ///
  let streamedText = $state([
    { id: 1, text: "Lorem ipsum dolor sit amet." },
    { id: 2, text: "Wlazł kotek na płotek." },
    { id: 3, text: "Litwo, ojczyzno moja." },
    { id: 4, text: "To be or not to be." },
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

  onMount(() => {
    scrollToBottom(textStream)
    window.addEventListener('resize', () => { scrollToBottom(textStream) });
  });

  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: "smooth" });
  };

  /// Chat modal ///
  let messages = $state([{ id: 1, user: "user_1234", text: "Hello, world!" }]);
  let showChatModal = $state(false);

  let sendMessageHandler = (/** @type {string} */ msgText) => {
    messages.push({ id: Date.now(), user: "me", text: msgText });
    // TODO: Debug only, disable later
    addTextToStream({ id: Date.now(), text: msgText });
  };

  /// Game info ///
  let gameInfo = $state({
    lobbyCode: "ABCDEF",
    day: 3,
    hour: "3:00 am",
  });

  /// User list ///
  let users = $state(
    Array.from(
      { length: 10 },
      () => "user_" + Math.floor(Math.random() * 10000),
    ),
  );

  /// Voting ///
  let showVoting = $state(true);

  let votingPrompt = $state("Eliminate user?");
  let votingOptions = $state([
    "user_0123",
    "user_1234",
    "user_6789",
    "user_5555",
  ]);
  let votingEnd = $state(Date.now() + 15 * 1000);

  let now = $state(Date.now());
  onMount(() => {
    const id = setInterval(() => {
      now = Date.now();
    }, 500); // 500 for smoother display
    return () => clearInterval(id);
  });
  let votingMillisecondsLeft = $derived(Math.max(votingEnd - now, 0));

  let votingSelectedByPlayer = $state("");
  /** @type {Record<string, number>} */
  let votingSelectedByOthers = $state({
    user_0123: 2,
    user_5555: 1,
  });

  const votingSelectHandler = (/** @type {any} */ option) => {
    if (votingMillisecondsLeft > 0) {
      console.debug("Selected vote for", option);
      votingSelectedByPlayer = option;
    }
  };

  /**
   * @param {number} ms
   */
  function formatDuration(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const seconds = totalSeconds % 60;
    const totalMinutes = Math.floor(totalSeconds / 60);
    const minutes = totalMinutes % 60;
    const hours = Math.floor(totalMinutes / 60);

    // pad to 2 digits:
    const s = String(seconds).padStart(2, "0");
    const m = String(minutes).padStart(2, "0");
    const h = String(hours).padStart(2, "0");

    return hours ? `${h}:${m}:${s}` : `${m}:${s}`;
  }
</script>

{#if showChatModal}
  <div class="modal">
    <Chat {messages} {sendMessageHandler} />
  </div>
{/if}

<main>
  <div class="main-area">
    <div class="lobby-info overlay">
      <LobbyInfo lobbySettings={gameInfo} />
    </div>
    <div class="text-stream overlay" bind:this={textStream}>
      <h1>Game Theme</h1>
      {#each streamedText as streamed (streamed.id)}
        <div class="text-stream-element" transition:fade>
          <p>{streamed.text}</p>
        </div>
      {/each}

      {#if showVoting}
        <div class="voting-container">
          <div class="voting-header">
            <p><strong>{votingPrompt}</strong></p>
            <p class="voting-timer">{formatDuration(votingMillisecondsLeft)}</p>
          </div>
          <div class="voting-options">
          {#each votingOptions as option}
            <button
              class="voting-button"
              onclick={() => {
                votingSelectHandler(option);
              }}
            >
              {#each Array(votingSelectedByOthers[option] ?? 0) as _, i}
                <span>[</span>
              {/each}

              {#if votingSelectedByPlayer === option}
                <span>(</span>
              {/if}

              {option}

              {#if votingSelectedByPlayer === option}
                <span>)</span>
              {/if}

              {#each Array(votingSelectedByOthers[option] ?? 0) as _, i}
                <span>]</span>
              {/each}
            </button>
          {/each}
        </div>
        </div>
      {/if}
    </div>

    <div class="user-list overlay">
      <UserList {users} />
    </div>
  </div>
</main>

<style>
  :global(body) {
    background: url("/city-theme-bg.png") center/cover no-repeat;
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
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
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
        /* left  */
        20vw
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

  .text-stream {
    display: flex;
    flex-direction: column;
    overflow-y: hidden;
    overflow-x: hidden;
    height: 80%;
    max-height: 100%;
    max-width: 100%;
    padding: 2rem;
  }

  .voting-container {
    margin-top: auto;
  }

  .voting-header {
    display: flex;
    max-width: 100%;
  }

  .voting-timer {
    margin-left: auto;
  }

  .voting-options {
    display: flex;
    flex-flow: row wrap;
    max-width: 100%;
    gap: 1rem;
    row-gap: 0rem;
  }

  .voting-options button {
    all: unset;            /* reset every built‑in style */
    display: inline;       /* behave like a <span> */
    font: inherit;         /* use the parent's font settings */
    color: inherit;        /* use the parent's text color */
    cursor: pointer;       /* still look clickable */
    font-weight: 500;
  }

  .voting-options button:hover {
    font-weight: bolder;
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
</style>
