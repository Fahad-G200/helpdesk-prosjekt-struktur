# Testplan – IT Helpdesk

## Formål
Sikre at helpdesk-løsningen fungerer slik spesifikasjon og krav beskriver.

---

## Testmiljø
- **Lokalt:** Python 3.8+, Flask, SQLite
- **Docker:** docker-compose up
- **Nettleser:** Chrome / Firefox (modern)
- **Test-brukere:**
  - User: `test` / `test123`
  - Support: `admin` / `admin123`

---

## Testresultater (Siste kjøring: 2026-01-26)

| # | Test | Trinn | Forventet resultat | Resultat | Status |
|---|------|-------|-------------------|----------|--------|
| 1 | **Innlogging** | 1. Åpne /login<br>2. Skriv `test` / `test123`<br>3. Klikk "Sign In" | Omdirigeres til dashboard | Fungerer korrekt | ✅ OK |
| 2 | **Feil innlogging** | 1. Skriv feil passord<br>2. Klikk "Sign In" | Feilmelding uten å avsløre detaljer | Viser generisk feilmelding | ✅ OK |
| 3 | **Registrering** | 1. Gå til /register<br>2. Fyll inn brukernavn, passord<br>3. Klikk "Sign Up" | Ny bruker opprettet, omdirigeres til login | Bruker synlig i database | ✅ OK |
| 4 | **Brukerrolle – tilgang** | 1. Logg inn som `test` (user)<br>2. Prøv å se alle saker (admin-panel) | Tilgang nektes (kun eget brukerrom) | Får 403 Forbidden | ✅ OK |
| 5 | **Support-rolle – tilgang** | 1. Logg inn som `admin` (support)<br>2. Gå til Admin → Saker<br>3. Se alle brukersaker | Ser alle saker fra alle brukere | Viser 100% av saker | ✅ OK |
| 6 | **Opprette sak** | 1. Logg inn som user<br>2. Gå til "Mine saker"<br>3. Opprett ny sak (tittel, beskrivelse, prioritet)<br>4. Klikk "Send inn" | Saken lagres med status "Åpen" | Sak ID generert, lagret i DB | ✅ OK |
| 7 | **Vedlegg – opplasting** | 1. Opprett sak<br>2. Last opp JPG/PDF-fil<br>3. Klikk "Upload" | Fil valideres og lagres | Fil synlig i sak-detaljer | ✅ OK |
| 8 | **Vedlegg – validering** | 1. Prøv å laste opp .exe/.zip-fil | Feilmelding, fil ikke akseptert | "Filtypen ikke tillatt" | ✅ OK |
| 9 | **Vedlegg – nedlasting** | 1. Åpne sak med vedlegg<br>2. Klikk på nedlasting-knapp | Fil lastes ned til datamaskin | Fil mottatt som JPG/PDF | ✅ OK |
| 10 | **Lukk sak (bruker)** | 1. Logg inn som user<br>2. Åpne egen åpen sak<br>3. Klikk "Lukk sak" | Status endres til "Lukket" | Sak låst, kan ikke endres | ✅ OK |
| 11 | **Vurder sak** | 1. Lukket sak vises<br>2. Velg rating (1-5 stjerner)<br>3. Klikk "Send" | Vurdering lagres, "Tusen takk"-melding | Rating synlig i sak | ✅ OK |
| 12 | **Kunnskapsbase (bruker)** | 1. Logg inn som user<br>2. Gå til "Kunnskapsbase"<br>3. Klikk på artikkel | Artikkel-innhold vises | Lesbar, formatert korrekt | ✅ OK |
| 13 | **KB Admin – opprett artikel** | 1. Logg inn som `admin`<br>2. Gå til Admin → KB Admin<br>3. Opprett ny artikel (tittel, innhold)<br>4. Publiser | Artikkel lagres og synlig for alle | Artikkel ID generert, i DB | ✅ OK |
| 14 | **KB Admin – rediger artikel** | 1. Klikk "Rediger" på artikel<br>2. Endre innhold<br>3. Klikk "Lagre" | Endringer lagres | Artikkel oppdatert i DB | ✅ OK |
| 15 | **KB Admin – slett artikel** | 1. Klikk "Slett" på artikel<br>2. Bekreft sletting | Artikkel fjernet fra KB | Ikke synlig for brukere | ✅ OK |
| 16 | **Admin – brukertyper** | 1. Gå til Admin → Brukere<br>2. Se liste over alle brukere<br>3. Klikk "Promote" / "Demote" | Brukerrolle endres | Role-felt oppdatert i DB | ✅ OK |
| 17 | **Admin – reset passord** | 1. Klikk "🔑 Nytt passord" på bruker<br>2. Brukeren får nytt passord | Brukeren kan logge inn med nytt passord | Werkzeug-hash oppdatert | ✅ OK |
| 18 | **Admin – slett bruker** | 1. Klikk "🗑️ Slett" på bruker<br>2. Bekreft sletting | Bruker fjernet fra system | Ikke lenger i databasen | ✅ OK |
| 19 | **Admin – saker (bulk)** | 1. Gå til Admin → Saker<br>2. Velg flere saker<br>3. Klikk "Lukk valgte" | Alle valgte saker lukkes | Status endret til "Lukket" | ✅ OK |
| 20 | **Admin – aktivitetslogg** | 1. Gå til Admin → Aktivitetslogg<br>2. Se liste over handlinger | Alle admin-handlinger logget | User, timestamp, action registrert | ✅ OK |
| 21 | **Chatbot** | 1. Åpne chat-panel nederst<br>2. Skriv "Hei"<br>3. Klikk "Send" | Chatbot svarer | Svar mottatt, kontekstgitt | ✅ OK |
| 22 | **Passord-reset** | 1. Gå til /forgot-password<br>2. Skriv brukernavn<br>3. Klikk "Send kode" | Omdirigeres, bekreftelse vises | Input-felt fungerer (fikset) | ✅ OK |
| 23 | **Cookie-banner** | 1. Åpne inkognito-modus<br>2. Besøk nettsiden<br>3. Klikk "Godta" | Banner forsvinner, cookie settes | localStorage.cookie_consent = "accepted" | ✅ OK |
| 24 | **Innstillinger** | 1. Logg inn som user<br>2. Gå til "Innstillinger"<br>3. Oppdater E-post/telefon<br>4. Klikk "Lagre" | Preferanser lagres | Felt oppdatert i bruker-profil | ✅ OK |
| 25 | **Sikkerhet – session timeout** | 1. Logg inn<br>2. Vent 1 time uten aktivitet<br>3. Prøv å laste side | Omdirigeres til login | Sesjon utløpt, må logge inn på nytt | ✅ OK |

---

## Testdekning

✅ **Godkjent** (25/25 tester)

- ✅ Autentisering (login, register, passord-reset)
- ✅ Autorisasjon (roller, tilgangskontroll)
- ✅ Tickets (CRUD, status, vurdering)
- ✅ Vedlegg (opplasting, nedlasting, validering)
- ✅ Kunnskapsbase (lesing, admin-CRUD)
- ✅ Admin-funksjoner (brukere, bulkoperasjoner, logging)
- ✅ Sikkerhet (hashing, sessions, GDPR)
- ✅ Brukervennlighet (chatbot, innstillinger, banner)

---

## Konklusjon

Prosjektet er **stabil og vurderingsklart**. Alle kjerneflyter fungerer som forventet.

**Sist testet:** 26. januar 2026
