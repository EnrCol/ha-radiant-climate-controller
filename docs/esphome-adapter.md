# ESPHome adapter

## Stato attuale

La serie 0.4 espone il consenso comando per ESPHome, ma non pilota ancora il PID reale.

Home Assistant fornisce:

```text
target mandata consigliato
consenso a usare il target
motivo del consenso o del blocco
```

ESPHome deve sempre mantenere una curva locale di fallback.

## Entita v0.4

```text
sensor.centralina_radiante_target_mandata_consigliato
binary_sensor.centralina_radiante_target_mandata_comandabile
sensor.centralina_radiante_motivo_target_non_comandabile
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

## Import ESPHome previsto

```yaml
sensor:
  - platform: homeassistant
    id: target_mandata_ha
    entity_id: sensor.centralina_radiante_target_mandata_consigliato
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
target che verrebbe usato
```

Il PID continua a usare la logica attuale.

## Comando reale futuro

Quando passeremo al comando reale, ESPHome dovra usare il target HA solo se il consenso e on e il valore e nel range sicuro.

Se HA non risponde, se il target manca o se il consenso e off, ESPHome resta sulla curva locale.

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
