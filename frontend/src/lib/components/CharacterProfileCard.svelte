<script>
  import AnimatedText from './AnimatedText.svelte';

  let { profile = null, visible = false, currentIndex = 1, totalCount = 4 } = $props();
  
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
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .profile-overlay.visible {
    opacity: 1;
  }
  
  .profile-card {
    background: linear-gradient(135deg, #2c1810 0%, #1a0f08 100%);
    border: 2px solid #8b4513;
    border-radius: 20px;
    padding: 40px;
    max-width: 500px;
    width: 90%;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8);
    transform: scale(0.8);
    transition: all 0.4s ease;
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
    margin-bottom: 30px;
    border-bottom: 1px solid #8b4513;
    padding-bottom: 15px;
  }
  
  .profile-header h2 {
    color: #d4af37;
    font-size: 1.2em;
    margin: 0;
    font-family: 'Georgia', serif;
  }
  
  .profile-counter {
    background: #8b4513;
    color: white;
    padding: 5px 15px;
    border-radius: 15px;
    font-weight: bold;
    font-size: 0.9em;
  }
  
  /* Profession emoji */
  .profile-emoji {
    font-size: 4em;
    margin-bottom: 20px;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5));
  }
  
  .profile-name {
    color: #f4f4f4;
    font-size: 2.5em;
    margin: 0 0 10px 0;
    font-family: 'Georgia', serif;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  }
  
  .profile-profession {
    color: #d4af37;
    font-size: 1.4em;
    margin: 0 0 25px 0;
    font-style: italic;
    text-transform: uppercase;
    letter-spacing: 2px;
  }
  
  .profile-description {
    color: #cccccc;
    font-size: 1.1em;
    line-height: 1.6;
    margin: 0 0 30px 0;
    font-family: 'Georgia', serif;
    text-align: left;
    background: rgba(0, 0, 0, 0.3);
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #d4af37;
  }
  
  .profile-progress {
    margin-top: 20px;
  }
  
  .progress-bar {
    width: 100%;
    height: 6px;
    background: rgba(139, 69, 19, 0.3);
    border-radius: 3px;
    overflow: hidden;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #d4af37, #f4d03f);
    border-radius: 3px;
    transition: width 0.5s ease;
  }
  
  @media (max-width: 600px) {
    .profile-card {
      padding: 20px;
      margin: 20px;
    }
    
    .profile-name {
      font-size: 2em;
    }
    
    .profile-emoji {
      font-size: 3em;
    }
    
    .profile-header h2 {
      font-size: 1em;
    }
  }
</style>