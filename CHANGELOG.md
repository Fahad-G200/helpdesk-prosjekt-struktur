# Changelog

Alle vesentlige endringer i prosjektet dokumenteres her.

---

## [1.0.0] – 2026-01-26 (Vurderingsklart)

### Added
- Cookie consent banner (GDPR-kompatibel)
- Komplett dokumentasjon for vurdering (kompetansemål, testing, KI-bruk)
- Forbedret README med demo-flyt og setup-instruksjoner

### Changed
- Refaktorert CSS og JavaScript til egne filer (bedre vedlikehold)
- Oppgradert dokumentasjon med tydelige kompetansemål og testing

### Fixed
- Input-felt på "Glemt passord"-siden (pointer-events: none fjernet)
- Chatbot-integrasjon

### Security
- Passordhashing med Werkzeug
- Rollebasert tilgangskontroll (RBAC)
- Aktivitetslogg for audit trail

---

## [0.9.0] – 2026-01-10

### Added
- Ticketsystem med fullt CRUD (Create, Read, Update, Delete)
- Vedleggsystem (jpg, png, pdf) med validering
- Kunnskapsbase (KB) med admin-håndtering
- Vurderingssystem for lukkede saker (1-5 stjerner)
- Chatbot-assistanse
- Rolle-basert tilgangskontroll (user/support/admin)
- Aktivitetslogg
- Innstillinger (E-post, SMS, varsler)
- Passord-reset funksjonalitet

### Changed
- Splittet innlogging fra main-app (auth_base.html vs base.html)
- Forbedret design og brukeropplevelse
- Migrert til SQLite-database fra fil-basert lagring

### Fixed
- Admin-bruker manglet ved oppstart
- Saker som forsvant ved omstart (nå persistert i DB)
- Tilgangskontroll mellom bruker og support
- Docker-konfigurering (localhost → 127.0.0.1)

### Security
- Innførte sesjonshåndtering
- Passordhashing
- Filtype-validering på vedlegg

---

## [0.5.0] – 2026-01-07

### Added
- Testplan for løsningen
- Arkitektur-dokumentasjon
- Personvern- og sikkerhetsdokumentasjon
- Brukerveiledning

### Changed
- Strukturert dokumentasjon under docs/

---

## [0.3.0] – 2026-01-05

### Added
- Prosjektbeskrivelse
- Behovskartlegging (docs/krav.md)
- GitHub-repo opprettet
- Grunnstruktur (docs/, backend/, infra/)

### Changed
- Innledende krav og arkitektur definert

---

## [0.1.0] – 2026-01-01

### Added
- Initialisert prosjekt
- Opprettet grunnmapper og filer
