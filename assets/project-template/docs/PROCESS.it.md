# Mappa di lavoro

Leggi prima questa pagina; non caricare tutti i documenti del progetto insieme.

1. **Schema:** `schematic-source.json` e `schematic-layout.json`.
2. **Importazione PCB:** board minimale → gate formato → Update PCB from Schematic.
3. **Piazzamento:** leggere `pcb-layout.json`, poi solo i moduli necessari da
   `pcb-constraints/index.json`; il gate richiede che tutti siano accettati.
4. **Sbroglio/revisione:** concentrarsi su massa, netclass, routing e
   potenza/termica.

Registra fase corrente e rischi aperti in `PROJECT_STATE.md`. Il progetto mantiene
la versione di processo registrata all'inizializzazione: adotta funzioni più nuove
in modo deliberato, senza cambiare metodo a metà revisione.
