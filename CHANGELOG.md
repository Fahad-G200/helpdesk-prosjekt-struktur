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

## 2026-01-20

### Sikkerhet
- Byttet hardkodet SECRET_KEY til sikker, tilfeldig generert nøkkel
- Lagt til security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
-  Lagt til error handling i alle routes
-  Implementert logging av viktige hendelser (innlogging, saksopprettelse, etc.)

### Dokumentasjon
-  Opprettet `docs/risikoanalyse.md` med komplett risikovurdering
-  Opprettet `docs/kvalitetssikring.md` med ITIL-basert prosess og KPI
-  Opprettet `backup.py` for automatisk database-backup

### Kode-kvalitet
-  Slettet tomme filer (models.py, build_site.py)
-  Ryddet i duplikate build-scripts
- Forbedret error messages for bedre brukeropplevelse

### Filer endret
- `backend/app/__init__.py` - Sikker SECRET_KEY og security headers
- `backend/app/routes.py` - Error handling og logging
- `docs/risikoanalyse.md` - Ny fil
- `docs/kvalitetssikring.md` - Ny fil
- `backup.py` - Ny fil


### Added
- La til nye sider for Varsler (/notifications), Innstillinger (/settings) og Aktivitetslogg (/admin/activity).
- La til templates: `notifications.html`, `settings.html` og `logs.html`.
- La til visning av antall uleste varsler (badge) i navigasjonen via `notif_count`.

### Changed
- Oppdatert `routes.py` slik at lenkene i `base.html` faktisk peker på eksisterende routes (fikser 404 på Innstillinger).
- Oppdatert `db.py` slik at eksisterende databaser automatisk får kolonnene `email`, `notify_email` og `notify_inapp` (trygge `ALTER TABLE` ved oppstart).

### Fixed
- Fikset 404 “Not Found” når man trykker på “Innstillinger” i menyen.
- Reduserte risiko for krasj ved innstillinger/varsler hvis databasen var opprettet før disse feltene fantes.

### Added
- Lagt til støtte for **SMS-varslinger** via Twilio
- Brukere kan nå lagre **telefonnummer** i profilinnstillinger
- Nye varslingsvalg i innstillinger:
  - E-postvarsler
  - Interne varsler i applikasjonen
  - SMS-varsler
- Eksakt tidspunkt vises for:
  - Når en sak ble opprettet
  - Når en sak ble oppdatert
  - Når en sak ble lukket
- Aktivitet logges når bruker endrer varselinnstillinger

### Changed
- Oppdatert **settings-siden** til å håndtere flere typer varslinger
- Database-struktur utvidet med:
  - `phone`
  - `notify_sms`
- Oppdatert `update_preferences` slik at alle varslingsvalg lagres samlet
- Twilio-integrasjon gjort **valgfri** slik at appen ikke krasjer hvis Twilio ikke er installert

### Fixed
- Rettet feil som gjorde at **Innstillinger-siden ikke fungerte**
- Forhindret krasj ved manglende `twilio`-avhengighet
- Ryddet opp i imports og fjernet direkte Twilio-import fra routes
- Stabilisert database-initiering ved eksisterende databaser

### Security
- Brukernavn er fortsatt **unik** (kan ikke registreres flere ganger)
- Applikasjonen starter trygt selv uten SMS-konfigurasjon

### Added
- Støtte for filvedlegg på saker (attachments)
- Mulighet for å laste opp skjermbilder, PDF-er og dokumenter til en sak
- Ny database-tabell for vedlegg knyttet til tickets
- Unike filnavn ved opplasting for å unngå overskriving
- Nedlasting av vedlegg med tilgangskontroll
- SMS-varsling via Twilio (valgfritt)
- Telefonnummer lagret på brukerprofil
- Nye brukerinnstillinger for:
  - E-postvarsler
  - Interne varsler
  - SMS-varsler
- Aktivitetslogging for endring av innstillinger

### Changed
- Utvidet `/settings`-siden til å håndtere flere varseltyper
- Forbedret tickets-visning med støtte for vedlegg
- Database-initialisering gjort mer robust (ALTER TABLE med try/except)
- Varslingslogikk forbedret slik at appen ikke krasjer hvis eksterne tjenester mangler
- Strukturert bedre separasjon mellom database, ruter og tjenester

### Fixed
- Innstillinger som tidligere ikke ble lagret korrekt
- Feil ved oppstart hvis Twilio ikke var installert
- Varsler som ikke ble markert som lest
- Feil som oppstod ved manglende miljøvariabler

### Security
- Sikret filopplasting med `secure_filename`
- Begrenset tillatte filtyper via konfigurasjon
- Forhindrer path traversal ved opplasting
- Kun sakseier eller support har tilgang til vedlegg

---

## 2026-01-22

### Added
- Implementert avansert AI-basert helpdesk-chat
- Chatboten analyserer fritekst og identifiserer problemområde automatisk
- Støtte for flere temaer:
  - Feide / innlogging
  - Wi-Fi / nettverk
  - Utskrift / skrivere
  - Passord og kontotilgang
  - Microsoft 365 (Teams, Outlook, OneDrive m.fl.)
  - Nettleserproblemer
- Chatten gir trinnvis feilsøking (grunnleggende → avansert)
- Automatisk eskalering til support etter flere mislykkede forsøk
- Mulighet for bruker å be om menneskelig support direkte i chat
- Endepunkt for reset av chat-samtale (`/chat/reset`)

### Changed
- Forbedret saksopprettelse med støtte for flere filvedlegg samtidig
- Tickets inkluderer nå vedlegg i visning for både bruker og support
- Varslinger sendes til support ved ny sak og ved vurdering
- Forbedret aktivitetslogging for:
  - Chat-bruk
  - Saksopprettelse
  - Lukking av saker
  - Vurderinger

### Added
- Støtte for sikre filvedlegg på saker:
  - Skjermbilder, PDF-er og dokumenter
  - Unike filnavn for å unngå overskriving
  - Ny database-tabell for vedlegg
- Nedlasting av vedlegg med tilgangskontroll
  - Kun sakseier eller support har tilgang

### Security
- Validering av filtyper ved opplasting
- Sikret filnavn med `secure_filename`
- Forhindrer uautorisert tilgang til vedlegg

## [Unreleased]

### Added
- Ny dashboard-side (/dashboard) med oversikt over tickets
- Statistikk for aktive saker og kritiske saker
- Avansert AI-basert chatbot (IntelligentHelpdeskAI)
- Støtte for kontekstbasert chat, feilanalyse og eskalering til support
- Bevaring av samtaletilstand via session

### Changed
- Erstattet tidligere enkel chatbot med intelligent AI-løsning

### Fixed
- Ingen eksisterende funksjonalitet endret eller fjernet


# Changelog

## [Unreleased]

### Added
- Blå primærknapper i kunnskapsbasen for viktige handlinger:
  - "Start med nivå 1"
  - "Gå til Mine saker"
  - "Opprett / se saker"

### Changed
- Oppdatert kb.html slik at sentrale navigasjonslenker nå bruker
  eksisterende knappestil (`.btn`) for bedre visuell konsistens.

### Fixed
- Fjernet inkonsistent visning av viktige handlinger som lilla
  standardlenker i kunnskapsbasen.

### Notes
- Ingen endringer er gjort i `base.html`.
- Ingen CSS-, JavaScript- eller backend-funksjonalitet er endret.
- Endringen er bevisst isolert til én template for å unngå regresjoner.


# Changelog

## 2026-01-23

### Added
- Egen autentiserings-layout (`auth_base.html`) for innlogging og registrering
- Visuelt adskilt innlogging/registrering fra resten av applikasjonen
- Hero-seksjon på autentiseringssider med:
  - Bakgrunnsbilde
  - Mørk gradient-overlay
  - Funksjonspills (24/7 Support, Secure Access, Expert Team)
- Fanebasert navigasjon mellom **Login** og **Sign Up**
- Felles design og struktur for alle auth-sider

### Changed
- Flyttet innlogging og registrering ut av hovedlayout (`base.html`)
- Sørget for at dashboard, tickets, varsler og innstillinger kun vises etter innlogging
- Autentiseringssider arver ikke sidebar eller topbar
- Forbedret visuell konsistens og profesjonelt førstetrykk

### Fixed
- Fjernet uønsket visning av dashboard-/app-elementer på innloggingssiden
- Forhindret at navigasjon og sidebar vises før bruker er autentisert
- Ryddet opp i layout-arv som tidligere gjorde at alt ble vist på samme side

### Notes
- Ingen endringer er gjort i `base.html` for applikasjonssidene
- Endringen er isolert til autentisering (`auth_base.html`, login- og register-templates)
- Backend-logikk for innlogging, sesjon og sikkerhet er ikke endret


## [2026-01-23]

### Added
- Fullt fungerende admin-sider for:
  - Brukeradministrasjon
  - Sakshåndtering (inkl. bulk handlinger)
  - Kunnskapsbase-administrasjon
  - Systeminnstillinger
- Manglende templates for admin-funksjoner ble lagt til

### Fixed
- Fikset Internal Server Error ved klikk på admin-menyvalg
- Rettet feil med manglende eller feil-koblede Flask-ruter
- Fjernet dupliserte view-funksjoner som førte til endpoint-kollisjoner

### Improved
- Admin-menyen fungerer nå konsekvent uten å endre eksisterende UI eller design
- Backend og templates er nå korrekt synkronisert
