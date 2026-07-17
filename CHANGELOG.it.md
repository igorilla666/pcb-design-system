# Registro modifiche

Questo è un riepilogo umano. Leggi la voce più recente; le precedenti sono
contesto, non compiti obbligatori da recuperare.

## 1.8.0 — Test strutturati del framework

- Un unico runner separa suite veloci, template, fixture di regressione e
  integrazione KiCad opzionale, producendo un breve report locale.
- La prima fixture di regressione intercetta il token `uuid` PCB non valido a
  livello radice.

## 1.7.0 — Vincoli modulari prima del piazzamento

- I vincoli PCB sono otto file piccoli, indicizzati da un file breve.
- Netclass, stackup, massa, meccanica, routing, termica e test devono essere
  accettati prima del piazzamento.
- `check_pcb_constraints.py . --require-placement-ready` è il gate di
  piazzamento.

## 1.6.0 — Continuità di massa prima del piazzamento

- Pianificare layer di riferimento, domini GND, keep-out di sicurezza e percorsi
  di ritorno prima di piazzare i componenti; ispezionare le zone provvisorie.

## 1.5.0 — Il PCB parte dall'importazione dello schema

- Creare/validare un PCB minimale, poi usare Update PCB from Schematic di KiCad.
- L'automazione piazza solo footprint importati; non ricrea le associazioni.

## 1.4.0 — Input dichiarativi per generatori

- Separare sorgente elettrica, layout schema e piazzamento PCB, evitando di
  nascondere decisioni progettuali nel codice Python.

## 1.3.0 — Strumenti riproducibili e versione KiCad

- Solo strumenti di progetto registrati con hash possono modificare l'hardware.
- Gli script storici sono quarantinati; KiCad usa esattamente la major dichiarata.

## 1.2.0 e precedenti — Fondamenta

- Record di progetto in Git, confine delle dipendenze, gate di formato KiCad,
  manifest elettrico e revisione della leggibilità dello schema.
