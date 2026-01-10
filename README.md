# Helpdesk og kunnskapsbase – Vg2 IT

## Om prosjektet
Dette prosjektet er en enkel helpdesk-løsning laget for skole eller bedrift.  
Brukere kan melde inn IT-problemer, følge status på saken sin og lese veiledninger i en kunnskapsbase.  
IT-support kan se sakene, svare på dem og oppdatere status.

Prosjektet brukes for å vise kompetanse i **utvikling**, **driftsstøtte** og **brukerstøtte**.

---

## Mål med prosjektet
- Lage en fungerende IT-tjeneste
- Vise hvordan man planlegger, bygger og dokumenterer en løsning
- Øve på arbeidsmåter som brukes i IT-yrker (GitHub, dokumentasjon, testing)

---

## Målgruppe
- Elever eller ansatte som trenger IT-hjelp  
- IT-support som håndterer saker og veileder brukere

---

## Funksjoner – versjon 1.0 (MVP)

### Bruker
- Logge inn
- Opprette en ny supportsak (ticket)
- Se status på egne saker
- Lese veiledninger i kunnskapsbasen

### Support / admin
- Se alle saker
- Endre status (åpen / pågår / løst)
- Svare på saker
- Legge til og redigere kunnskapsartikler

---

## Teknologi og verktøy
- VS Code
- Git og GitHub
- Python og Flask
- Database (senere)
- Docker og Docker Compose

---

## Dokumentasjon i prosjektet
- `docs/krav.md` – behov og krav til løsningen  
- `docs/arkitektur.md` – hvordan systemet er bygget og driftet  
- `docs/personvern.md` – personvern og sikkerhet  
- `docs/brukerveiledning.md` – veiledning for brukere  
- `docs/feilsoking.md` – hvordan feil kan løses  
- `docs/testplan.md` – testing av løsningen  
- `docs/ai-logg.md` – bruk av KI i prosjektet  

---

## Kompetansemål (kort forklart)

### Driftsstøtte
- Administrere brukere og roller (bruker / support / admin)
- Planlegge og dokumentere IT-løsningen
- Bruke Docker for å kjøre og drifte tjenesten

### Brukerstøtte
- Veilede brukere gjennom veiledninger og kunnskapsbase
- Feilsøke problemer på en strukturert måte
- Kommunisere tydelig med brukere

### Utvikling
- Lage krav basert på behov
- Utvikle en fungerende løsning i Python
- Bruke GitHub til versjonskontroll og dokumentasjon

---

## Status
Prosjektet er under utvikling.  
Denne versjonen viser planlegging, struktur og start på implementasjon.  
Løsningen bygges videre i neste periode.


# Helpdesk‑prosjekt

Dette prosjektet er et tverrfaglig arbeid hvor du designer og dokumenterer en enkel helpdesk‑løsning for en skole eller liten organisasjon. Målet er å kombinere IT‑ferdigheter (struktur, teknologi), yrkesfaglige serviceferdigheter (kundebehandling) og norsk (tydelig og korrekt fagspråk).

## Innhold

Dette repositoriet inneholder følgende:

| Mappestruktur | Beskrivelse |
| --- | --- |
| `README.md` | Kort introduksjon til prosjektet (denne filen). |
| `docs/prosjektbeskrivelse.md` | Detaljert beskrivelse av bakgrunn, mål og fremgangsmåte for prosjektet. |
| `docs/refleksjon.md` | Mal (nå med eksempel) for refleksjon rundt eget arbeid. |
| `system/level1.md` | Veiledning til nivå 1: selvhjelp og standardløsninger. |
| `system/level2.md` | Veiledning til nivå 2: dypere feilsøking. |
| `system/level3.md` | Veiledning til nivå 3: sende inn sak/eskalering. |
| `system/index.html` | Enkel nettside som viser kunnskapsbase og skjema for innmelding. |

## Hvordan bruke

1. **Les prosjektbeskrivelsen** (`docs/prosjektbeskrivelse.md`) for å forstå mål og vurderingskriterier.
2. **Les og rediger veiledningene** i `system`‑mappen. Disse beskriver hvordan brukere løser problemer på ulike nivåer (selvhjelp, teknikerstøtte, eskalering).
3. **Åpne `system/index.html`** i en nettleser for å se et eksempel på en enkel kunnskapsbase med de tre nivåene. Her kan du legge til flere kategorier og forbedre utseendet.
4. **Les og eventuelt tilpass refleksjonen** i `docs/refleksjon.md` når prosjektet er ferdig eller underveis.

Prosjektet kan brukes som basis for en tverrfaglig oppgave der du både viser teknisk forståelse, evne til å planlegge og dokumentere, samt bruk av fagspråk og serviceinnstilling.


## Kjøring hjemme med Docker (lokalt miljø)

Dette prosjektet kan kjøres lokalt hjemme uten skolens nettverk ved hjelp av Docker.

### Start
1. Bygg image:
   docker build -t helpdesk-app .
2. Start container:
   docker run --name helpdesk -p 8080:80 helpdesk-app
3. Åpne i nettleser:
   http://localhost:8080

### Stopp
docker stop helpdesk

### Start igjen
docker start helpdesk

### Slett container (hvis du vil kjøre på nytt)
docker rm -f helpdesk


## Kjøring lokalt hjemme (Docker)

Prosjektet kan kjøres lokalt uten skolens nettverk ved hjelp av Docker.

### Bygg image
docker build -t helpdesk-app .

### Start container
docker run -d --name helpdesk -p 8080:80 helpdesk-app

### Åpne i nettleser
http://127.0.0.1:8080

### Stoppe / starte igjen
docker stop helpdesk
docker start helpdesk

### Slette container (hvis du vil kjøre på nytt)
docker rm -f helpdesk