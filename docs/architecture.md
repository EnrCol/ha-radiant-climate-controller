# Architettura

## Scelta architetturale

Questo progetto usa una custom integration Home Assistant invece di un package YAML.

La divisione prevista e:

```text
Home Assistant = centralina climatica predittiva
ESPHome = attuatore locale, PID e fallback valvola miscelatrice
```

Home Assistant ha il contesto completo della casa. ESPHome deve restare robusto e autonomo nel controllo locale della valvola.

## Perche integrazione e non package

Una integrazione permette:

- configurazione da UI;
- entita generate automaticamente;
- diagnostica piu pulita;
- installazione e aggiornamento via HACS;
- logica Python piu leggibile e testabile;
- evoluzione verso number, select, binary_sensor e button;
- separazione netta tra osservazione, decisione e comando.

## Stato attuale

La serie `0.3.x` e osservativa.

Oggi la centralina:

- legge temperatura, umidita e rugiada stanza per stanza;
- calcola temperatura massima casa;
- calcola trend filtrati a 15, 30 e 60 minuti;
- assegna uno stato radiante automatico;
- applica isteresi agli stati;
- calcola target mandata comfort;
- applica limite anti-condensa;
- produce target mandata consigliato;
- produce azione consigliata;
- espone motivo target e motivo azione.

Non comanda ancora:

- ESPHome;
- PID;
- valvola miscelatrice;
- deumidificatori;
- testine;
- termostati.

## Ciclo di controllo previsto

```text
sensori stanza
+ umidita
+ punto rugiada
+ trend interno
+ deumidifica zona
+ modalita stagionale
+ standby ACS/porte/rugiada
→ stato radiante
→ target mandata comfort
→ limite anti-condensa
→ target mandata consigliato
→ consenso comando
→ ESPHome PID valvola
```

## Separazione dei livelli

### Livello 1 - Osservazione

Calcola e pubblica sensori, senza comandare nulla.

Esempi:

- temperatura massima casa;
- trend temperatura usato;
- stato radiante;
- target consigliato;
- azione consigliata.

### Livello 2 - Consenso comando

Decide se il target calcolato puo essere usato come comando.

Esempi di blocco:

- modalita diversa da Estate;
- ACS attiva;
- standby porte;
- protezione rugiada globale;
- target fuori range;
- dati principali non disponibili.

### Livello 3 - Attuazione ESPHome

ESPHome legge target e consenso da Home Assistant.

Se consenso e target sono validi, usa il target HA. Altrimenti resta sulla curva locale o fallback sicuro.

### Livello 4 - Azioni locali opzionali

Solo dopo validazione del comportamento:

- richiesta deumidificazione zona;
- gestione testine;
- eventuale coordinamento termostati;
- protezioni locali piu fini.

## Regola anti-condensa

```text
target_finale = max(target_richiesto, punto_rugiada_massimo_casa + margine)
```

Default margine: `2.5 C`.

Il margine puo essere modificato dalla UI dell integrazione.

## Principio di sicurezza

La centralina deve essere prudente.

Se mancano dati, se il rischio rugiada e elevato, se ACS o standby sono attivi, il target non deve diventare un comando diretto.

La logica attiva arrivera solo dopo la fase osservativa e solo tramite un consenso esplicito.