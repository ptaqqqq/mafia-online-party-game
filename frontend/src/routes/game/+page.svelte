<script>
  import { onMount, tick } from "svelte";
  import { fade } from "svelte/transition";
  import Chat from "$lib/components/Chat.svelte";
  import LobbyInfo from "$lib/components/LobbyInfo.svelte";
  import UserList from "$lib/components/UserList.svelte";
  import { page } from "$app/state";
  import CharacterProfileCard from '$lib/components/CharacterProfileCard.svelte';


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
    if (ms <= 1000) {
      return "Waiting...";
    }

    const totalSeconds = Math.floor(ms / 1000);
    const seconds = totalSeconds % 60;
    const totalMinutes = Math.floor(totalSeconds / 60);
    const minutes = totalMinutes % 60;
    const hours = Math.floor(totalMinutes / 60);


    const s = String(seconds).padStart(2, "0");
    const m = String(minutes).padStart(2, "0");
    const h = String(hours).padStart(2, "0");

    return hours ? `${h}:${m}:${s}` : `${m}:${s}`;
  }


  /// Game info ///
  let lobbyCode = page.url.searchParams.get('room_id');
  let nickname = page.url.searchParams.get('nickname');
  let currentPhase = $state('lobby');
  let userUuid = $state('n/a')
  let lastPhase = $state(Date.now() / 1000.0);
  let phaseEnd = $state(Date.now() / 1000.0);
  let winner = $state('n/a')
  let showingProfiles = $state(false);
  let currentProfile = $state(null);
  let profileIndex = $state(0);
  let totalProfiles = $state(0);

  // Narrator block state
  let narratorVisible = $state(false);
  let narratorText = $state("");
  let narratorDisplayText = $state("");
  let narratorAnimating = $state(false);
  let allProfiles = $state([]);
  let profileQueue = $state([]);
  let isDisplayingProfiles = $state(false);
  let profileTimeout = null;
  let loadingProfiles = $state(false);

  let phaseMillisecondsLeft = $derived(Math.max(0, (phaseEnd - now) * 1000));
  let gameInfo = $derived({
    lobbyCode: lobbyCode,
    nickname: nickname,
    phase: currentPhase,
    uuid: userUuid,
    nextPhase: '' + Math.round(phaseMillisecondsLeft / 1000) + ' s',
    winner: winner
  });

  /// User list ///
  /**
     * @type {string[]}
     */
  let users = $state([]);
  /**
    * @type {string[]}
    */
  let eliminated = $state([]);
  /**
    * @type {string[]}
    */
  let mafiosi = $state([]);
  /**
    * @type {string[]}
    */
  let medics = $state([]);



  /// Text stream ///
  let streamedText = $state([
    { id: 1, text: "Game will start automatically once at least four players join." },
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
    streamedText = streamedText;
    tick();
    scrollToBottom(textStream);
  }
  onMount(() => {
    scrollToBottom(textStream)
    window.addEventListener('resize', () => { scrollToBottom(textStream) });
  });
  onMount(() => setInterval(() => {
    // dirty hack just in case
    scrollToBottom(textStream);
  }, 2000))
  // @ts-ignore
  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: "smooth" });
  };


  /// Chat modal ///
  /**
     * @type {{ id: number; user: string; text: string; }[]}
     */
  let messages = $state([]);
  let showChatModal = $derived((currentPhase === "day") && !(eliminated.includes(userUuid)) && (now - lastPhase > 10.0) && !narratorAnimating);

  let chatInstance = $state();

  let sendMessageHandler = (/** @type {string} */ msgText) => {
    const payload = { actor_id: userUuid, timestamp: now, 'text': msgText };
    ws.send(JSON.stringify({ type: 'message.send', payload }));
  };


  /// Voting ///
  let showVoting = $derived((currentPhase === "voting" || (currentPhase === "night" && (mafiosi.includes(userUuid) || medics.includes(userUuid)))) && !(eliminated.includes(userUuid)) && !narratorAnimating);
  let votingPrompt = $derived.by(() => {
    if (currentPhase === "voting") {
      return "Who is the most suspicious?";
    } else if (currentPhase === "night" && mafiosi.includes(userUuid)) {
      return "Choose your target to eliminate...";
    } else if (currentPhase === "night" && medics.includes(userUuid)) {
      return "Choose someone to heal and protect...";
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
    if (phaseMillisecondsLeft > 1000) {
      console.debug("Selected vote for", option);
      console.debug("User role check - mafia:", mafiosi.includes(userUuid), "medic:", medics.includes(userUuid));

      // Set selection immediately for all roles to show instant feedback
      votingSelectedByPlayer = option;

      if (currentPhase === 'voting') {
        const payload = { actor_id: userUuid, target_id: option };
        console.debug("Sending voting action:", payload);
        ws.send(JSON.stringify({ type: 'action.vote', payload }));
      } else if (currentPhase === 'night' && mafiosi.includes(userUuid)) {
        const payload = { actor_id: userUuid, action: 'kill', target_id: option };
        console.debug("Sending MAFIA kill action:", payload);
        ws.send(JSON.stringify({ type: 'action.night', payload }));
      } else if (currentPhase === 'night' && medics.includes(userUuid)) {
        const payload = { actor_id: userUuid, action: 'heal', target_id: option };
        console.debug("Sending MEDIC heal action:", payload);
        ws.send(JSON.stringify({ type: 'action.night', payload }));
      } else {
        console.debug("No action sent - phase:", currentPhase, "mafia:", mafiosi.includes(userUuid), "medic:", medics.includes(userUuid));
      }
    }
  };


    /**
     * @param {string | null} message
     */
function showAlert(message, timeout = 3000) {
  const container = document.getElementById('nonBlockingAlerts')
    || Object.assign(document.body.appendChild(document.createElement('div')), {
         id: 'nonBlockingAlerts',
         style: 'position:fixed;top:1rem;right:1rem;display:flex;flex-direction:column;gap:.5rem;z-index:9999;'
       });

  const alert = document.createElement('div');
  alert.className = 'non-blocking-alert';
  alert.textContent = message;
  // click to dismiss early
  alert.addEventListener('click', () => remove(alert));
  container.appendChild(alert);

  // trigger CSS animation
  requestAnimationFrame(() => alert.classList.add('show'));

  // auto‑remove
  const remove = (/** @type {HTMLDivElement} */ el) => {
    el.classList.remove('show');
    el.addEventListener('transitionend', () => el.remove(), { once: true });
  };
  setTimeout(() => remove(alert), timeout);
}



  ///////////////
  // Websocket //
  ///////////////
  /**
    * @type {WebSocket}
    */
  let ws;

  /**
   * @type {Record<string, string>}
   */
  let userDisplayNames = $state({});

  function connect() {
    ws = new WebSocket(`/ws/${lobbyCode}`);

    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = async (evt) => {
      const event = JSON.parse(evt.data);
      console.debug(event)
      switch (event.type) {
        case 'player.uuid':
          userUuid = event.payload.uuid
          const payload = { player_id: userUuid, name: nickname };
          console.log(payload);
          ws.send(JSON.stringify({ type: 'player.join', payload }));
          console.log('sent hello!');
          break;

        case 'player.joined':
          userDisplayNames[event.payload.player_id] = event.payload.name;
          addTextToStream({ id: Date.now(), text: `Player ${event.payload.name} joined the game`});
          break;

        case 'character.profiles_start':
          if (!isDisplayingProfiles) {
            totalProfiles = event.payload.total_count;
            profileQueue = [];
            allProfiles = [];
            loadingProfiles = true;

            addTextToStream({
              id: Date.now(),
              text: `🎭 Preparing character introductions...`
            });
          }
          break;

        case 'character.profile':
          const profile = {
            player_id: event.payload.player_id,
            name: event.payload.name,
            profession: event.payload.profession,
            description: event.payload.description,
            emoji: event.payload.emoji
          };

          profileQueue.push(profile);
          allProfiles.push(profile);

          if (profileTimeout) clearTimeout(profileTimeout);

          if (profileQueue.length === event.payload.total_count) {
            displayProfilesSequentially();
          } else {
            profileTimeout = setTimeout(() => {
              if (profileQueue.length > 0 && !isDisplayingProfiles) {
                displayProfilesSequentially();
              }
            }, 3000);
          }
          break;

        case 'character.profiles_complete':
          if (profileTimeout) {
            clearTimeout(profileTimeout);
            profileTimeout = null;
          }

          if (!isDisplayingProfiles && profileQueue.length > 0) {
            displayProfilesSequentially();
          }

          addTextToStream({
            id: Date.now(),
            text: `✅ All residents have been introduced. The game begins...`
          });
          break;

        case 'player.left':
          addTextToStream({ id: Date.now(), text: `Player ${userDisplayNames[event.payload.player_id] || event.payload.player_id} left the game`});
          delete userDisplayNames[event.payload.player_id];
          users = users.filter(u => u !== event.payload.player_id);
          eliminated = eliminated.filter(u => u !== event.payload.player_id);
          mafiosi = mafiosi.filter(u => u !== event.payload.player_id);
          medics = medics.filter(u => u !== event.payload.player_id);
          break;

        case 'game.state':
          console.log('received game state')
          const st = event.payload;

          currentPhase = st.phase;
          phaseEnd = st.phase_ends_at;

          if (window.pendingPhaseExtension && phaseEnd) {
            phaseEnd += window.pendingPhaseExtension;
            window.pendingPhaseExtension = 0;
          }
          if (st.winner) {
            winner = st.winner
          }
          const st_users = st.players;
          const st_votes = st.votes;

          // @ts-ignore
          users = st_users.map(p => p.player_id);
          // @ts-ignore
          mafiosi = st_users.filter(p => p.role_revealed === 'mafia').map(p => p.player_id);
          // @ts-ignore
          medics = st_users.filter(p => p.role_revealed === 'medic').map(p => p.player_id);
          // @ts-ignore
          eliminated = st_users.filter(p => p.alive === false).map(p => p.player_id);
          userDisplayNames = {};
          // @ts-ignore
          st_users.forEach(p => userDisplayNames[p.player_id] = p.name);
          
          if (st_votes) {
            console.debug("Received votes in game.state:", st_votes);
            if (st_votes[userUuid]) {
              console.debug("Setting votingSelectedByPlayer from game.state:", st_votes[userUuid]);
              votingSelectedByPlayer = st_votes[userUuid];
            } else if (!votingSelectedByPlayer) {
              // Only clear selection if user hasn't made a choice yet
              console.debug("No vote found for user in game.state, clearing selection (only if empty)");
              votingSelectedByPlayer = '';
            } else {
              console.debug("No vote in game.state but user has local selection, keeping:", votingSelectedByPlayer);
            }

            users.forEach(p => votingSelectedByOthers[p] = 0);
            Object.entries(st_votes).forEach(([actorId, targetId]) => {
              if (actorId === userUuid) return;
              votingSelectedByOthers[targetId] = votingSelectedByOthers[targetId] + 1;
            });
          } else {
            users.forEach(p => votingSelectedByOthers[p] = 0)
          }

          setNightTheme(currentPhase === 'night');
          break;

        case 'message.received':
          chatInstance.addMessage({ id: Date.now(), user: userDisplayNames[event.payload.actor_id], text: event.payload.text });
          break;

        case 'narrator.message':
          showNarratorMessage(event.payload.text);
          break;

        case 'action.morning_news':
          // Basic message in main chat + alert
          addTextToStream({ id: Date.now(), text: `Player ${userDisplayNames[event.payload.target_id]} has been killed by the mafia.` });
          showAlert(`Player ${userDisplayNames[event.payload.target_id]} has been killed by the mafia.`);
          break;
        case 'action.evening_news':
          // Basic message in main chat
          addTextToStream({ id: Date.now(), text: `Player ${userDisplayNames[event.payload.target_id]} has been voted off.` });
          break;

        case 'action.vote_cast':
          const { actor_id, target_id } = event.payload;
          console.debug("Received vote_cast:", { actor_id, target_id, userUuid, currentPhase });
          if (actor_id === userUuid) {
            // Update our own selection (for medic heal votes and mafia kill votes)
            console.debug("Updating own selection from", votingSelectedByPlayer, "to", target_id);
            votingSelectedByPlayer = target_id;
            console.debug("Selection updated successfully:", votingSelectedByPlayer);
          } else {
            // votingSelectedByOthers[target_id] = (votingSelectedByOthers[target_id] || 0) + 1;
          }
          break;

        case 'phase.change':
          currentPhase = event.payload.phase;
          lastPhase = phaseEnd;
          phaseEnd = event.payload.phase_ends_at;

          if (window.pendingPhaseExtension && phaseEnd) {
            phaseEnd += window.pendingPhaseExtension;
            window.pendingPhaseExtension = 0;
          }

          // Reset voting selection when phase changes
          votingSelectedByPlayer = "";

          if (currentPhase === 'ended') {
            alert("Game ended!");
            addTextToStream({ id: Date.now(), text: "The game ended. Winner: " + winner + "!" });
          } else if (currentPhase === 'lobby') {
            addTextToStream({ id: Date.now(), text: "Game will start automatically once at least four players join." });
          } else if (currentPhase === 'character_intro') {
            addTextToStream({ id: Date.now(), text: "🎭 Meet the townspeople..." });
          } else {
            // Basic phase announcements in main chat
            addTextToStream({ id: Date.now(), text: "A new " + currentPhase + " began..." });
          }
          scrollToBottom(textStream);
          break;

        default:
          console.warn('Unhandled event', event.type);
      }
    };
    ws.onclose = () => console.log('WebSocket disconnected');
  }

  onMount(connect)
  onMount(() => setInterval(() => {
    ws.send(JSON.stringify({ type: 'game.sync_request', player_id: userUuid }));
  }, 1000))

  /**
     * @param {boolean} night
     */
  function setNightTheme(night) {
    if (night) {
      window.document.body.classList.add('night');
    } else {
      window.document.body.classList.remove('night');
    }
  }

  /**
   * Extend phase time to account for narrator/profile display
   * @param {number} seconds
   */
  function extendPhaseTime(seconds) {
    if (phaseEnd === undefined || isNaN(phaseEnd) || phaseEnd === 0) {
      if (!window.pendingPhaseExtension) window.pendingPhaseExtension = 0;
      window.pendingPhaseExtension += seconds;
      return;
    }

    if (window.pendingPhaseExtension) {
      seconds += window.pendingPhaseExtension;
      window.pendingPhaseExtension = 0;
    }

    phaseEnd += seconds;
  }

  async function displayProfilesSequentially() {
    if (isDisplayingProfiles || profileQueue.length === 0 || narratorAnimating) return;

    isDisplayingProfiles = true;
    loadingProfiles = false;

    for (let i = 0; i < profileQueue.length; i++) {
      const profile = profileQueue[i];
      currentProfile = profile;
      profileIndex = i + 1;
      showingProfiles = true;

      await new Promise(resolve => setTimeout(resolve, 6000));
    }

    showingProfiles = false;
    currentProfile = null;
    isDisplayingProfiles = false;

    ws.send(JSON.stringify({ type: 'opening.story_request' }));

    setTimeout(() => {
      if (!narratorAnimating && !narratorVisible) {
        const fallbackStory = "As darkness falls over the quiet town, the residents lock their doors and draw their curtains. Tonight, secrets will be revealed and alliances tested. The game begins...";
        showNarratorMessage(fallbackStory);
      }
    }, 3000);
  }

  async function showNarratorMessage(text) {
    if (narratorAnimating || showingProfiles) return;

    narratorText = text;
    narratorDisplayText = text;
    narratorVisible = true;
    narratorAnimating = true;

    setTimeout(() => {
      narratorVisible = false;
      narratorAnimating = false;
    }, 15000);
  }
</script>

{#if showChatModal}
  <div class="modal">
    {#if currentPhase !== 'lobby' || (currentPhase === 'lobby' && users.length >= 4)} 
      <h1 class="chat-timer">{formatDuration(phaseMillisecondsLeft)}</h1>
    {/if}
    <Chat bind:this={chatInstance} {messages} {sendMessageHandler} />
  </div>
{/if}

<div id="nonBlockingAlerts"></div>

<main>
  <div class="main-area">
    <div class="lobby-info overlay">
      <LobbyInfo lobbySettings={gameInfo} />
    </div>
    <div class="text-stream overlay" bind:this={textStream}>
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

              {userDisplayNames[option]}

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
      <UserList {users} {mafiosi} {medics} {eliminated} {userDisplayNames}/>
    </div>
  </div>
</main>

<!-- Loading Overlay for Profiles -->
{#if loadingProfiles}
  <div class="loading-overlay">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <h2>🎭 Preparing Character Introductions...</h2>
      <p>Creating unique townspeople for your story...</p>
    </div>
  </div>
{/if}

<CharacterProfileCard
  profile={currentProfile}
  visible={showingProfiles}
  currentIndex={profileIndex}
  totalCount={totalProfiles}
/>

<!-- Narrator Block with Overlay -->
{#if narratorVisible}
  <div class="narrator-overlay">
    <div class="narrator-block" class:visible={narratorVisible}>
      <div class="narrator-text">
        {narratorDisplayText}
      </div>
    </div>
  </div>
{/if}

<style>
  :global(body) {
    background: url("/city-theme-bg.png") center/cover no-repeat;
    margin: 0;
    padding: 0;
    font-family: sans-serif;
    height: 100vh;
    overflow: hidden;
  }

  :global(body.night) {
    background: url("/city-theme-bg-night.png") center/cover no-repeat !important;
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

  #nonBlockingAlerts {
    position: fixed;
    top: 1rem;
    right: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 9999;
  }

  .non-blocking-alert {
    background: #333;
    color: #fff;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.3s ease, transform 0.3s ease;
    cursor: pointer;
  }
  .non-blocking-alert.show {
    opacity: 1;
    transform: translateY(0);
  }

  /* Narrator Overlay */
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(5px);
    z-index: 1000;
  }

  .loading-content {
    text-align: center;
    color: #f4f4f4;
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    border: 2px solid #8b4513;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
  }

  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #8b4513;
    border-top: 4px solid #d4af37;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-content h2 {
    margin: 0 0 10px 0;
    color: #d4af37;
    font-size: 1.5em;
  }

  .loading-content p {
    margin: 0;
    color: #b8860b;
    font-style: italic;
  }

  .narrator-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(3px);
  }

  /* Narrator Block */
  .narrator-block {
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    border: 2px solid #8b4513;
    border-radius: 12px;
    padding: 30px 40px;
    max-width: 70%;
    min-width: 500px;
    max-height: 60%;
    overflow-y: auto;
    box-shadow: 0 8px 25px rgba(0,0,0,0.8);
    font-family: 'Georgia', serif;
    opacity: 0;
    transform: scale(0.9);
    transition: all 0.3s ease;
  }

  .narrator-block.visible {
    opacity: 1;
    transform: scale(1);
  }

  .narrator-block::before {
    content: '🎭';
    position: absolute;
    top: -15px;
    left: 50%;
    transform: translateX(-50%);
    background: #2c1810;
    padding: 8px 12px;
    border-radius: 50%;
    font-size: 1.5em;
    border: 2px solid #8b4513;
  }

  .narrator-text {
    color: #f4e4bc;
    font-size: 1.2em;
    line-height: 1.8;
    text-align: center;
    font-style: italic;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    margin-top: 10px;
    padding: 0 10px;
  }

  /* Night theme adjustments for narrator */
  :global(body.night) .narrator-block {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-color: #4a5568;
  }

  :global(body.night) .narrator-block::before {
    background: #1a1a2e;
  }
</style>
