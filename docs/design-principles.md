# Principi di progetto

## Obiettivo principale

La centralina nasce per risolvere il problema del raffrescamento radiante che arriva tardi.

Il problema non e solo il PID della valvola, ma il ritardo complessivo tra:

```text
carico termico reale
→ temperatura stanze che sale
→ target mandata che cambia
→ massa del pavimento che reagisce
→ comfort percepito
```

La centralina deve anticipare con prudenza, non inseguire in modo nervoso.

## Filosofia

La centralina non deve essere un clone dei package YAML attuali.

I package esistenti sono una base di conoscenza:

- entita reali gia affidabili;
- logiche di standby;
- logiche ACS;
- logiche rugiada;
- logiche deumidificazione.

Dove funzionano, si riusano.

Dove producono rumore o ritardo, si migliora.

Dove diventano ridondanti, si potranno semplificare in futuro.

## Strada evolutiva

La sequenza corretta e:

1. osservare;
2. stabilizzare i sensori e lo storico;
3. calcolare stato e target;
4. verificare il comportamento su casa reale;
5. aggiungere consenso comando;
6. collegare ESPHome solo con fallback;
7. valutare azioni locali su deumidifica, testine e termostati.

## Cosa evitare

Non bisogna:

- comandare ESPHome prima che il target sia stabile;
- far cambiare stato per ogni piccola variazione del trend;
- usare sensori diagnostici rumorosi come dashboard principale;
- inseguire il comfort solo con temperatura media;
- ignorare la stanza peggiore;
- ignorare il punto rugiada;
- rimuovere fallback locali da ESPHome.

## Logica da perseguire

La centralina deve usare piu livelli:

- temperatura stanza piu calda;
- trend temperatura interna filtrato;
- umidita stanza;
- punto rugiada stanza;
- punto rugiada massimo casa;
- delta minimo dalla rugiada;
- stato deumidificazione zona giorno/notte;
- stato ACS;
- standby porte/finestre;
- standby rugiada;
- stato stagionale;
- in futuro, temperatura esterna e previsione.

## Decisione corretta

La domanda guida non e:

```text
quanto e caldo fuori adesso?
```

ma:

```text
con questa casa, questa inerzia e queste stanze, che mandata serve adesso per non arrivare tardi tra 1-3 ore?
```

## Prudenza

La centralina deve scegliere il target mandata piu utile e sicuro.

Deve raffrescare abbastanza presto, ma non deve forzare stati troppo aggressivi per variazioni deboli.

Per questo sono stati introdotti:

- trend filtrati;
- testi motivo meno variabili;
- state machine con isteresi;
- stabilizzazione stanza piu calda;
- disattivazione recupero anticipato;
- diagnostica separata dai sensori principali.

## Sicurezza

La regola anti-condensa e superiore alla richiesta comfort.

```text
target_finale = max(target_comfort, punto_rugiada_massimo_casa + margine)
```

Se il rischio rugiada e alto, la centralina deve preferire protezione, deumidificazione o fallback.

## Futuro comando attivo

Il comando attivo deve passare da un consenso esplicito.

Nessun target deve arrivare a ESPHome come comando utile se:

- non e Estate;
- ACS e attiva;
- porte/finestre sono in standby;
- il rischio rugiada e globale;
- il target e fuori range;
- i dati principali sono mancanti;
- Home Assistant e appena ripartito e non ha ancora trend affidabile.

## Ruolo finale

A regime:

```text
Home Assistant decide la strategia climatica
ESPHome esegue il controllo locale in sicurezza
```

Questa separazione deve restare chiara anche nelle versioni attive.