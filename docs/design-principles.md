# Principi di progetto

## Obiettivo principale

La centralina nasce per risolvere il problema del raffrescamento radiante che arriva tardi.

Il problema osservato non è solo il PID della valvola, ma il ritardo complessivo tra:

```text
carico termico reale
→ temperatura stanze che sale
→ target mandata che cambia
→ massa del pavimento che reagisce
→ comfort percepito
```

La centralina deve quindi anticipare, non inseguire.

## Ruolo dei package Home Assistant attuali

I package attuali sono dati di contesto e integrazione.

Non sono automaticamente la soluzione migliore e non devono essere considerati immutabili.

La centralina deve:

- leggere la situazione reale esistente;
- riusare le entità già affidabili;
- rispettare i blocchi di sicurezza esistenti;
- proporre miglioramenti dove la logica attuale arriva tardi o lavora in modo troppo grezzo.

## Cosa evitare

Non bisogna trasformare la centralina in un semplice clone dei package attuali.

Non bisogna neppure fare un refactor gigante senza motivo.

La strada corretta è evolutiva:

1. osservare;
2. confrontare logica attuale e logica proposta;
3. generare target e consigli;
4. abilitare comandi attivi solo quando il comportamento è verificato.

## Logica da perseguire

La centralina deve usare più livelli:

- temperatura stanza più calda;
- trend temperatura interna;
- umidità e punto rugiada stanza per stanza;
- stato deumidificazione zona giorno/notte;
- stato termostati e chiamate reali;
- temperatura esterna e, in futuro, previsione;
- stato ACS, porte/finestre e standby.

## Decisione corretta

La centralina deve scegliere il target mandata pavimento più utile e sicuro per prevenire il surriscaldamento delle stanze.

La domanda guida non è:

```text
quanto è caldo fuori adesso?
```

ma:

```text
con questa casa, questa inerzia e queste stanze, che mandata serve adesso per non arrivare tardi tra 1-3 ore?
```

## Uso della logica attuale

La logica attuale di termostati, deumidificatori e rugiada deve essere usata come base di conoscenza.

Dove funziona, si riusa.

Dove limita il risultato, si migliora.

Dove è ridondante rispetto alla centralina, si può valutare una semplificazione futura.
