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
    if (isNaN(ms) || ms === null || ms === undefined) {
      console.error(`🕐 formatDuration: Invalid ms value: ${ms}`);
      return "00:00";
    }

    if (ms <= 1000) {
      return "00:00";
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
  let narratorActiveFromBackend = $state(false);
  let timerPausedAt = $state(0);
  let showingProfiles = $state(false);
  let currentProfile = $state(null);
  let profileIndex = $state(0);
  let totalProfiles = $state(0);

  // Narrator block state
  let narratorVisible = $state(false);
  let narratorText = $state("");
  let narratorDisplayText = $state("");
  let narratorAnimating = $state(false);
  let narratorCharIndex = $state(0);
  let narratorTypewriterActive = $state(false);
  let allProfiles = $state([]);
  let profileQueue = $state([]);
  let isDisplayingProfiles = $state(false);
  let profileTimeout = null;
  let loadingProfiles = $state(false);

  let phaseMillisecondsLeft = $derived.by(() => {
    // Simple validation - just check if numbers exist and are valid
    if (!phaseEnd || isNaN(phaseEnd) || !now || isNaN(now)) {
      console.warn(`⚠️ Invalid values: phaseEnd=${phaseEnd}, now=${now}`);
      return 30000; // 30 seconds fallback
    }

    const validTimerPausedAt = timerPausedAt && !isNaN(timerPausedAt) ? timerPausedAt : 0;

    if (narratorActiveFromBackend && validTimerPausedAt > 0) {
      // Timer is paused - return the time that was left when paused
      const pausedTime = Math.max(0, (phaseEnd - validTimerPausedAt) * 1000);

      return pausedTime;
    } else {
      // Timer is running normally
      const normalTime = Math.max(0, (phaseEnd - now) * 1000);

      return normalTime;
    }
  });
  let gameInfo = $derived.by(() => {
    const timeLeft = phaseMillisecondsLeft;
    let nextPhaseText;

    if (isNaN(timeLeft)) {
      nextPhaseText = 'Loading...';
    } else if (timeLeft < 0) {
      nextPhaseText = 'Time up!';
    } else if (timeLeft <= 1000) {
      nextPhaseText = '00:00';
    } else {
      // Use same logic as formatDuration
      const totalSeconds = Math.floor(timeLeft / 1000);
      const seconds = totalSeconds % 60;
      const minutes = Math.floor(totalSeconds / 60) % 60;
      const s = String(seconds).padStart(2, "0");
      const m = String(minutes).padStart(2, "0");
      nextPhaseText = `${m}:${s}`;
    }

    return {
      lobbyCode: lobbyCode,
      nickname: nickname,
      phase: currentPhase,
      uuid: userUuid,
      nextPhase: nextPhaseText,
      winner: winner
    };
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
    // Usuń blokadę timera - pozwól głosować zawsze gdy voting jest aktywny
    console.debug("Selected vote for", option, "phaseTime:", phaseMillisecondsLeft);
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

    ws.onopen = () => {
      console.log('WebSocket connected');
      // Request initial game state after connection
      setTimeout(() => {
        if (userUuid && userUuid !== 'n/a') {
          ws.send(JSON.stringify({ type: 'game.sync_request', player_id: userUuid }));
        }
      }, 500);
    };
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
          const st = event.payload;
          currentPhase = st.phase;

          // Set phaseEnd with validation
          phaseEnd = st.phase_ends_at;
          if (phaseEnd === undefined || phaseEnd === null || isNaN(phaseEnd)) {
            console.error(`🚨 Invalid phaseEnd received: ${phaseEnd}, using fallback`);
            phaseEnd = (Date.now() / 1000) + 30; // Current time + 30 seconds
          }

          // Handle narrator active state
          const wasNarratorActive = narratorActiveFromBackend;
          narratorActiveFromBackend = st.narrator_active || false;



          if (narratorActiveFromBackend && !wasNarratorActive) {
            // Narrator just became active - pause timer
            timerPausedAt = now;
            console.log(`🎭 Timer paused - narrator became active at ${now}, phaseEnd=${phaseEnd}`);
          } else if (!narratorActiveFromBackend && wasNarratorActive) {
            // Narrator just became inactive - resume timer and finish animation
            timerPausedAt = 0;
            console.log(`🎭 Timer resumed - narrator became inactive`);

            // Finish narrator animation if it's still running
            if (narratorAnimating) {
              narratorVisible = false;
              narratorAnimating = false;
              narratorTypewriterActive = false;
              console.log('🎭 Narrator animation finished by backend signal');
            }
          }

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
          showNarratorMessage(event.payload.text, event.payload.duration);
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
  // Sync game state every 5 seconds (reduced from 1 second)
  onMount(() => setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'game.sync_request', player_id: userUuid }));
    }
  }, 5000))

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

  async function showNarratorMessage(text, duration) {
    if (narratorAnimating || showingProfiles) return;

    narratorText = text;
    narratorDisplayText = "";
    narratorCharIndex = 0;
    narratorVisible = true;
    narratorAnimating = true;
    narratorTypewriterActive = true;

    console.log(`🎭 Starting narrator animation for ${duration}s: ${text}`);
    console.log(`🎭 Frontend will NOT auto-finish - waiting for backend narrator_active=false`);

    // Start typewriter effect
    await typewriterEffect(text);

    // Don't auto-finish - wait for backend to set narrator_active=false
    console.log(`🎭 Typewriter finished, waiting for backend to finish narrator...`);
  }

  async function typewriterEffect(text) {
    const typingSpeed = 5; // milliseconds per character (ultra szybkie)

    for (let i = 0; i <= text.length; i++) {
      if (!narratorTypewriterActive) break;

      narratorDisplayText = text.substring(0, i);
      narratorCharIndex = i;

      await new Promise(resolve => setTimeout(resolve, typingSpeed));
    }

    narratorTypewriterActive = false;
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
            <div class="voting-card {votingSelectedByPlayer === option ? 'selected' : ''} {(votingSelectedByOthers[option] ?? 0) > 0 ? 'has-votes' : ''}">
              <button
                class="voting-button"
                onclick={() => {
                  votingSelectHandler(option);
                }}
              >
                <div class="player-info">
                  <img src="https://avatar.iran.liara.run/public?username={option}" alt="{userDisplayNames[option]}'s avatar" class="voting-avatar" />
                  <div class="player-details">
                    <div class="player-name">{userDisplayNames[option]}</div>
                    {#if mafiosi.includes(option)}
                      <div class="player-role mafia">🔪 Mafia</div>
                    {:else if medics.includes(option)}
                      <div class="player-role medic">⚕️ Medic</div>
                    {:else}
                      <div class="player-role citizen">👤 Citizen</div>
                    {/if}
                  </div>
                </div>

                {#if votingSelectedByPlayer === option}
                  <div class="your-vote-indicator">
                    <span class="vote-icon">✓</span>
                    <span class="vote-text">Your Vote</span>
                  </div>
                {/if}

                {#if (votingSelectedByOthers[option] ?? 0) > 0}
                  <div class="others-votes">
                    <div class="vote-count">{votingSelectedByOthers[option]}</div>
                    <div class="vote-dots">
                      {#each Array(Math.min(votingSelectedByOthers[option] ?? 0, 5)) as _, i}
                        <span class="vote-dot">●</span>
                      {/each}
                      {#if (votingSelectedByOthers[option] ?? 0) > 5}
                        <span class="vote-more">+{(votingSelectedByOthers[option] ?? 0) - 5}</span>
                      {/if}
                    </div>
                  </div>
                {/if}
              </button>
            </div>
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
      <div class="narrator-header">
        <div class="narrator-icon">🎭</div>
        <h2>The Narrator Speaks</h2>
      </div>

      <div class="narrator-content">
        <div class="narrator-text">
          {narratorDisplayText}<span class="cursor" class:blinking={narratorTypewriterActive}>|</span>
        </div>
      </div>

      <div class="narrator-footer">
        <div class="story-progress">
          <div class="progress-dots">
            <span class="dot active"></span>
            <span class="dot active"></span>
            <span class="dot active"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
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
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 100;
    backdrop-filter: blur(8px);
    padding: 2rem;
    box-sizing: border-box;
  }

  .chat-timer {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
    padding: 1rem 2rem;
    border-radius: 25px;
    font-weight: bold;
    font-size: 1.5em;
    margin-bottom: 1.5rem;
    border: 3px solid #8b4513;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    font-family: 'Georgia', serif;
    letter-spacing: 1px;
    animation: timerPulse 2s infinite;
  }

  @keyframes timerPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
  }

  .modal :global(.chat-container) {
    max-width: 800px;
    width: 90%;
    max-height: 70vh;
    min-height: 500px;
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
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .voting-header p {
    margin: 0;
    font-size: 1.2em;
    font-weight: bold;
    color: #2c1810;
  }

  .voting-timer {
    margin-left: auto;
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    border: 2px solid #8b4513;
  }

  .voting-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    max-width: 100%;
  }

  .voting-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 240, 240, 0.95));
    border: 2px solid #8b4513;
    border-radius: 15px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .voting-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }

  .voting-card.selected {
    border-color: #d4af37;
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(184, 134, 11, 0.2));
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
  }

  .voting-card.has-votes {
    border-color: #dc143c;
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.1), rgba(178, 34, 34, 0.1));
  }

  .voting-card.selected.has-votes {
    border-color: #ff6347;
    background: linear-gradient(135deg, rgba(255, 99, 71, 0.2), rgba(220, 20, 60, 0.2));
  }

  .voting-button {
    all: unset;
    width: 100%;
    padding: 1rem;
    cursor: pointer;
    display: block;
    position: relative;
  }

  .player-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .voting-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 3px solid #8b4513;
    flex-shrink: 0;
  }

  .voting-card.selected .voting-avatar {
    border-color: #d4af37;
  }

  .player-details {
    flex: 1;
  }

  .player-name {
    font-size: 1.1em;
    font-weight: bold;
    color: #2c1810;
    font-family: 'Georgia', serif;
    margin-bottom: 0.2rem;
  }

  .player-role {
    font-size: 0.9em;
    font-style: italic;
    font-family: 'Georgia', serif;
  }

  .player-role.mafia {
    color: #dc143c;
    font-weight: bold;
  }

  .player-role.medic {
    color: #228b22;
    font-weight: bold;
  }

  .player-role.citizen {
    color: #8b4513;
  }

  .your-vote-indicator {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8em;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    box-shadow: 0 2px 8px rgba(212, 175, 55, 0.4);
  }

  .vote-icon {
    font-size: 1em;
  }

  .vote-text {
    font-family: 'Georgia', serif;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .others-votes {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(139, 69, 19, 0.3);
  }

  .vote-count {
    background: linear-gradient(135deg, #dc143c, #b22222);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-weight: bold;
    font-size: 0.9em;
    min-width: 2rem;
    text-align: center;
  }

  .vote-dots {
    display: flex;
    align-items: center;
    gap: 0.2rem;
    flex: 1;
    justify-content: center;
  }

  .vote-dot {
    color: #dc143c;
    font-size: 1.2em;
    animation: pulse 1.5s infinite;
  }

  .vote-dot:nth-child(2) { animation-delay: 0.3s; }
  .vote-dot:nth-child(3) { animation-delay: 0.6s; }
  .vote-dot:nth-child(4) { animation-delay: 0.9s; }
  .vote-dot:nth-child(5) { animation-delay: 1.2s; }

  .vote-more {
    color: #dc143c;
    font-weight: bold;
    font-size: 0.9em;
    margin-left: 0.3rem;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.1); }
  }

  @media (max-width: 800px) {
    .voting-options {
      grid-template-columns: 1fr;
    }

    .voting-header {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }

    .voting-timer {
      margin-left: 0;
    }
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
    background: rgba(0, 0, 0, 0.95);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(8px);
    animation: fadeIn 0.5s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .narrator-block {
    background: linear-gradient(135deg, #2c1810 0%, #4a2c1a 50%, #1a0f08 100%);
    border: 3px solid #d4af37;
    border-radius: 25px;
    padding: 0;
    max-width: 80%;
    min-width: 600px;
    max-height: 70%;
    overflow: hidden;
    box-shadow:
      0 25px 50px rgba(0, 0, 0, 0.9),
      0 0 30px rgba(212, 175, 55, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    font-family: 'Georgia', serif;
    opacity: 0;
    transform: scale(0.8) translateY(50px);
    transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
  }

  .narrator-block::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 20%, rgba(212, 175, 55, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(139, 69, 19, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }

  .narrator-block.visible {
    opacity: 1;
    transform: scale(1) translateY(0);
  }

  .narrator-header {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #8b4513;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: relative;
  }

  .narrator-header::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background: linear-gradient(90deg, transparent, #2c1810, transparent);
    border-radius: 2px;
  }

  .narrator-icon {
    font-size: 2.5em;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5));
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(5deg); }
  }

  .narrator-header h2 {
    color: #2c1810;
    font-size: 1.8em;
    margin: 0;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    letter-spacing: 1px;
  }

  .narrator-content {
    padding: 3rem;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .narrator-text {
    color: #f4e4bc;
    font-size: 1.4em;
    line-height: 2;
    text-align: center;
    font-style: italic;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    position: relative;
    max-width: 100%;
  }

  .cursor {
    color: #d4af37;
    font-weight: bold;
    font-style: normal;
    animation: blink 1s infinite;
  }

  .cursor.blinking {
    animation: blink 0.8s infinite;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  .narrator-footer {
    background: linear-gradient(135deg, rgba(44, 24, 16, 0.8), rgba(26, 15, 8, 0.9));
    padding: 1.5rem 2rem;
    border-top: 1px solid rgba(212, 175, 55, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .story-progress {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .progress-dots {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: rgba(139, 69, 19, 0.5);
    border: 2px solid #8b4513;
    transition: all 0.3s ease;
  }

  .dot.active {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    border-color: #d4af37;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
  }

  /* Night theme adjustments for narrator */
  :global(body.night) .narrator-block {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1419 100%);
    border-color: #4a5568;
  }

  :global(body.night) .narrator-header {
    background: linear-gradient(135deg, #4a5568, #2d3748);
  }

  :global(body.night) .narrator-header h2 {
    color: #e2e8f0;
  }

  :global(body.night) .narrator-text {
    color: #cbd5e0;
  }

  :global(body.night) .cursor {
    color: #4a5568;
  }

  @media (max-width: 800px) {
    .narrator-block {
      min-width: 90%;
      max-width: 95%;
      margin: 1rem;
    }

    .narrator-header {
      padding: 1rem 1.5rem;
      flex-direction: column;
      text-align: center;
      gap: 0.5rem;
    }

    .narrator-icon {
      font-size: 2em;
    }

    .narrator-header h2 {
      font-size: 1.4em;
    }

    .narrator-content {
      padding: 2rem 1.5rem;
    }

    .narrator-text {
      font-size: 1.2em;
      line-height: 1.8;
    }

    .narrator-footer {
      padding: 1rem;
    }
  }

  @media (max-width: 500px) {
    .narrator-block {
      min-width: 95%;
    }

    .narrator-content {
      padding: 1.5rem 1rem;
    }

    .narrator-text {
      font-size: 1.1em;
    }
  }
</style>
