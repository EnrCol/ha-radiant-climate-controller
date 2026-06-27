# Analisi package climatizzazione attuale

Analisi basata sui file esportati da `/homeassistant/packages/climatizzazione/`.

## File allegati analizzati

- `acs.yaml`
- `acs_test.yaml.bak`
- `deumidificatore_portatile.yaml`
- `ecodan.yaml`
- `gestione_acs.yaml.bak`
- `gestione_deumidificatori.yaml`
- `gestione_porte_finestre.yaml`
- `gestione_rugiada.yaml`
- `gestione_termostati.yaml`
- `helpers.yaml`
- `riscaldamento_bagno.yaml`
- `split_taverna.yaml`

## Architettura reale emersa

### 1. Generatore / PDC

`ecodan.yaml` gestisce il cambio stagione:

- Estate: Ecodan zone 1/2 in `Cooling Flow`, gruppo `climate.termostati_pt` in `cool`, setpoint 25°C.
- Inverno: Ecodan zone 1/2 in `Heating Flow`, gruppo `climate.termostati_pt` in `heat`, setpoint 23°C.

Questo conferma che `input_select.modalita_stagionale` è il selettore globale.

### 2. Termostati / testine

`gestione_termostati.yaml` contiene i 6 termostati principali:

- `climate.termostato_cucina`
- `climate.termostato_soggiorno`
- `climate.termostato_bagno`
- `climate.termostato_studio`
- `climate.termostato_camera`
- `climate.termostato_camera_ricky`

Sono gestiti anche:

- salvataggio setpoint per ogni stanza;
- standby estate con spegnimento globale `climate.termostati_pt`;
- ripristino estate con setpoint salvati;
- standby inverno con setpoint 15°C;
- ripristino inverno.

### 3. Deumidificatori idronici

`gestione_deumidificatori.yaml` divide il sistema in due zone:

#### Zona giorno

- cucina
- soggiorno

Entità principali:

- `sensor.temperatura_media_zona_giorno`
- `sensor.umidita_media_zona_giorno`
- `sensor.soglia_umidita_zona_giorno`
- `binary_sensor.richiesta_deumidificazione_giorno`
- `switch.consenso_deumidificatore_giorno`

#### Zona notte

- camera
- camera Ricky
- bagno
- studio

Entità principali:

- `sensor.temperatura_media_zona_notte`
- `sensor.umidita_media_zona_notte`
- `sensor.soglia_umidita_zona_notte`
- `binary_sensor.richiesta_deumidificazione_notte`
- `switch.consenso_deumidificatore_notte`

La pompa comune dei deumidificatori è:

- `switch.deumidificatori_pompa_ricircolo`

Si accende se almeno uno dei due consensi deumidificatore è attivo.

### 4. Rugiada / condensa

`gestione_rugiada.yaml` contiene:

- `sensor.punto_rugiada_minimo_casa`
- `sensor.punto_rugiada_massimo_casa`
- `binary_sensor.standby_rugiada`

Il controllo rugiada confronta, stanza per stanza:

- punto di rugiada stanza;
- temperatura stanza;
- `input_number.rugiada_temperatura_delta_sicurezza`, default 2.5°C.

Se una stanza entra nel delta di sicurezza, `binary_sensor.standby_rugiada` diventa ON.

Nel file sono presenti automazioni commentate per spegnere e riaccendere i singoli termostati quando una stanza si avvicina alla rugiada. Questa logica è coerente con l'evoluzione della centralina: prima azione locale sulla stanza, poi azione globale sulla mandata.

### 5. Standby generale

`helpers.yaml` crea `binary_sensor.standby_attivo` come aggregatore di:

- standby ACS;
- standby porte;
- standby rugiada.

Nota tecnica da verificare: nel template compare `binary.sensor.standby_rugiada` invece di `binary_sensor.standby_rugiada`. Questo potrebbe impedire allo standby rugiada di entrare correttamente nello standby generale.

### 6. Porte e finestre

`gestione_porte_finestre.yaml` crea `binary_sensor.standby_porte` da `group.porte_finestre_piano_terra`, con `delay_on` 10 minuti e `delay_off` 1 minuto.

Le vecchie automazioni di standby/ripristino porte risultano commentate.

### 7. ACS

`acs.yaml` contiene:

- `binary_sensor.acs_in_riscaldamento`
- `binary_sensor.acs_blocco_valvola_miscelatrice`

Queste entità sono fondamentali per la logica ESPHome della valvola: in Estate, durante ACS e per il ritardo configurato, la valvola pavimento deve essere gestita in modo protetto.

## Implicazione per la custom integration

La centralina non deve ricreare da zero la logica esistente.

Deve prima diventare un supervisore che legge:

- stato stagione;
- termostati e hvac_action;
- richieste deumidificazione giorno/notte;
- consensi deumidificatori;
- standby ACS / porte / rugiada;
- punto rugiada massimo casa;
- delta rugiada stanza per stanza;
- target mandata finale consigliato.

## Roadmap corretta

### v0.1 osservazione

- calcolo stanza più calda;
- calcolo stanza più critica per rugiada;
- target mandata consigliato;
- nessun comando automatico su termostati/deumidificatori.

### v0.2 integrazione con entità esistenti

- usare `sensor.punto_rugiada_massimo_casa` se disponibile;
- usare `binary_sensor.standby_rugiada` come segnale sicurezza;
- usare `binary_sensor.richiesta_deumidificazione_giorno/notte` come input.

### v0.3 azioni consigliate

- indicare stanza critica;
- indicare zona deumidifica critica;
- suggerire: deumidifica, chiusura stanza, alzare mandata.

### v0.4 controllo attivo opzionale

- comando target mandata verso ESPHome;
- eventuale chiusura termostato stanza critica;
- eventuale forzatura deumidificatore zona.

## Regola di progetto

Ordine preferito di protezione in Estate:

1. deumidificare la zona corretta;
2. se rischio localizzato, chiudere la stanza/testina critica;
3. se rischio diffuso, alzare la mandata globale;
4. se sensori incoerenti, usare fallback prudente.
