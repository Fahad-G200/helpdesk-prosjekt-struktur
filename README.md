# IT Helpdesk – Vg2 Prosjekt

##  Om prosjektet

En fullstendig helpdesk-løsning for skole eller bedrift. Brukere kan melde inn IT-problemer, få hjelp fra support og lese løsninger i kunnskapsbasen. Prosjektet viser kompetanse i **drift**, **brukerstøtte** og **utvikling**.

## Kobling til kompetansemål

### Driftsstøtte
- Administrasjon av brukere, roller og tilganger dekker kompetansemålet:
  *«administrere brukere, tilganger og rettigheter i relevante systemer»*
- Logging, sikkerhetstiltak og backup dekker:
  *«planlegge, drifte og implementere IT-løsninger som ivaretar informasjonssikkerhet»*
- Docker-oppsett og lokal drift viser forståelse for:
  *«utforske og beskrive komponenter i en driftsarkitektur»*

### Brukerstøtte
- Ticketsystemet og eskalering mellom nivåer dekker:
  *«utøve brukerstøtte og veilede i relevant programvare»*
- Kunnskapsbasen og chatboten dekker:
  *«kartlegge behovet for og utvikle veiledninger for brukere»*
- Bruk av tydelig språk og struktur viser:
  *«tilpasse kommunikasjonsform og fagterminologi i møte med brukere»*

### Utvikling
- Flask, routing, templates og database dekker:
  *«designe og implementere IT-tjenester»*
- Bruk av Git, commits og changelog dekker:
  *«beskrive og anvende relevante versjonskontrollsystemer»*
- Databasedesign for brukere, saker og vedlegg dekker:
  *«modellere og opprette databaser for informasjonsflyt i systemer»*

---

##  Kom i gang

### Forutsetninger
- Python 3.8+ og pip
- Docker og Docker Compose (alternativ)
- Git

### Lokalt (uten Docker)

```bash
# Klon og gå til backend
cd backend

# Opprett virtuelt miljø
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Installer pakker
pip install -r requirements.txt

# Initialisér database (første gang)
python app/init_db.py

# Kjør applikasjonen
flask run
```

Åpne: **http://127.0.0.1:5000**

### Med Docker

```bash
# Bygg og start
docker-compose up --build

# Åpne
http://127.0.0.1:8080
```

**Demo-brukere:**
- Bruker: `test` / `test123`
- Support: `admin` / `admin123`

---

##  Brukerroller

| Rolle | Tilganger |
|-------|-----------|
| **User** | Opprette saker, se egne saker, last opp vedlegg, lese KB, vurdere saker |
| **Support** | Se alle saker, endre status/prioritet, administrere KB-artikler |
| **Admin** | Full tilgang + brukerhåndtering, aktivitetslogg |

---

##  Hovedfunksjoner

- **Saksystem (Tickets)** – opprett, lukk, vurder, last opp vedlegg (jpg/png/pdf)
- **Kunnskapsbase (KB)** – admin kan opprett/rediger/slette artikler
- **Chatbot** – tekstbasert assistanse for vanlige spørsmål
- **Tilgangskontroll** – rollebasert sikkerhet
- **Innstillinger** – E-post og varsler
- **Aktivitetslogg** – Audit trail for sikkerhet

---

## Demo- og brukerflyt

1. Bruker logger inn og oppretter en ny sak
2. Saken lagres i systemet og blir synlig for support
3. Support ser saken i dashboard og vurderer prioritet
4. Support kan kommunisere, legge ved filer og lukke saken
5. Bruker får varsling og kan se status på sin sak
6. Hvis mulig løses problemet via chatbot eller kunnskapsbase før eskalering

---

##  DEMO-FLYT

### Bruker-perspektiv
1. Åpne http://127.0.0.1:5000/login
2. Logg inn: `test` / `test123`
3. Gå til "Mine saker" → "Ny sak"
4. Opprett sak med tittel, beskrivelse, prioritet
5. Last opp vedlegg (jpg/pdf) → Send inn
6. Gå til "Mine saker" → åpne saken din
7. Se status: "Åpen" → "Pågår" → "Lukket"
8. Når sak er lukket: vurder løsningen (1-5 stjerner)
9. Gå til "Kunnskapsbase" → les artikler fra support

### Support/Admin-perspektiv
1. Logg inn: `admin` / `admin123`
2. Gå til "Dashboard" → se statistikk og aktive saker
3. Gå til "Admin" → "Saker" → se alle brukers saker
4. Klikk på sak → endre status, prioritet, tildel deg selv
5. Gå til "Admin" → "KB Admin" → opprett ny artikkel
6. Skriv tittel og innhold → publiser
7. Gå til "Admin" → "Brukere" → promover/demote/reset passord
8. Gå til "Admin" → "Aktivitetslogg" → se all brukeraktivitet

---

##  Kompetansemål (LK20 – Vg2 IT)

### **Drift** – Administrere og drifte IT-løsninger

**Mål 1: Tilgangsstyring og roller**
- Prosjektet implementerer 3 brukerroller (user/support/admin)
- Hver rolle har definert tilgang (user kan bare se egne saker, support kan se alle)
- Passordhashing med Werkzeug, sesjonshåndtering i Flask

**Mål 2: Logging og overvåking**
- Aktivitetslogg registrerer alle admin-handlinger
- Systemet sporer hvem som endrer hva og når (audit trail)

**Mål 3: Infrastruktur og containerisering**
- Docker-oppsett med docker-compose.yml
- Løsningen kjører i isolert container, uavhengig av lokalt miljø
- Enkelt å scale og redeploy

---

### **Brukerstøtte** – Veilede og hjelpe brukere

**Mål 1: Strukturert casehåndtering**
- Ticketsystem med klare statuser (Åpen → Pågår → Lukket)
- Brukere gir tilbakemelding via vurdering av sak (1-5 stjerner)
- Support har tydelig arbeitsflyt og prioritering

**Mål 2: Kunnskapsbase og selvbetjening**
- KB-modulen lar support opprett/rediger veiledninger
- Brukere kan selv søke løsninger før de melder sak
- Chatbot gir rask assistanse for hyppige spørsmål

**Mål 3: Kommunikasjon og løsningsorientert tilnærming**
- Saker følges fra innmelding til avslutning
- Vedlegg (screenshots, filer) hjelper support å forstå problemet
- Support kan prioritere kritiske saker høyere

---

### **Utvikling** – Planlegge og utvikle IT-løsninger

**Mål 1: Kravanalyse og design**
- Dokumentert i `docs/krav.md` – behovskartlegging og funksjonelle krav
- Arkitektur beskrevet i `docs/arkitektur.md`
- Klare usecase-beskrivelser

**Mål 2: Implementasjon i Python**
- Flask-applikasjon med 48+ ruter
- Jinja2 for templating (HTML)
- CSS/JavaScript for brukergrensesnitt
- Autentisering (login/register), passordreset

**Mål 3: Versjonskontroll og CI/CD**
- Git-repo med tydelig commit-historie
- CHANGELOG.md dokumenterer alle endringer
- Branch-strategi for testing før merge
- Docker-integrasjon for automatisk deploy

---

##  Sikkerhet og Personvern

- **Autentisering:** Brukernavn + passord (Werkzeug-hashing, salt)
- **Autorisasjon:** Rollebasert tilgangskontroll (RBAC)
- **Sesjonshåndtering:** Flask sessions, sikre cookies
- **Filvedlegg:** Validering av filtyper (jpg, png, pdf), filstørrelse
- **GDPR:** Lokal SQLite-database (ingen skytjenester)
- **Logging:** Aktivitetslogg for audit trail

Se [docs/personvern.md](docs/personvern.md) for detaljer.

---

##  Testing

| Test | Status | Beskrivelse |
|------|--------|-------------|
| Innlogging |  OK | User og admin kan logge inn/ut |
| Roller |  OK | User kan ikke se andre sin saker; support ser alle |
| Tickets |  OK | Opprett, lukk, vurder, endre status |
| Vedlegg |  OK | Last opp/ned jpg/pdf, validering av type |
| KB Admin |  OK | Support kan opprett/rediger/slette artikler |
| Chatbot |  OK | Svarer på spørsmål |
| Passord |  OK | Reset-funksjonalitet fungerer |

Se [docs/testplan.md](docs/testplan.md) for full testkjøring.

---

##  KI-bruk i prosjektet

KI (ChatGPT) ble brukt som **læringsstøtte**:
- Forstå Flask/Jinja/SQLAlchemy-konsepter
- Feilsøking av bugs (Docker, routing, database)
- Kodestruktur og best practices
- Skrive dokumentasjon

**Hva jeg gjorde selv:**
- Skrev all kode manuelt
- Testet hver endring før publisering
- Tok avgjørelser basert på prosjektkrav
- Forstod løsningene før jeg beholdt dem

Se [docs/ai-logg.md](docs/ai-logg.md) for detaljer.

---

##  Prosjektstruktur

```
helpdesk-prosjekt/
├── backend/
│   ├── app/
│   │   ├── routes.py        # 48+ Flask-ruter
│   │   ├── db.py            # Database-initialisering
│   │   ├── templates/       # Jinja2 HTML
│   │   └── static/          # CSS, JS
│   ├── requirements.txt
│   └── init_db.py
├── docs/                    # Dokumentasjon
├── infra/
│   ├── docker-compose.yml
│   └── Dockerfile
└── README.md
```

Se [docs/struktur.md](docs/struktur.md) for detaljert arkitektur-oversikt.

---

##  Dokumentasjon

- **krav.md** – Behovskartlegging og funksjonelle krav
- **arkitektur.md** – Systemarkitektur og design
- **personvern.md** – Sikkerhet og GDPR
- **testplan.md** – Testkjøring og resultat
- **ai-logg.md** – KI-bruk og egen innsats
- **brukerveiledning.md** – Veiledning for sluttbruker
- **prosjektbeskrivelse.md** – Bakgrunn og mål
- **refleksjon.md** – Refleksjon over arbeidet

---

##  Support

For feilsøking eller spørsmål, se [docs/feilsoking.md](docs/feilsoking.md).

# FILE: README.md

# IT Helpdesk (v1.0)
Et helpdesk-system laget for skoleprosjekt (ITK02). Løsningen lar brukere sende inn saker, laste opp vedlegg, bruke kunnskapsbase (KB), og gir support/admin verktøy for å håndtere saker og innhold.

## Demo / visning
**Brukerflyt**
1. Registrer / logg inn
2. Les Kunnskapsbase (nivå 1–2)
3. Opprett sak (nivå 3) + last opp vedlegg (skjermbilde/PDF)
4. Se status og varsler

**Support/Admin-flyt**
1. Se alle saker (admin/support)
2. Se vedlegg til saken
3. Lukke saker
4. Administrere KB-artikler
5. Administrere brukere (rolle/tilgang)

---

## Teknologi
- Backend: **Flask (Python)**
- Database: **SQLite**
- Frontend: **Jinja templates + CSS**
- Filvedlegg: lagres på disk i uploads-mappe + registreres i DB
- Varsling: in-app (notifications), e-post valgfritt (konfig)

---

## Kjøring lokalt
### 1) Installer
```bash
python -m venv venv
source venv/bin/activate   # mac/linux
# venv\Scripts\activate    # windows

pip install -r requirements.txt

## Refleksjon og begrunnede valg

I dette prosjektet har jeg tatt bevisste tekniske og funksjonelle valg for å etterligne en realistisk IT-helpdesk i en organisasjon.

Jeg valgte å implementere roller (bruker, support og admin) for å simulere ekte tilgangsstyring og ansvarsfordeling. Dette gjør løsningen mer realistisk enn en enkel demo, og viser forståelse for hvordan brukere, rettigheter og tilganger administreres i praksis.

Ticketsystemet er bygget slik at brukere kan opprette saker, mens support kan se, prioritere og lukke saker. Dette ble valgt for å speile en ekte arbeidsflyt innen brukerstøtte, der saker eskaleres og håndteres systematisk.

Chatboten ble implementert som første støttenivå (nivå 1) for å gi brukerne rask hjelp uten menneskelig involvering. Løsningen er bevisst holdt enkel og regelbasert, siden målet er å demonstrere forståelse av feilsøkingsflyt – ikke å lage en fullverdig kommersiell AI.

Jeg har også valgt å fokusere på sikkerhet og struktur fremfor avansert grafikk. Dette inkluderer tilgangskontroll, sikker filopplasting og logging av hendelser. Dette valget ble tatt fordi prosjektet først og fremst skal vise faglig forståelse, ikke bare visuelt design.

## Begrensninger og videre arbeid

Dette prosjektet er en versjon 1.0 og har bevisste begrensninger.

Chatboten er regelbasert og ikke koblet til en ekte språkmodell. I en videreutvikling ville dette blitt erstattet med en mer avansert NLP-løsning for bedre forståelse av fritekst.

Systemet bruker lokal database og er ikke satt opp med ekte skylagring. I en produksjonsløsning ville dette vært erstattet med en skytjeneste og redundans.

Designet er funksjonelt, men ikke fullt optimalisert for universell utforming. Videre arbeid ville inkludert bedre tilgjengelighet og testing mot flere brukergrupper.

Disse begrensningene er akseptable innenfor rammen av et skoleprosjekt, og valgene er gjort for å prioritere faglig forståelse og stabil funksjonalitet.
