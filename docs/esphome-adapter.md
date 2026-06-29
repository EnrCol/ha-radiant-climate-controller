# ESPHome adapter

## Stato attuale

La serie 0.4 espone il consenso comando per ESPHome, ma non pilota ancora il PID reale.

Home Assistant fornisce:

```text
target mandata consigliato
consenso a usare il target
motivo del consenso o del blocco
heartbeat comando HA
```

ESPHome deve sempre mantenere una curva locale di fallback.

## Entita v0.4.1

```text
sensor.centralina_radiante_target_mandata_consigliato
binary_sensor.centralina_radiante_target_mandata_comandabile
sensor.centralina_radiante_motivo_target_non_comandabile
sensor.centralina_radiante_heartbeat_comando_ha
```

Il binary sensor e on solo con condizioni sicure:

```text
Estate attiva
stato manuale auto
stato radiante noto
target disponibile
target tra 17 C e 23 C
ACS non attiva
standby porte non attivo
protezione rugiada globale non attiva
nessuna protezione locale rugiada prioritaria
```

L heartbeat deve cambiare regolarmente. Se non cambia per alcuni minuti, ESPHome deve ignorare il target HA e usare la curva locale.

## Import ESPHome previsto

```yaml
sensor:
  - platform: homeassistant
    id: target_mandata_ha
    entity_id: sensor.centralina_radiante_target_mandata_consigliato
    internal: true

  - platform: homeassistant
    id: heartbeat_comando_ha
    entity_id: sensor.centralina_radiante_heartbeat_comando_ha
    internal: true

binary_sensor:
  - platform: homeassistant
    id: target_mandata_ha_comandabile
    entity_id: binary_sensor.centralina_radiante_target_mandata_comandabile
    internal: true
```

## Fase log-only

Prima del comando reale, ESPHome deve solo leggere e loggare:

```text
target curva locale
target HA
consenso HA
heartbeat HA fresco
target che verrebbe usato
```

Il PID continua a usare la logica attuale.

## Comando reale futuro

Quando passeremo al comando reale, ESPHome dovra usare il target HA solo se:

```text
consenso HA on
heartbeat fresco
target valido nel range sicuro
```

Se HA non risponde, se il target manca, se l heartbeat e vecchio o se il consenso e off, ESPHome resta sulla curva locale.

## Sicurezze locali da mantenere

- range target valido;
- fallback se HA non risponde;
- fallback se sensore target e unavailable;
- blocco ACS se gestito localmente;
- manual override della valvola;
- limite fisico sulla percentuale valvola.

## Semantica valvola

```text
Estate: 100% = piu acqua fredda, 0% = piu ritorno caldo
Inverno: 100% = piu acqua calda, 0% = piu ritorno freddo
```
