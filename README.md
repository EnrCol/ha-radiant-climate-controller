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

La serie `0.3.x` e ancora **osservativa**.

L integrazione non comanda ancora ESPHome, termostati, testine o deumidificatori. Calcola pero lo stato climatico consigliato e il target mandata che in futuro potra essere usato come comando.

Oggi l integrazione:

- legge le stanze reali della casa;
- calcola la temperatura massima casa;
- individua la stanza piu calda con stabilizzazione anti-rimbalzo;
- calcola trend filtrati a 15, 30 e 60 minuti;
- calcola lo stato radiante automatico: mantenimento, normale, spinto, recupero;
- usa isteresi sugli stati per evitare cambi continui vicino alle soglie;
- protegge il target mandata con punto rugiada massimo casa + margine;
- tiene conto di ACS, standby porte, standby rugiada e rischio condensa;
- espone target richiesto, target sicuro e target consigliato;
- espone azione consigliata e motivo azione;
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

Il recupero anticipato e stato disattivato: il recupero entra solo sopra la soglia reale. Questo riduce oscillazioni tra `recupero anticipato` e `spinto` quando la temperatura e quasi stabile.

## Isteresi stati

Per evitare una centralina nervosa, gli stati automatici usano memoria dello stato precedente e isteresi.

Default:

```text
recupero entra sopra 26.2 C, esce sotto 25.9 C
spinto entra sopra 25.7 C, esce sotto 25.4 C
normale entra sopra 25.2 C, esce sotto 24.9 C
```

La temperatura massima casa resta sempre il massimo reale. Solo alcune entita descrittive, come la stanza piu calda, vengono stabilizzate per ridurre rumore nello storico.

## Sicurezza rugiada

Il target consigliato non puo scendere sotto il limite anti-condensa:

```text
target_consigliato = max(target_comfort, punto_rugiada_massimo_casa + margine)
```

Il margine viene letto dal number dell integrazione se modificato da UI. Se non e stato modificato, resta valido l helper esistente:

```text
input_number.rugiada_temperatura_delta_sicurezza
```

Fallback: `2.5 C`.

## Modello impianto

Stanze considerate:

- cucina;
- soggiorno;
- bagno;
- studio;
- camera;
- camera Ricky.

Zone:

- zona giorno: cucina, soggiorno;
- zona notte: bagno, studio, camera, camera Ricky.

Il soggiorno puo avere apporti solari forti. La camera puo avere portata radiante ridotta. Per questo la centralina deve leggere la casa reale e non basarsi solo su medie generali.

## Entita principali

Sensori principali:

- Temperatura massima casa;
- Umidita massima casa;
- Punto rugiada massimo casa;
- Stato radiante;
- Target mandata comfort;
- Target mandata sicuro;
- Target mandata consigliato;
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

Entita diagnostiche disabilitate di default:

- Campioni trend temperatura;
- Stanza piu vicina alla rugiada;
- Zona piu vicina alla rugiada.

## Configurazione da UI

L integrazione espone number/select per modificare:

- soglie ingresso normale/spinto/recupero;
- soglie anticipo normale/spinto/recupero;
- trend minimo normale/spinto/recupero;
- target mandata mantenimento/normale/spinto/recupero;
- margine punto rugiada;
- stato manuale: auto, mantenimento, normale, spinto, recupero.

## Roadmap

### v0.4 - Consenso comando

Aggiunta di una entita binaria del tipo:

```text
binary_sensor.centralina_radiante_target_mandata_comandabile
```

Sara `on` solo quando il target puo essere usato da ESPHome senza rischi:

- Estate attiva;
- target disponibile;
- target entro range sicuro;
- ACS non attiva;
- standby porte non attivo;
- nessuna protezione rugiada globale;
- stato manuale non in conflitto.

### v0.5 - Collegamento ESPHome

ESPHome continuera ad avere curva locale e PID come fallback.

Il target Home Assistant verra usato solo se:

```text
target disponibile + consenso comando on + valore nel range sicuro
```

### v0.6 - Azioni locali opzionali

Possibili azioni future:

- richiesta deumidificazione zona giorno/notte;
- suggerimento o comando locale su testine;
- blocco o riduzione raffrescamento in stanze vicine alla rugiada;
- gestione piu fine dei termostati.

### v1.0 - Centralina attiva

Obiettivo finale:

```text
Home Assistant decide il target e le priorita climatiche
ESPHome esegue localmente PID e sicurezza base
```

La centralina dovra restare prudente: in caso di dati mancanti, ACS, standby o rischio condensa, deve preferire fallback e protezione.

## Aggiornamenti HACS

Per far vedere a HACS gli aggiornamenti in modo pulito, usare GitHub Releases.

Regola pratica:

1. aggiornare `manifest.json` con la nuova versione;
2. aggiornare `CHANGELOG.md`;
3. fare commit e push;
4. creare una GitHub Release con tag coerente, ad esempio `v0.3.7`;
5. in HACS usare il controllo aggiornamenti o attendere la scansione automatica.

Solo creare un tag non basta: serve una release GitHub completa.
