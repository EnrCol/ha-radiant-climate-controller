# HA Radiant Climate Controller

<p align="center">
  <img src="assets/icon.svg" alt="Radiant Climate Controller" width="160">
</p>

Custom integration Home Assistant per trasformare Home Assistant in una **centralina climatica radiante predittiva**.

Il progetto nasce per un impianto radiante in raffrescamento con:

- pompa di calore;
- deumidificatori idronici giorno/notte;
- valvola miscelatrice gestita da ESPHome/PID;
- sensori temperatura, umidita e punto rugiada stanza per stanza;
- logiche di standby per ACS, porte/finestre e rischio rugiada.

## Stato attuale

La serie `0.4.x` introduce il primo livello di preparazione al comando ESPHome.

L integrazione **non comanda ancora direttamente ESPHome**, ma espone un consenso esplicito per dire se il target mandata consigliato puo essere usato come comando esterno.

Oggi l integrazione:

- legge le stanze reali della casa;
- calcola la temperatura massima casa;
- individua la stanza piu calda con stabilizzazione anti-rimbalzo;
- calcola trend filtrati a 15, 30 e 60 minuti;
- calcola lo stato radiante automatico: mantenimento, normale, spinto, recupero;
- usa isteresi sugli stati per evitare cambi continui vicino alle soglie;
- protegge il target mandata con punto rugiada massimo casa + margine;
- tiene conto di ACS, standby porte, standby rugiada e rischio condensa;
- espone target comfort, target sicuro e target consigliato;
- espone azione consigliata e motivo azione;
- espone `Target mandata comandabile` per il futuro collegamento a ESPHome;
- espone il motivo quando il target non e comandabile;
- permette configurazione da UI tramite entita number/select.

## Obiettivo finale

L obiettivo non e solo mostrare sensori.

L integrazione dovra diventare una centralina che decide **quando e quanto raffrescare il pavimento** prima che la casa arrivi tardi al comfort.

Schema finale previsto:

```text
stanze + trend + rugiada + deumidifica + standby + stagione
→ stato radiante
→ target mandata sicuro
→ consenso comando
→ ESPHome PID valvola miscelatrice
→ eventuali azioni su deumidifica, testine e termostati
```

## Strategia climatica estiva

La logica estiva usa la temperatura piu alta tra le stanze come riferimento principale.

| Stato | Ingresso reattivo | Anticipo con trend | Target comfort |
|---|---:|---:|---:|
| mantenimento | sotto soglia | no | 19.2 C |
| normale | >= 25.2 C | >= 24.8 C e trend positivo | 19.0 C |
| spinto | >= 25.7 C | >= 25.3 C e trend positivo | 18.5 C |
| recupero | >= 26.2 C | no | 18.0 C |

Il recupero anticipato e disattivato: il recupero entra solo sopra la soglia reale.

## Consenso comando v0.4

La v0.4 aggiunge:

```text
binary_sensor.centralina_radiante_target_mandata_comandabile
sensor.centralina_radiante_motivo_target_non_comandabile
```

Il target e comandabile solo quando:

- Estate e attiva;
- stato manuale e `auto`;
- stato radiante noto;
- target mandata disponibile;
- target tra 17 C e 23 C;
- ACS non attiva;
- standby porte non attivo;
- protezione rugiada globale non attiva;
- non c e una protezione locale rugiada o richiesta deumidifica prioritaria.

Questo consenso e pensato per ESPHome: il PID potra usare il target Home Assistant solo quando il binary sensor e `on`.

## Sicurezza rugiada

Il target consigliato non puo scendere sotto il limite anti-condensa:

```text
target_consigliato = max(target_comfort, punto_rugiada_massimo_casa + margine)
```

Fallback margine: `2.5 C`.

## Entita principali

Sensori principali:

- Temperatura massima casa;
- Umidita massima casa;
- Punto rugiada massimo casa;
- Stato radiante;
- Target mandata comfort;
- Target mandata sicuro;
- Target mandata consigliato;
- Motivo target non comandabile;
- Delta sicurezza target;
- Stanza piu calda;
- Temperatura stanza piu calda;
- Trend temperatura usato;
- Fonte trend temperatura;
- Delta minimo dalla rugiada;
- Stato rischio rugiada;
- Azione consigliata;
- Motivo target;
- Motivo azione;
- Stanze in rischio critico;
- Stanze in attenzione.

Binary sensor principale:

- Target mandata comandabile.

Entita diagnostiche disabilitate di default:

- Campioni trend temperatura;
- Stanza piu vicina alla rugiada;
- Zona piu vicina alla rugiada.

## Roadmap

### v0.4 - Consenso comando

Completata la base per dire a ESPHome se il target HA puo essere usato.

### v0.5 - ESPHome log-only

ESPHome leggera target HA e consenso, ma il PID continuera a usare la logica locale. Serve a confrontare:

```text
target curva locale
target HA
consenso HA
target che verrebbe usato
```

### v0.6 - Collegamento PID reale

ESPHome usera il target Home Assistant solo se:

```text
target disponibile + consenso comando on + valore nel range sicuro
```

La curva locale ESPHome restera fallback.

### v1.0 - Centralina attiva

Obiettivo finale:

```text
Home Assistant decide il target e le priorita climatiche
ESPHome esegue localmente PID e sicurezza base
```

La centralina deve restare prudente: in caso di dati mancanti, ACS, standby o rischio condensa, deve preferire fallback e protezione.
