# Entità

## Configurazione iniziale

La config flow propone questi default:

```text
season_entity:
  input_select.modalita_stagionale

temperature_entities:
  climate.soggiorno,
  climate.cucina,
  sensor.temperatura_soggiorno,
  sensor.soggiorno_temperature,
  sensor.temperatura_cucina,
  sensor.cucina_temperature

humidity_entities:
  sensor.umidita_media_zona_giorno,
  sensor.umidita_soggiorno,
  sensor.soggiorno_humidity,
  sensor.umidita_cucina,
  sensor.cucina_humidity
```

La temperatura zona giorno usa il massimo dei valori validi.

L'umidità zona giorno usa la media dei valori validi.

## Sensori creati

- Temperatura zona giorno
- Umidità zona giorno
- Punto rugiada zona giorno
- Stato radiante
- Target mandata richiesto
- Target mandata sicuro
- Target mandata finale
- Delta sicurezza rugiada
- Stato stagione
