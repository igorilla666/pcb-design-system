# Inizia da qui

Non è necessario leggere l'intero framework. Questa pagina è la mappa operativa.

## Flusso essenziale

1. Dichiarare l'esatta versione di KiCad e mantenere portabili i sorgenti.
2. Creare e validare prima lo schema.
3. Creare un PCB minimale, validarne il formato e aggiornarlo dallo schema con
   KiCad.
4. Prima del piazzamento, accettare i vincoli modulari ed eseguire il relativo
   gate.
5. Piazzare, ispezionare le zone GND provvisorie, sbrogliare, quindi eseguire
   DRC e revisione manuale.

## Cosa leggere e quando

| Situazione | Leggere solo… |
| --- | --- |
| Avvio/ripresa progetto | `AGENTS.md`, `PROJECT_STATE.md`, ultimo log del progetto. |
| Creazione schema | `schematic-source.json`, `schematic-layout.json`. |
| Preparazione piazzamento | `pcb-layout.json`, poi i file indicati da `pcb-constraints/index.json`. |
| Sbroglio o revisione rame | `ground.json`, `netclasses.json`, `routing.json`, `power-thermal.json`. |
| Aggiornamento framework | Solo l'ultima voce di `CHANGELOG.it.md`. |

## Regole sempre obbligatorie

- Usare la major KiCad dichiarata; mai un fallback a un'altra versione.
- Prima lo schema; KiCad importa footprint e net nel PCB.
- Mai usare script storici non revisionati o cercare risorse locali non dichiarate.
- Nessun piazzamento prima del superamento del gate dei vincoli.
- Il DRC è necessario, ma restano obbligatorie le revisioni elettrica e meccanica.

## Come restare in controllo

Tratta il framework come una checklist, non come un unico prompt. Lavora una fase
alla volta, apri solo i record di quella fase e chiudi registrando decisione e
risultato della validazione. I progetti esistenti restano sulla versione di
processo registrata; adotta una capacità più nuova deliberatamente, un modulo
alla volta.
