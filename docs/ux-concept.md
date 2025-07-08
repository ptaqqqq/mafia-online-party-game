# Mafia in Chat – Koncepcja Produktu

**Mafia in Chat** to przeglądarkowa imprezówka dla znajomych:  
wchodzisz bez zakładania konta, wrzucasz link do czatu grupowego, tworzysz lobby w stylu Among Us i już po kilku kliknięciach jesteś w kultową grze. Dodatkowa otoczka fabularna jest generowana przez streaming krótkich opisów generowanych przez LLM, host ma pełną kontrolę nad ustawieniami/stylem rozgrywki, a gra działa zarówno na desktopie, jak i na telefonach.

## Główne flow użytkownika
1. **Wejście do gry**  
   - Ekran powitalny: wpisz nick, "Stwórz lobby" lub "Dołącz po kodzie"  
   - Guest-only, zero rejestracji.

2. **Lobby**  
   - Lista graczy + prosty czat (filtr wulgaryzmów).  
   - Ustawienia hosta:  
     - motyw (prowincja/miasto/kosmos/itp.),
     - czas na decyzję (domyślnie 60 s),
     - max graczy (5–12).  
   - Join in-flight: rola "obserwator" (bez prawa głosu).

3. **Rozgrywka**  
   - **Fazy**: noc (LLM opisuje akcje mafii), dzień (głosowanie).  
   - **Tekst**: streaming 2–3 zdania, auto-scroll w terminalowym okienku.  
   - **Głosowanie**:  
     - lista żywych graczy + timer,
     - automatyczne po upływie czasu,
     - dodatkowe kick-vote w dowolnym momencie.
   - Czat dostępny tylko w fazie dziennej.

4. **Eliminacja**  
   - Animacja + efekt dźwiękowy.  
   - Nekrolog: "Jan Kowalski został wyeliminowany – był ..."
   - Pasek statusu: ikony wszystkich żywych graczy.

5. **Koniec gry & podsumowanie**  
   - Generujemy 3–5 akapitów w stylu "Gazeta Wiejska" lub "Galactic Times".  
   - Dodajemy smaczki: najlepszy detektyw, top-bluffer.  
   - Przyciski:  
     - "Udostępnij link"
     - "Zachowaj w plikach"
     - "Share to social"

## Kluczowe ekrany

| Ekran            | Elementy UI                                                                         |
|------------------|-------------------------------------------------------------------------------------|
| **Landing**      | logo + input nick + dwa buttony (New Game / Join Game)                              |
| **Lobby**        | lista nicków (awatar+status), czat, settings panel (host only), "Start"             |
| **Game View**    | terminal-style box (streaming tekstu), dynamiczne opcje wyboru, pasek graczy, timer |
| **Vote Modal**   | over-screen modal: lista graczy + timer + confirm                                   |
| **Podsumowanie** | artykuł z motywem, akapity, staty (badges), share button                            |

## Mechaniki i reguły
- **Role**: domyślnie ukryte (opcja otwartych przy tworzeniu gry).  
- **Głosowanie**: automatyczne po czasie; kick-vote niezależne.  
- **Obserwatorzy**: brak wpływu na głosowania.  
- **Czat**: tylko w fazie dziennej; nowi joinerzy nie widzą historii.

## 5. Personalizacja i motywy
- **Free**: prowincja, miasto, kosmos, żegluga, wypad w góry.  
- Unikalne tła + doodle w headerze.  
- Auto-switch trybu jasny/ciemny wg lokalnej pory dnia.

## Zaangażowanie
- **Badges & osiągnięcia**:  
  - Detektyw tygodnia (najwięcej trafnych głosów)  
  - Passa zwycięstw (np. 3+ wygranych z rzędu)  
  - Host pass (prowadzenie x sesji)
- **Monetyzacja**: in-app purchases motywów (0,99 $).  
- **Retention hack**: opcjonalne powiadomienia push/mail.

## Tech & Performance
- Lekki LLM mini/lite: szybki turnaround (< 2 s).  
- **Prefetch**: po turze N–1 generujemy treść na turę N.  
- Fallback loader + komunikat "LLM śni... zaraz wracam".

## MVP vs Roadmap

| Feature                              | MVP 1.0 | 1.1+                     |
|--------------------------------------|:-------:|--------------------------|
| Lobby + guest nick                   | ✅      | –                        |
| Klasyczne role + day/night + vote    | ✅      | –                        |
| Motywy free + auto-theme switch      | ✅      | –                        |
| Streaming tekstu + auto-scroll       | ✅      | –                        |
| Podsumowanie artykułem               | ✅      | –                        |
| Badges & stats                       | ✅      | –                        |
| In-app zakupy motywów                | –       | ✅                       |
| PWA / offline LAN                    | –       | ✅                       |
| Screen reader / accessibility        | –       | ✅                       |
