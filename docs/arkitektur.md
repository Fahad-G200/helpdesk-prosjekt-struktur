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


## Skytjenester og nettverkssegmentering

Helpdesk-løsningen kan driftes i en skytjeneste eller på en lokal server. I et mer realistisk driftsmiljø vil løsningen bestå av flere komponenter som er logisk adskilt for bedre sikkerhet og stabilitet.

En mulig arkitektur er:
- Webapplikasjonen (Flask) kjører i én sone (applikasjonssone)
- Databasen kjører i en egen sone (databasesone)
- Brukere får kun tilgang til webapplikasjonen via HTTP/HTTPS
- Databasen er ikke tilgjengelig direkte fra brukere

Denne typen segmentering reduserer risikoen for at et angrep på webapplikasjonen også gir direkte tilgang til databasen. Løsningen kan kjøres i en skyplattform som for eksempel Azure, AWS eller Google Cloud, der nettverkssoner og brannmurregler kan styres sentralt.