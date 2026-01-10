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



# Changelog

Alle vesentlige endringer i prosjektet dokumenteres i denne filen.

## [1.0.0] – 2026-01-10
### Nytt
- Opprettet komplett prosjektstruktur for helpdesk og kunnskapsbase (docs, backend, infra)
- Implementert nivåbasert brukerstøtte (nivå 1–3) med tydelig eskaleringsflyt
- Lagt til innsendingsskjema på nivå 3 med kategori, prioritet og enhet/programvare
- Implementert visning av mottatt sak på nettsiden (demonstrasjon uten backend-lagring)
- Lagt til database for lagring av saker
- Implementert roller for bruker og support
- Support-bruker kan se og lukke saker
- Oppdatert testplan, personvern og arkitektur-dokumentasjon
- Satt opp Docker (nginx) for lokal kjøring av prosjektet

### Endret
- Gått fra midlertidig lagring til database for saker
- Forbedret struktur i backend-koden
- Forbedret design og brukeropplevelse på nettsiden
- Forbedret oversikt over saker og status
- Rettet Dockerfile fra feil mappe (`system/`) til riktig mappe (`docs/`)
- Forbedret innhold og struktur i dokumentasjon (README, prosjektbeskrivelse og refleksjon)

### Fikset
- Rettet feil der saker forsvant ved omstart
- Forbedret tilgangskontroll (bruker vs. support)
- Rettet feil der `localhost` ikke fungerte som forventet ved testing
  - Prosjektet kjøres nå via `http://127.0.0.1:8080`
- Ryddet opp i HTML-struktur slik at skjema vises korrekt

### Notater
- Dette er første ferdige hovedversjon av prosjektet (versjon 1.0.0)
- Prosjektet dekker kompetansemål innen utvikling, drift og brukerstøtte
- Løsningen kan kjøres lokalt og er uavhengig av skolens nettverk

### Planlagt videre arbeid
- Koble nivå 3-innsendingsskjema direkte til backend for full saksbehandling
- Utvide kunnskapsbasen med flere artikler og søk/filtrering
- Gjennomføre og dokumentere flere tester og feilrettinger