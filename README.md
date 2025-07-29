# Mafia Online

Online Mafia (also known as Werewolf) party game.

Gather at least four people, join the same lobby with a code, and have fun together, no matter where you are!

![Screenshot of the game homepage](https://i.imgur.com/anaFUDq.jpeg)
![Screenshot of the game during night - medic](https://i.imgur.com/SNxtYhS.png)

## Usage

### Play online

<https://mafia.ptaqqqq.hackclub.app>

### Self-host

Put this in `.env`:

```.env
BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_WEBSOCKET_URL=ws://localhost:8000
```

Run `docker compose up --build`.

<div align="center">
  <a href="https://shipwrecked.hackclub.com/?t=ghrm" target="_blank">
    <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/739361f1d440b17fc9e2f74e49fc185d86cbec14_badge.png" 
         alt="This project is part of Shipwrecked, the world's first hackathon on an island!" 
         style="width: 35%;">
  </a>
</div>
