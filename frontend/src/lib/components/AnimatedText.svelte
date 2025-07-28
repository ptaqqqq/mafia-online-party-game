<script>
  import { onMount } from 'svelte';

  let { text = '', speed = 40, onAnimationComplete = null } = $props(); // milliseconds per character - same as narrator

  let displayedText = $state('');
  let isAnimating = $state(false);
  let lastText = $state('');
  let animationComplete = $state(false);

  $effect(() => {
    if (text && text !== lastText && !isAnimating) {
      lastText = text;
      animationComplete = false;
      startAnimation();
    }
  });

  async function startAnimation() {
    if (!text || isAnimating || animationComplete) return;

    isAnimating = true;
    displayedText = '';

    for (let i = 0; i <= text.length; i++) {
      if (!isAnimating) break; // Allow interruption

      displayedText = text.substring(0, i);
      await new Promise(resolve => setTimeout(resolve, speed));
    }

    console.log('🎭 AnimatedText finished, adding 3s pause...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('🎭 AnimatedText pause completed');

    isAnimating = false;
    animationComplete = true;

    if (onAnimationComplete) {
      onAnimationComplete();
    }
  }

  onMount(() => {
    return () => {
      isAnimating = false;
    };
  });
</script>

<span class="animated-text">
  {displayedText}
  {#if isAnimating}
    <span class="cursor">|</span>
  {/if}
</span>

<style>
  .animated-text {
    display: inline;
  }
  
  .cursor {
    animation: blink 1s infinite;
    color: #d4af37;
    font-weight: bold;
  }
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
</style>
