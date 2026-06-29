# Entita

## Configurazione iniziale

La config flow usa come riferimento la modalita stagionale:

```text
input_select.modalita_stagionale
```

Il modello stanze e definito nel codice dell integrazione e rispecchia l impianto reale.

## Stanze

```text
cucina
soggiorno
bagno
studio
camera
camera_ricky
```

Zone:

```text
giorno: cucina, soggiorno
notte: bagno, studio, camera, camera_ricky
```

## Sensori principali

| Entita | Scopo |
|---|---|
| Temperatura massima casa | Massima temperatura valida tra le stanze |
| Umidita massima casa | Massima umidita valida tra le stanze |
| Punto rugiada massimo casa | Punto rugiada peggiore usato per sicurezza mandata |
| Stato radiante | Stato automatico: mantenimento, normale, spinto, recupero |
| Target mandata comfort | Target richiesto dalla logica comfort |
| Target mandata sicuro | Minimo consentito da punto rugiada + margine |
| Target mandata consigliato | Target finale: max comfort/sicurezza |
| Motivo target non comandabile | Spiega perche ESPHome non deve usare il target come comando |
| Delta sicurezza target | Distanza tra target finale e punto rugiada |
| Stato stagione | Stato letto da input_select.modalita_stagionale |
| Stanza piu calda | Stanza piu calda stabilizzata con delta anti-rimbalzo |
| Temperatura stanza piu calda | Temperatura della stanza piu calda stabilizzata |
| Trend temperatura usato | Trend scelto dalla centralina per la logica |
| Fonte trend temperatura | Fonte trend: 30m, 15m o non_disponibile |
| Trend temperatura 15 min | Trend filtrato su 15 minuti |
| Trend temperatura 30 min | Trend filtrato principale |
| Trend temperatura 60 min | Trend filtrato lungo |
| Delta minimo dalla rugiada | Delta peggiore tra temperatura stanza e punto rugiada |
| Stato rischio rugiada | ok, attenzione, critico o unknown |
| Azione consigliata | Azione logica suggerita |
| Motivo target | Spiegazione sintetica del target |
| Motivo azione | Spiegazione sintetica dell azione |
| Stanze in rischio critico | Numero stanze in rischio critico |
| Stanze in attenzione | Numero stanze in attenzione |

## Binary sensor

| Entita | Scopo |
|---|---|
| Target mandata comandabile | On quando ESPHome puo usare il target HA come comando |

Il target e comandabile solo se:

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

## Entita diagnostiche

Queste entita sono utili per debug, ma sono rumorose nello storico. Sono diagnostiche e disabilitate di default per nuove installazioni:

| Entita | Scopo |
|---|---|
| Campioni trend temperatura | Numero campioni nella memoria trend |
| Stanza piu vicina alla rugiada | Stanza con delta minore dalla rugiada |
| Zona piu vicina alla rugiada | Zona della stanza piu vicina alla rugiada |

Se erano gia state create da Home Assistant prima del cambio categoria, possono restare abilitate nel registro entita. In quel caso vanno disattivate manualmente una volta.

## Number configurabili

| Number | Scopo |
|---|---|
| Soglia normale | Temperatura ingresso stato normale |
| Soglia spinto | Temperatura ingresso stato spinto |
| Soglia recupero | Temperatura ingresso stato recupero |
| Anticipo normale | Temperatura minima per normale anticipato |
| Anticipo spinto | Temperatura minima per spinto anticipato |
| Anticipo recupero | Parametro mantenuto per compatibilita, non usato da recupero anticipato |
| Trend normale | Trend minimo per normale anticipato |
| Trend spinto | Trend minimo per spinto anticipato |
| Trend recupero | Parametro mantenuto per compatibilita, non usato da recupero anticipato |
| Target mantenimento | Target mandata comfort in mantenimento |
| Target normale | Target mandata comfort in normale |
| Target spinto | Target mandata comfort in spinto |
| Target recupero | Target mandata comfort in recupero |
| Margine rugiada | Margine aggiunto al punto rugiada massimo casa |

## Select configurabili

| Select | Opzioni |
|---|---|
| Stato manuale | auto, mantenimento, normale, spinto, recupero |

Lo stato manuale serve per test e diagnosi. In modalita auto la centralina calcola lo stato automaticamente.

## Entita future previste

### v0.5

ESPHome log-only:

```text
target_mandata_ha
consenso_target_ha
target_che_verrebbe_usato
```

### v0.6+

Possibili entita future:

- richiesta deumidificazione zona;
- azione locale stanza;
- protezione locale stanza;
- suggerimento testina;
- stato comando attivo.
