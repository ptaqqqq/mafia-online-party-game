<script>
  import { onMount, tick } from "svelte";
  import { fade } from "svelte/transition";
  import Chat from "$lib/components/Chat.svelte";
  import LobbyInfo from "$lib/components/LobbyInfo.svelte";
  import UserList from "$lib/components/UserList.svelte";
  import { page } from "$app/state";


  let now = $state(Date.now() / 1000.0);  // in seconds to match Python code
  onMount(() => {
    const id = setInterval(() => {
      now = Date.now() / 1000.0;
    }, 500); // 500 for smoother display
    return () => clearInterval(id);
  });

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


  /// Game info ///
  let lobbyCode = page.params.room_id;
  let currentPhase = $state('lobby');
  let userUuid = $state('n/a')
  let phaseEnd = $state(Date.now() / 1000.0);
  let winner = $state('n/a')

  let phaseMillisecondsLeft = $derived((phaseEnd - now) * 1000);
  let gameInfo = $derived({
    lobbyCode: lobbyCode,
    phase: currentPhase,
    uuid: userUuid,
    nextPhase: phaseMillisecondsLeft,
    winner: winner
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
  /**
     * @type {{ id: number; user: string; text: string; }[]}
     */
  let messages = $state([]);
  let showChatModal = $derived(currentPhase === "day" || currentPhase === "lobby");

  let sendMessageHandler = (/** @type {string} */ msgText) => {
    const payload = { actor_id: userUuid, timestamp: now, 'text': msgText };
    ws.send(JSON.stringify({ type: 'message.send', payload }));
  };


  /// User list ///
  let users = $state(
    Array.from(
      { length: 10 },
      () => "user_" + Math.floor(Math.random() * 10000),
    ),
  );
  /**
    * @type {string[]}
    */
  let eliminated = $state([]);
  /**
    * @type {string[]}
    */
  let mafiosi = $state([]);


  /// Voting ///
  let showVoting = $derived(currentPhase === "voting" || (currentPhase === "night" && mafiosi.includes(userUuid)));
  let votingPrompt = $derived.by(() => {
    if (currentPhase === "voting") {
      return "Who is the most suspicious?";
    } else {
      return "Choose your target wisely...";
    }
  });
  /**
     * @type {string[]}
     */
  let votingOptions = $derived(users.filter(p => !eliminated.includes(p)));
  let votingSelectedByPlayer = $state("");
  /** @type {Record<string, number>} */
  let votingSelectedByOthers = $state({});
  const votingSelectHandler = (/** @type {any} */ option) => {
    if (phaseMillisecondsLeft > 0) {
      console.debug("Selected vote for", option);
      votingSelectedByPlayer = option;
      if (currentPhase === 'voting') {
        const payload = { actor_id: userUuid, target_id: option };
        ws.send(JSON.stringify({ type: 'action.vote', payload }));
      } else if (currentPhase === 'night') {
        const payload = { actor_id: userUuid, action: 'kill', target_id: option };
        ws.send(JSON.stringify({ type: 'action.night', payload }));
      }
    }
  };``


  ///////////////
  // Websocket //
  ///////////////
  /**
    * @type {WebSocket}
    */
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
          userUuid = event.payload.uuid
          const payload = { player_id: userUuid, name: "hello its me" };
          ws.send(JSON.stringify({ type: 'player.join', payload }));
          console.log('sent hello!')
          break;

        case 'game.state':
          console.log('received game state')
          const st = event.payload;

          currentPhase = st.phase;
          phaseEnd = st.phase_ends_at;
          if (st.winner) {
            winner = st.winner
          }
          const st_users = st.players;
          const st_votes = st.votes;

          // TODO: switch to displaying player names instead of UUIDs
          // @ts-ignore
          users = st_users.map(p => p.player_id);
          // @ts-ignore
          mafiosi = st_users.filter(p => p.role_revealed === 'mafia').map(p => p.player_id);
          // @ts-ignore
          eliminated = st_users.filter(p => p.alive === false).map(p => p.player_id);
          
          if (st_votes) {
            if (st_votes[userUuid]) {
              votingSelectedByPlayer = st_votes[userUuid];
            } else {
              votingSelectedByPlayer = '';
            }

            Object.entries(st_votes).forEach(([actorId, targetId]) => {
              if (actorId === userUuid) return;
              users.forEach(p => votingSelectedByOthers[p] = 0);
              votingSelectedByOthers[targetId] = (votingSelectedByOthers[targetId] || 0) + 1;
            });
          } else {
            users.forEach(p => votingSelectedByOthers[p] = 0)
          }
          break;

        case 'message.received':
          // TODO: autoscroll
          messages.push({ id: Date.now(), user: event.payload.actor_id, text: event.payload.text });
          break;

        case 'action.morning_news':
          addTextToStream({ id: Date.now(), text: `Player ${event.payload.target_id} has been killed by the mafia.` });
          break;
        case 'action.evening_news':
          addTextToStream({ id: Date.now(), text: `Player ${event.payload.target_id} has been voted off.` });
          break;

        case 'action.vote_cast':
          const { actor_id, target_id } = event.payload;
          if (actor_id !== userUuid) {
            // votingSelectedByOthers[target_id] = (votingSelectedByOthers[target_id] || 0) + 1;
          }
          break;

        case 'phase.change':
          currentPhase = event.payload.phase;
          phaseEnd = event.payload.phase_ends_at;
          break;

        default:
          console.warn('Unhandled event', event.type);
      }
    };
    ws.onclose = () => console.log('WebSocket disconnected');
  }

  onMount(connect)
  onMount(() => setInterval(() => {
    ws.send(JSON.stringify({ type: 'game.sync_request', playerId: userUuid }));
  }, 1000))
</script>

{#if showChatModal}
  <div class="modal">
    <h1 class="chat-timer">{formatDuration(phaseMillisecondsLeft)}</h1>
    <Chat {messages} {sendMessageHandler} />
  </div>
{/if}

<main>
  <div class="main-area">
    <div class="lobby-info overlay">r
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
            <p class="voting-timer">{formatDuration(phaseMillisecondsLeft)}</p>
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
