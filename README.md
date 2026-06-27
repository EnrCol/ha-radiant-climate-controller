# HA Radiant Climate Controller

Custom integration Home Assistant per usare Home Assistant come **centralina climatica radiante predittiva** ed ESPHome come **attuatore/PID valvola miscelatrice**.

## Obiettivo

La centralina nasce per evitare che il radiante arrivi tardi quando le stanze sono già troppo calde.

La logica principale non è copiare i package esistenti, ma usare i dati reali della casa per anticipare:

```text
stanze + trend + rugiada + deumidifica + standby
→ target mandata consigliato
→ ESPHome PID valvola miscelatrice
```

## Versione 0.2.0

La v0.2.0 è una base di osservazione predittiva. Non comanda ancora termostati, testine o deumidificatori.

Legge il modello reale dell'impianto:

- cucina e soggiorno in zona giorno;
- bagno, studio, camera e camera Ricky in zona notte;
- deumidificatori giorno/notte già gestiti da Home Assistant;
- sensori punto rugiada stanza per stanza;
- standby ACS, porte e rugiada;
- modalità stagionale `input_select.modalita_stagionale`.

Crea sensori per:

- temperatura massima casa;
- stanza più calda;
- trend temperatura casa;
- stanza più critica per rugiada;
- zona rugiada critica;
- target mandata comfort;
- target mandata sicuro;
- target mandata consigliato;
- azione consigliata;
- motivo del target e dell'azione.

## Strategia estate iniziale

| Stato | Condizione reattiva | Anticipo con trend | Target comfort |
|---|---:|---:|---:|
| mantenimento | sotto soglia | stabile | 19.2°C |
| normale | >= 25.2°C | >= 24.8°C e trend positivo | 19.0°C |
| spinto | >= 25.7°C | >= 25.3°C e trend positivo | 18.5°C |
| recupero | >= 26.2°C | >= 25.8°C e trend positivo | 18.0°C |

Il target consigliato è protetto da rugiada:

```text
target_consigliato = max(target_comfort, punto_rugiada_massimo_casa + margine)
```

Il margine viene letto da:

```text
input_number.rugiada_temperatura_delta_sicurezza
```

fallback: `2.5°C`.

## Stato sviluppo

- `v0.1.0`: scaffold integrazione custom + sensori base.
- `v0.2.0`: modello stanze reale, trend, rugiada esistente, azione consigliata.
- `v0.3.0`: entità number/select per soglie, target e modalità manuale.
- `v0.4.0`: comando target mandata verso ESPHome.
- `v0.5.0`: controllo attivo opzionale su deumidifica/testine.
