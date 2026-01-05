# Arkitektur og oppsett – Helpdesk og kunnskapsbase

## Oversikt
Løsningen består av en webapplikasjon (helpdesk) og en database. Brukere bruker nettleser for å logge inn og opprette saker. Support/admin bruker samme løsning for å håndtere saker og publisere veiledninger.

Målet med arkitekturen er å holde løsningen enkel, men samtidig vise god struktur, tilgangsstyring og drift.

---

## Komponenter

### 1. Klient (bruker)
- Nettleser på PC/Mac
- Bruker appen for å lage sak og lese veiledninger

### 2. Webapplikasjon (backend)
- Python + Flask
- Håndterer innlogging, roller, tickets og artikler
- Validerer input og styrer tilgang basert på rolle

### 3. Database
- Lagrer brukere, tickets og kunnskapsartikler
- Tilkobling skal kun være tilgjengelig for applikasjonen (ikke direkte fra brukere)

---

## Arkitekturdiagram (enkelt)

[Bruker i nettleser]
        |
        v
  (HTTP til webapp)
        |
        v
[Flask-webapp]  --->  [Database]
   (logikk)             (data)

   