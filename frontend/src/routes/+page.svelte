<script>
    let username = $state('user_' + Math.floor(Math.random() * 10000));

    function join_lobby() {
        console.log('User choose to join an exisiting lobby')
    }

    function create_lobby() {
        console.log('User choose to create a new lobby')
    }
</script>

<h1>Play Mafia Online!</h1>

<div id="container">
  <div id="top">
    <input type="text" bind:value={username} />
  </div>
  <div id='bottom'>
    <button onclick={join_lobby}>Join lobby</button>
    <button onclick={create_lobby}>Create lobby</button>
  </div>
</div>

<style>
</style>
