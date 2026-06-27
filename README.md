# HA Radiant Climate Controller

Custom integration Home Assistant per usare Home Assistant come **centralina climatica radiante** ed ESPHome come **attuatore/PID valvola miscelatrice**.

## Obiettivo

Questa repo non nasce più come semplice package YAML.

L'obiettivo è una integrazione custom installabile in:

```text
/config/custom_components/radiant_climate_controller
```

La logica sarà:

```text
Home Assistant
├── legge temperatura zona giorno
├── legge umidità zona giorno
├── calcola punto di rugiada
├── calcola stato climatico radiante
├── calcola target mandata richiesto
├── applica limite anti-condensa
└── pubblica sensori di controllo

ESPHome
└── legge sensor.radiante_target_mandata_finale
    └── PID valvola miscelatrice
```

## Versione iniziale

La versione `0.1.0` crea una custom integration con:

- config flow da UI;
- calcolo temperatura zona giorno;
- calcolo umidità zona giorno;
- calcolo punto di rugiada;
- calcolo stato radiante estate;
- calcolo target mandata richiesto;
- calcolo target mandata sicuro;
- calcolo target mandata finale.

## Strategia estate iniziale

| Stato | Condizione | Target richiesto |
|---|---:|---:|
| mantenimento | zona giorno < 25.2°C | 19.2°C |
| normale | zona giorno >= 25.2°C | 19.0°C |
| spinto | zona giorno >= 25.7°C | 18.5°C |
| recupero | zona giorno >= 26.2°C | 18.0°C |

Il target finale è sempre protetto da punto di rugiada:

```text
target_finale = max(target_richiesto, punto_rugiada + margine)
```

Margine iniziale: `2.0°C`.

## Stato sviluppo

- `v0.1.0`: scaffold integrazione custom + sensori.
- `v0.2.0`: number/select entity per modificare soglie e target da UI.
- `v0.3.0`: opzioni avanzate, trend temperatura e anticipo caldo.
- `v0.4.0`: integrazione ESPHome documentata e validata.
