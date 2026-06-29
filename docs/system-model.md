# Modello impianto

## Stanze considerate

La centralina considera tutte le stanze servite dal radiante:

- soggiorno;
- cucina;
- bagno;
- studio;
- camera;
- camera Ricky.

## Zone deumidificazione

### Zona giorno

Stanze:

- soggiorno;
- cucina.

Servita dal deumidificatore idronico zona giorno.

### Zona notte

Stanze:

- bagno;
- studio;
- camera;
- camera Ricky.

Servita dal deumidificatore idronico zona notte.

## Sensori stanza

La centralina usa, dove disponibili:

- temperatura stanza;
- umidita stanza;
- punto rugiada stanza;
- boolean sicurezza rugiada stanza;
- appartenenza zona giorno/notte.

Esempi di sensori temperatura:

```text
sensor.temperatura_cucina
sensor.temperatura_soggiorno
sensor.temperatura_bagno
sensor.temperatura_studio
sensor.temperatura_camera
sensor.temperatura_camera_ricky
```

Esempi di sensori umidita:

```text
sensor.umidita_cucina
sensor.umidita_soggiorno
sensor.umidita_bagno
sensor.umidita_studio
sensor.umidita_camera
sensor.umidita_camera_ricky
```

## Stato fisico della casa

Il modello deve tenere conto della casa reale.

Esempi noti:

- soggiorno esposto a sud, con apporto solare elevato;
- porta vetrata del soggiorno piu critica delle finestre isolate con triplo vetro e tapparelle quasi chiuse;
- camera con flusso radiante ridotto per evitare eccesso di calore in inverno;
- comportamento delle stanze non uniforme.

Quindi la centralina non deve ragionare solo su medie. Deve guardare il locale peggiore e stabilizzare solo le entita descrittive per evitare rumore.

## Stato attuale impianto

La PDC entra in chiamata dal primo termostato che richiede climatizzazione.

Il termostato che chiama:

1. apre le testine della propria zona;
2. abilita il circuito radiante della stanza/zona;
3. fa partire la pompa di ricircolo posizionata sopra la valvola miscelatrice.

Attualmente i termostati possono essere lasciati con target difficili da raggiungere, cosi il pavimento lavora quasi in continuo.

## Storico funzionamento

In passato il pavimento lavorava con mandata fissa regolata manualmente tra 18 C e 19 C dall integrazione della PDC.

Questa scelta era necessaria per evitare condensa quando non erano ancora disponibili i deumidificatori idronici.

## Nuova architettura con deumidificatori

I deumidificatori idronici lavorano meglio con acqua piu fredda, indicativamente intorno a 16 C.

Per separare le esigenze e stata installata una valvola miscelatrice sul circuito pavimento:

```text
PDC / deumidificatori: acqua piu fredda
valvola miscelatrice: miscela mandata fredda e ritorno
pavimento radiante: target variabile e sicuro contro condensa
```

La valvola miscelatrice separa quindi:

- deumidificatori: acqua piu fredda;
- pavimento: acqua piu alta, stabile e protetta dalla rugiada.

## Principio di controllo

La temperatura piu alta tra le stanze guida la richiesta di raffrescamento.

Il punto rugiada massimo casa guida la sicurezza della mandata.

Il delta minimo dalla rugiada serve a capire quanto la casa e vicina al rischio condensa.

La media e utile per comfort generale, ma non deve nascondere il locale peggiore.

## Stato radiante

Gli stati automatici sono:

```text
mantenimento
normale
spinto
recupero
```

La centralina usa:

- soglie reattive;
- trend filtrato;
- anticipo per normale e spinto;
- nessun recupero anticipato;
- isteresi sugli stati.

## Ruolo della centralina

### Oggi

Osserva e calcola:

- temperatura massima casa;
- stanza piu calda;
- stato radiante;
- target comfort;
- target sicuro;
- target consigliato;
- rischio rugiada;
- azione consigliata.

### Prossimo passo

Aggiungere consenso comando verso ESPHome.

### Futuro

Solo dopo verifica:

- comando target mandata ESPHome;
- eventuale azione su deumidifica;
- eventuale gestione locale testine;
- eventuale coordinamento termostati;
- semplificazione dei package ridondanti.