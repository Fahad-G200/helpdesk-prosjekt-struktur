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

2026-01-10
### Nytt
- Opprettet komplett prosjektstruktur for helpdesk og kunnskapsbase (docs, backend, infra, site)
- Implementert nivåbasert brukerstøtte (nivå 1–3) med tydelig eskaleringsflyt
- Lagt til kunnskapsbase i backend (/kb) integrert med innlogging og felles design
- Lagt til innsendingsskjema på nivå 3 med kategori, prioritet og enhet/programvare
- Implementert ticketsystem med opprettelse, visning og lukking av saker
- Lagt til SQLite-database for lagring av brukere og saker
- Implementert registreringsside for nye brukere
- Implementert roller (bruker og support/admin)
- Lagt til fast admin/support-bruker som kan se og håndtere alle saker
- Support-bruker kan lukke saker og følge status
- Satt opp Docker (nginx) for lokal kjøring av prosjektet uavhengig av skolens nettverk
- Oppdatert og fullført dokumentasjon (testplan, personvern, arkitektur, refleksjon)

### Endret
- Gått fra midlertidig/demonstrasjonslagring til databasebasert lagring
- Forbedret struktur i backend-koden (routes, database, templates)
- Forbedret navigasjon og brukeropplevelse i backend (felles layout og meny)
- Forbedret design og struktur på nettsiden for mer profesjonelt uttrykk
- Rettet Dockerfile fra feil mappe (`system/`) til korrekt innhold (`docs` / `site`)
- Forbedret innhold og sammenheng i README, prosjektbeskrivelse og refleksjon

### Fikset
- Rettet feil der saker forsvant ved omstart (manglende database)
- Rettet feil der admin-bruker manglet i databasen
- Forbedret tilgangskontroll mellom bruker og support/admin
- Rettet problemer med lokal kjøring (`localhost`) ved testing
  - Prosjektet kjøres nå stabilt via `http://127.0.0.1:8080`
- Ryddet opp i HTML- og CSS-struktur for å sikre korrekt visning

### Notater
- Dette er første ferdige hovedversjon av prosjektet (versjon 1.0.0)
- Prosjektet viser en helhetlig helpdesk-løsning med brukerstøtte, roller og saksbehandling
- Løsningen kan kjøres lokalt og er uavhengig av skolens nettverk
- Standard admin for demo/testing:
  - Brukernavn: `admin`
  - Passord: `admin123`

### Planlagt videre arbeid
- Koble nivå 3-innsendingsskjema enda tettere mot backend (for eksempel forhåndsvalgt kategori)
- Utvide kunnskapsbasen med flere artikler og bedre søk
- Gjennomføre flere tester og dokumentere testresultater



## 2026-01-11
- Lagt til beskrivelse av skytjenester og nettverkssegmentering
- Gjennomført risikoanalyse av helpdesk-løsningen
- Utviklet kursmateriell for brukere
- Dokumentert valg av programmeringsspråk og rammeverk



## 2026-01-12
### Endret
- Erstattet OpenAI-basert chat (krever billing) med lokal helpdesk-chatbot
- Chatboten kan nå håndtere fritekst/setninger og gir trinnvis veiledning (nivå 1–3)
- Lagt til enkle oppfølgingsspørsmål (OS/nettleser/feilmelding) for mer presis feilsøking

## Changelog

## 2026-01-16

### Endret
- Rettet ugyldig HTML i `base.html` ved å flytte CSS-regler inn i `<style>`-taggen.
- Forbedret navigasjonen med aktive menypunkter basert på nåværende side.
- Standardisert navigasjonslenker ved å bruke felles CSS-klassen `nav-link`.

### Forbedret
- Brukergrensesnittet fremstår mer profesjonelt og konsistent.
- Navigasjonen gir tydeligere tilbakemelding på hvor brukeren befinner seg i systemet.

### Fikset
- CSS som tidligere lå utenfor `<style>`-taggen og ikke ble tolket korrekt av nettleseren.

### Filer endret
- `backend/app/templates/base.html`

