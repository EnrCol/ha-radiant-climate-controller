# Sviluppo futuro

## Fase attuale

La serie 0.3.x osserva la casa e calcola:

- stato radiante;
- target mandata comfort;
- target mandata sicuro;
- target mandata consigliato;
- azione consigliata;
- rischio rugiada.

Non esegue ancora comandi sugli attuatori.

## Prossime fasi

### v0.4

Aggiungere un consenso comando per stabilire quando il target puo essere usato da ESPHome.

### v0.5

Integrare ESPHome in lettura, mantenendo fallback locale.

### v0.6

Usare il target Home Assistant come setpoint del PID solo quando il consenso e valido.

### v0.7

Valutare azioni su deumidificazione zona giorno e zona notte.

### v0.8

Valutare azioni locali sulle stanze, in particolare in caso di rischio rugiada.

### v1.0

Centralina attiva stabile: Home Assistant decide la strategia, ESPHome esegue il controllo locale in sicurezza.

## Regole

- Fallback ESPHome sempre presente.
- Sicurezza rugiada sempre prioritaria.
- ACS e standby devono bloccare il comando utile.
- Nessun comando attivo senza consenso esplicito.
- I package esistenti si semplificano solo dopo validazione della centralina.
