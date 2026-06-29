# Sviluppo futuro

## Fase attuale

La serie 0.4 aggiunge il consenso comando.

La centralina ora calcola anche:

- target mandata comandabile;
- motivo target non comandabile.

Non pilota ancora il PID reale.

## Prossime fasi

### v0.5

ESPHome in lettura e log, mantenendo fallback locale.

### v0.6

Uso del target Home Assistant come setpoint del PID solo quando il consenso e valido.

### v0.7

Azioni su deumidificazione zona giorno e zona notte.

### v0.8

Azioni locali sulle stanze in caso di rischio rugiada.

### v1.0

Centralina attiva stabile: Home Assistant decide la strategia, ESPHome esegue in sicurezza.

## Regole

- Fallback ESPHome sempre presente.
- Sicurezza rugiada sempre prioritaria.
- ACS e standby devono bloccare il comando utile.
- Nessun comando attivo senza consenso esplicito.
