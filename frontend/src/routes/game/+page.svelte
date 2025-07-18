<script>
  import { onMount, tick } from "svelte";
  import { fade } from "svelte/transition";
  import Chat from "$lib/components/Chat.svelte";
  import LobbyInfo from "$lib/components/LobbyInfo.svelte";
  import UserList from "$lib/components/UserList.svelte";
  import { page } from "$app/state";

  let now = $state(Date.now());
  onMount(() => {
    const id = setInterval(() => {
      now = Date.now();
      gameInfo.nextPhase = votingMillisecondsLeft
    }, 500); // 500 for smoother display
    return () => clearInterval(id);
  });

  // TODO: clean up everything

  /// Game info ///
  let gameInfo = $state({
    lobbyCode: page.params.room_id,
    phase: 'night',
    uuid: 'n/a',
    nextPhase: 0
  });


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
  let chatEnd = $state(Date.now() + 15 * 1000);
  let chatMillisecondsLeft = $derived(Math.max(0, chatEnd - now));
  let showChatModal = $derived(gameInfo.phase === "day" || gameInfo.phase === "lobby");

  let sendMessageHandler = (/** @type {string} */ msgText) => {
    const payload = { actor_id: gameInfo.uuid, timestamp: new Date().toISOString(), 'text': msgText };
    ws.send(JSON.stringify({ type: 'message.send', payload }));
  };

  /// User list ///
  let users = $state(
    Array.from(
      { length: 10 },
      () => "user_" + Math.floor(Math.random() * 10000),
    ),
  );
  let eliminated = $state([
    users[0],
    users[3]
  ]);
  let mafiosi = $state([
    users[2],
    users[3]
  ]);

  /// Voting ///
  let showVoting = $derived(gameInfo.phase === "voting");

  let votingPrompt = $state("Eliminate user?");
  let votingOptions = $state([
    "user_0123",
    "user_1234",
    "user_6789",
    "user_5555",
  ]);
  let votingEnd = $state(Date.now() + 30 * 1000);
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

  ///////////////
  // Websocket //
  ///////////////
  let ws;

  let display_names_per_id = $state({})

  function connect() {
    const roomId = page.url.searchParams.get('room_id');
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${protocol}://localhost:8000/ws/${roomId}`);

    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = async (evt) => {
      const event = JSON.parse(evt.data);
      console.debug(event)
      switch (event.type) {
        case 'player.uuid':
          gameInfo.uuid = event.payload.uuid
          const payload = { player_id: gameInfo.uuid, name: "hello its me" };
          ws.send(JSON.stringify({ type: 'player.join', payload }));
          console.log('sent hello!')
          break;

        case 'game.state':
          console.log('received game state')
          const st = event.payload;
          gameInfo = { lobbyCode: roomId, phase: st.phase, uuid: gameInfo.uuid };
          let phaseEnd = (new Date(st.logs[st.logs.length-1]?.timestamp || Date.now()).getTime());
          votingEnd = phaseEnd
          chatEnd = phaseEnd
          
          console.log('mapping users')

          // @ts-ignore
          users = st.players.map(p => p.name);
          display_names_per_id = st.players.map(p => ({[p.player_id]: p.name}));
          // @ts-ignore
          eliminated = st.players.filter(p => !p.alive).map(p => p.player_id);
          // if mafia reveal
          // @ts-ignore
          mafiosi = st.players.filter(p => p.role_revealed === 'mafia').map(p => p.player_id);
          break;

        case 'message.received':
          // TODO: make it work better with the component
          messages.push({ id: Date.now(), user: display_names_per_id[event.payload.actor_id], text: event.payload.text });
          break;

        case 'action.morning_news':
        case 'action.evening_news':
          // show news in stream
          addTextToStream({ id: Date.now(), text: `Player ${event.payload.target_id} eliminated.` });
          break;

        case 'action.vote_cast':
          const { actor_id, target_id } = event.payload;
          if (actor_id !== gameInfo.uuid) {
            votingSelectedByOthers[target_id] = (votingSelectedByOthers[target_id] || 0) + 1;
          }
          break;

        case 'phase.change':
          gameInfo['phase'] = event.payload.phase;
          chatEnd = votingEnd = new Date(event.payload.ends_at).getTime();
          if (showVoting) {
            votingPrompt = 'Eliminate user?';
            votingOptions = users.filter(u => !eliminated.includes(u));
            votingSelectedByOthers = {};
            votingSelectedByPlayer = '';
          }
          break;

        default:
          console.warn('Unhandled event', event.type);
      }
    };
    ws.onclose = () => console.log('WebSocket disconnected');
  }

  onMount(connect)

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
    <h1 class="chat-timer">{formatDuration(chatMillisecondsLeft)}</h1>
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
      <UserList {users} {mafiosi} {eliminated}/>
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
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }

  .chat-timer {
    margin-bottom: 0;
    padding-bottom: 0;
    color: #f0f0f0;
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
