<script>
  import { onMount } from 'svelte';

  let { text = '', speed = 50 } = $props(); // milliseconds per word

  let displayedText = $state('');
  let isAnimating = $state(false);
  let lastText = $state('');
  let animationComplete = $state(false);

  let words = $derived(text.split(' '));

  $effect(() => {
    if (text && text !== lastText && !isAnimating) {
      lastText = text;
      animationComplete = false;
      startAnimation();
    }
  });
  
  function startAnimation() {
    if (!text || isAnimating || animationComplete) return;

    isAnimating = true;
    displayedText = '';

    let currentWordIndex = 0;

    const interval = setInterval(() => {
      if (currentWordIndex < words.length) {
        if (currentWordIndex === 0) {
          displayedText = words[currentWordIndex];
        } else {
          displayedText += ' ' + words[currentWordIndex];
        }
        currentWordIndex++;
      } else {
        clearInterval(interval);
        isAnimating = false;
        animationComplete = true;
      }
    }, speed);
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
