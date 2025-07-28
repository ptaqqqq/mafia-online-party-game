<script>
  let {
    users: user_ids = $bindable([]),
    userDisplayNames = $bindable({}),
    eliminated = $bindable([]),
    mafiosi = $bindable([]),
    medics = $bindable([])
  } = $props()

  user_ids.filter(u => !(u in userDisplayNames)).forEach(u => userDisplayNames[u] = u);

  function getRoleIcon(userId) {
    if (mafiosi.includes(userId)) return '🔪';
    if (medics.includes(userId)) return '⚕️';
    return '👤';
  }

  function getRoleText(userId) {
    if (mafiosi.includes(userId)) return 'Mafia';
    if (medics.includes(userId)) return 'Medic';
    return 'Citizen';
  }

  function getUserStatus(userId) {
    if (eliminated.includes(userId)) return 'eliminated';
    if (mafiosi.includes(userId)) return 'mafia';
    if (medics.includes(userId)) return 'medic';
    return 'alive';
  }
</script>

{#each user_ids as u}
  <div class="user-card {getUserStatus(u)}">
    <div class="avatar-container">
      <img src="https://avatar.iran.liara.run/public?username={u}" alt="{userDisplayNames[u]}'s avatar" />
      <div class="role-badge">
        <span class="role-icon">{getRoleIcon(u)}</span>
      </div>
    </div>

    <div class="user-info">
      <div class="user-name">{userDisplayNames[u]}</div>
      <div class="user-role">{getRoleText(u)}</div>
    </div>

    {#if eliminated.includes(u)}
      <div class="status-indicator eliminated-indicator">💀</div>
    {:else}
      <div class="status-indicator alive-indicator">💚</div>
    {/if}
  </div>
{/each}

<style>
  .user-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    margin-bottom: 0.8rem;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 240, 240, 0.95));
    border: 2px solid #8b4513;
    border-radius: 15px;
    transition: all 0.3s ease;
    position: relative;
    backdrop-filter: blur(5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .user-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  }

  .user-card.eliminated {
    opacity: 0.6;
    background: linear-gradient(135deg, rgba(128, 128, 128, 0.8), rgba(96, 96, 96, 0.8));
    border-color: #666;
  }

  .user-card.mafia {
    border-color: #dc143c;
    background: linear-gradient(135deg, rgba(255, 240, 240, 0.95), rgba(255, 220, 220, 0.95));
  }

  .user-card.medic {
    border-color: #228b22;
    background: linear-gradient(135deg, rgba(240, 255, 240, 0.95), rgba(220, 255, 220, 0.95));
  }

  .avatar-container {
    position: relative;
    flex-shrink: 0;
  }

  .user-card img {
    border-radius: 50%;
    width: 48px;
    height: 48px;
    border: 3px solid #8b4513;
    transition: all 0.3s ease;
  }

  .user-card.mafia img {
    border-color: #dc143c;
  }

  .user-card.medic img {
    border-color: #228b22;
  }

  .user-card.eliminated img {
    border-color: #666;
    filter: grayscale(100%);
  }

  .role-badge {
    position: absolute;
    bottom: -5px;
    right: -5px;
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    border: 2px solid #8b4513;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8em;
  }

  .user-card.mafia .role-badge {
    background: linear-gradient(135deg, #8b0000, #dc143c);
    border-color: #dc143c;
  }

  .user-card.medic .role-badge {
    background: linear-gradient(135deg, #006400, #228b22);
    border-color: #228b22;
  }

  .user-card.eliminated .role-badge {
    background: linear-gradient(135deg, #404040, #666);
    border-color: #666;
  }

  .role-icon {
    color: white;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
  }

  .user-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .user-name {
    font-weight: bold;
    font-size: 1.1em;
    color: #2c1810;
    font-family: 'Georgia', serif;
  }

  .user-card.eliminated .user-name {
    color: #666;
    text-decoration: line-through;
  }

  .user-role {
    font-size: 0.9em;
    font-style: italic;
    color: #8b4513;
    font-family: 'Georgia', serif;
  }

  .user-card.mafia .user-role {
    color: #dc143c;
    font-weight: bold;
  }

  .user-card.medic .user-role {
    color: #228b22;
    font-weight: bold;
  }

  .user-card.eliminated .user-role {
    color: #666;
  }

  .status-indicator {
    font-size: 1.2em;
    flex-shrink: 0;
  }

  .eliminated-indicator {
    animation: pulse 2s infinite;
  }

  .alive-indicator {
    animation: heartbeat 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }

  @media (max-width: 600px) {
    .user-card {
      padding: 0.8rem;
      gap: 0.8rem;
    }

    .user-card img {
      width: 40px;
      height: 40px;
    }

    .role-badge {
      width: 20px;
      height: 20px;
      font-size: 0.7em;
    }

    .user-name {
      font-size: 1em;
    }

    .user-role {
      font-size: 0.8em;
    }
  }
</style>