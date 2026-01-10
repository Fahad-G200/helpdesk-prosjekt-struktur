# Changelog

## 2026-01-05
- Opprettet prosjektstruktur med docs, backend og infra
- Publiserte prosjektet til GitHub
- Startet README med prosjektbeskrivelse, MVP og kobling til kompetansemål

## 2026-01-05
- Skrev behovskartlegging og funksjonelle krav i krav.md

## 2026-01-05
- Skrev arkitektur for prosjektet
- Beskrev hvordan systemet er bygget opp med webapp og database
- Forklarte roller, drift med Docker og enkel segmentering
- Skrev personvern og sikkerhet (hvilke data som lagres og tiltak for å beskytte dem)
- Skrev brukerveiledning for vanlige brukere (innlogging, saker og kunnskapsbase)



## 2026-01-07
- Skrev testplan for helpdesk-løsningen (testmiljø, metoder og testtilfeller)

# Changelog

Alle viktige endringer i dette prosjektet dokumenteres her.

2026-01-09
### Lagt til
- Opprettet grunnstruktur for helpdesk-prosjektet
- Implementert helpdesk med tre støttenivåer (nivå 1, 2 og 3)
- Skrevet selvhjelpsinstruksjoner for vanlige problemer:
  - Feide-pålogging
  - Nettverk (Wi-Fi)
  - Utskrift
  - Glemt eller låst passord
- Laget refleksjon skrevet i førsteperson
- Dokumentert prosjektbeskrivelse, mål og fremgangsmåte
- Laget enkel HTML-side som demonstrerer helpdesk-flyten

### Endret
- Forbedret struktur og språk for å gjøre prosjektet mer profesjonelt
- Tilpasset dokumentasjon til tverrfaglig vurdering

### Planlagt
- Utvide kunnskapsbasen med flere problemtyper
- Forbedre design og brukervennlighet
- Eventuelt implementere lagring av innsendte saker



2026-01-10

- Satt opp Docker (nginx) for å kjøre helpdesk lokalt hjemme via localhost
- Satt opp Docker (nginx) for å kjøre helpdesk lokalt via http://127.0.0.1:8080


2026-01-10

### Nytt
- Lagt til database for lagring av saker
- Roller for bruker og support
- Support kan lukke saker
- Docker-oppsett for kjøring av prosjektet
- Script for database-oppsett og backup

### Endret
- Gått fra midlertidig lagring til database
- Forbedret struktur i koden
- Forbedret design og brukeropplevelse
- Bedre oversikt over saker og status

### Fikset
- Saker forsvinner ikke lenger ved omstart
- Bedre kontroll på hvem som kan gjøre hva i systemet

### Notat
- Dette er første ferdige versjon av prosjektet (versjon 1.0)
- Prosjektet dekker kompetansemål i utvikling, drift og brukerstøtte
