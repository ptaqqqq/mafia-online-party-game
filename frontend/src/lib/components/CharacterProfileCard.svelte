<script>
  import AnimatedText from './AnimatedText.svelte';

  let { profile = null, visible = false, currentIndex = 1, totalCount = 6 } = $props();
  
  let cardElement = $state();
  let animationClass = $state('');

  $effect(() => {
    if (visible && profile) {
      animationClass = 'fade-in';
      setTimeout(() => {
        animationClass = 'visible';
      }, 100);
    } else {
      animationClass = 'fade-out';
    }
  });
</script>

{#if visible && profile}
  <div class="profile-overlay" class:visible>
    <div class="profile-card {animationClass}" bind:this={cardElement}>
      
      <div class="profile-header">
        <h2>Meet the Townspeople</h2>
        <div class="profile-counter">
          {currentIndex} / {totalCount}
        </div>
      </div>

      <div class="profile-content">
        <div class="profile-emoji">
          {profile?.emoji || '👤'}
        </div>

        <h1 class="profile-name">
          {profile?.name || 'Unknown'}
        </h1>

        <h3 class="profile-profession">
          {profile?.profession || 'Citizen'}
        </h3>

        <div class="profile-description">
          <AnimatedText text={profile?.description || ''} />
        </div>
      </div>
      
      <div class="profile-progress">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            style="width: {(currentIndex / totalCount) * 100}%"
          ></div>
        </div>
      </div>
      
    </div>
  </div>
{/if}

<style>
  .profile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.95);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.4s ease;
    backdrop-filter: blur(8px);
  }

  .profile-overlay.visible {
    opacity: 1;
  }

  .profile-card {
    background: linear-gradient(135deg, #2c1810 0%, #4a2c1a 50%, #1a0f08 100%);
    border: 3px solid #d4af37;
    border-radius: 25px;
    padding: 3rem;
    max-width: 600px;
    width: 90%;
    text-align: center;
    box-shadow:
      0 25px 50px rgba(0, 0, 0, 0.9),
      0 0 30px rgba(212, 175, 55, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transform: scale(0.8);
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
  }

  .profile-card::before {
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
  
  .profile-card.fade-in {
    transform: scale(0.8);
    opacity: 0;
  }
  
  .profile-card.visible {
    transform: scale(1);
    opacity: 1;
  }
  
  .profile-card.fade-out {
    transform: scale(0.8);
    opacity: 0;
  }
  
  .profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    border-bottom: 2px solid #d4af37;
    padding-bottom: 1rem;
    position: relative;
  }

  .profile-header::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    border-radius: 2px;
  }

  .profile-header h2 {
    color: #f4e4bc;
    font-size: 1.4em;
    margin: 0;
    font-family: 'Georgia', serif;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    font-weight: bold;
  }

  .profile-counter {
    background: linear-gradient(135deg, #d4af37, #b8860b);
    color: #2c1810;
    padding: 0.6rem 1.2rem;
    border-radius: 20px;
    font-weight: bold;
    font-size: 1em;
    border: 2px solid #8b4513;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .profile-emoji {
    font-size: 5em;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.7));
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  .profile-name {
    color: #f4e4bc;
    font-size: 3em;
    margin: 0 0 0.5rem 0;
    font-family: 'Georgia', serif;
    text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
    font-weight: bold;
    background: linear-gradient(135deg, #f4e4bc, #d4af37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .profile-profession {
    color: #d4af37;
    font-size: 1.6em;
    margin: 0 0 2rem 0;
    font-style: italic;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-family: 'Georgia', serif;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    position: relative;
  }

  .profile-profession::before,
  .profile-profession::after {
    content: '✦';
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: #8b4513;
    font-size: 0.8em;
  }

  .profile-profession::before {
    left: -2rem;
  }

  .profile-profession::after {
    right: -2rem;
  }
  
  .profile-description {
    color: #e8d5b7;
    font-size: 1.2em;
    line-height: 1.8;
    margin: 0 0 2.5rem 0;
    font-family: 'Georgia', serif;
    text-align: left;
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(26, 15, 8, 0.6));
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #8b4513;
    border-left: 6px solid #d4af37;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
    position: relative;
  }

  .profile-description::before {
    content: '"';
    position: absolute;
    top: -10px;
    left: 15px;
    font-size: 3em;
    color: #d4af37;
    font-family: 'Georgia', serif;
    opacity: 0.7;
  }

  .profile-description::after {
    content: '"';
    position: absolute;
    bottom: -20px;
    right: 15px;
    font-size: 3em;
    color: #d4af37;
    font-family: 'Georgia', serif;
    opacity: 0.7;
  }

  .profile-progress {
    margin-top: 2rem;
    position: relative;
  }

  .profile-progress::before {
    content: 'Progress';
    position: absolute;
    top: -1.5rem;
    left: 0;
    color: #d4af37;
    font-size: 0.9em;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .progress-bar {
    width: 100%;
    height: 10px;
    background: linear-gradient(90deg, rgba(139, 69, 19, 0.3), rgba(74, 44, 26, 0.5));
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #8b4513;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #d4af37, #f4d03f, #d4af37);
    border-radius: 6px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
  }

  .progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shimmer 2s infinite;
  }

  @keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
  }
  
  @media (max-width: 600px) {
    .profile-card {
      padding: 2rem;
      margin: 1rem;
      max-width: 95%;
    }

    .profile-name {
      font-size: 2.2em;
    }

    .profile-emoji {
      font-size: 3.5em;
    }

    .profile-header h2 {
      font-size: 1.1em;
    }

    .profile-profession {
      font-size: 1.3em;
      letter-spacing: 2px;
    }

    .profile-profession::before,
    .profile-profession::after {
      display: none;
    }

    .profile-description {
      font-size: 1.1em;
      padding: 1.5rem;
    }

    .profile-counter {
      padding: 0.5rem 1rem;
      font-size: 0.9em;
    }
  }

  @media (max-width: 400px) {
    .profile-card {
      padding: 1.5rem;
    }

    .profile-name {
      font-size: 1.8em;
    }

    .profile-emoji {
      font-size: 3em;
    }

    .profile-header {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }
  }
</style>