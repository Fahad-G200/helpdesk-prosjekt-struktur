# Prosjektstruktur – IT Helpdesk

## Backend-arkitektur

### Mappestruktur

```
backend/
├── app/
│   ├── __init__.py              # Flask-initialisering
│   ├── routes.py                # 48+ Flask-ruter (alle endpoints)
│   ├── db.py                    # Database-initialisering
│   ├── config.py                # Konfiguppsett
│   ├── email_service.py         # E-post (Flask-Mail)
│   ├── get_user.py              # Hjelpefunksjon for brukerhenting
│   │
│   ├── templates/               # Jinja2 HTML-templates
│   │   ├── base.html            # Hoved-layout (innlogget)
│   │   ├── auth_base.html       # Layout for innlogging
│   │   ├── login.html           # Innloggingsside
│   │   ├── register.html        # Registreringsside
│   │   ├── dashboard.html       # Statistikk og oversikt
│   │   ├── tickets.html         # Liste over saker
│   │   ├── ticket_detail.html   # Detaljer på sak
│   │   ├── kb.html              # Kunnskapsbase-liste
│   │   ├── article.html         # Artikkelinnhold
│   │   ├── admin_users.html     # Brukerhåndtering
│   │   ├── admin_tickets.html   # Saksadministrasjon
│   │   ├── admin_kb.html        # KB-administrasjon
│   │   ├── settings.html        # Brukerinnstillinger
│   │   ├── chatbot.html         # Chat-grensesnitt
│   │   ├── notifications.html   # Varsler
│   │   └── (flere spesialsider)
│   │
│   ├── static/                  # CSS, JS, bilder
│   │   ├── css/
│   │   │   ├── app.css          # Hoved-styling (app)
│   │   │   └── auth.css         # Styling (innlogging)
│   │   ├── js/
│   │   │   ├── chatbot.js       # Chatbot-frontend
│   │   │   └── admin.js         # Admin-funksjoner
│   │   └── images/
│   │
│   ├── uploads/                 # Bruker-vedlegg
│   └── helpdesk.db              # SQLite-database
│
├── requirements.txt             # Python-pakker
├── init_db.py                   # Database-setup
```

---

## Databasemodeller

```python
# User
- id (PK)
- username (UNIQUE)
- password_hash
- email
- role (user/support/admin)
- created_at
- last_login

# Ticket
- id (PK)
- user_id (FK → User)
- title
- description
- priority (Lav/Middels/Høy/Kritisk)
- status (Åpen/Pågår/Lukket)
- created_at
- updated_at
- assigned_to (FK → User)

# Attachment
- id (PK)
- ticket_id (FK → Ticket)
- filename
- file_path
- uploaded_at

# KBArticle
- id (PK)
- title
- content
- author (FK → User)
- created_at
- updated_at

# Notification
- id (PK)
- user_id (FK → User)
- message
- is_read
- created_at

# ActivityLog
- id (PK)
- user_id (FK → User)
- action
- target (ticket/user/article)
- timestamp
```

---

## Rute-oversikt (48+ endpoints)

### Autentisering
- `GET/POST /login` – Innlogging
- `GET/POST /register` – Registrering
- `GET /logout` – Logg ut
- `GET/POST /forgot-password` – Glemt passord
- `GET/POST /reset-password` – Tilbakestill passord

### Bruker-funksjoner
- `GET /dashboard` – Oversikt/statistikk
- `GET /tickets` – Mine saker (liste)
- `POST /tickets` – Opprett sak
- `GET /tickets/<id>` – Sak-detaljer
- `POST /tickets/<id>/close` – Lukk sak
- `POST /tickets/<id>/rate` – Vurder sak
- `POST /tickets/<id>/upload` – Last opp vedlegg
- `GET /attachments/<id>/download` – Last ned vedlegg
- `GET /kb` – Kunnskapsbase
- `GET /kb/<id>` – Les artikkel
- `GET /settings` – Innstillinger
- `POST /settings` – Lagre innstillinger
- `GET /notifications` – Varsler

### Support/Admin-funksjoner
- `GET /admin/tickets` – Se alle saker
- `POST /tickets/<id>/assign` – Tildel sak
- `POST /tickets/<id>/priority` – Endre prioritet
- `POST /admin/tickets/bulk-close` – Lukk flere
- `POST /admin/tickets/bulk-delete` – Slett flere
- `GET /admin/users` – Brukerliste
- `POST /admin/users/<user>/promote` – Promover bruker
- `POST /admin/users/<user>/demote` – Demote bruker
- `POST /admin/users/<user>/reset-password` – Reset passord
- `POST /admin/users/<user>/delete` – Slett bruker
- `GET /admin/kb` – KB-administrasjon
- `GET/POST /admin/kb/new` – Opprett artikkel
- `GET/POST /kb/<id>/edit` – Rediger artikkel
- `POST /kb/<id>/delete` – Slett artikkel
- `GET /admin/activity` – Aktivitetslogg

### Chatbot
- `POST /chat` – Send melding
- `POST /chat/reset` – Nullstill chat

---

## Sikkerheitsarkitektur

```
┌─────────────────┐
│   Bruker (FE)   │  ← HTML/CSS/JS
└────────┬────────┘
         │ HTTP/HTTPS
┌────────▼────────────────────────┐
│   Flask-app (Backend)           │
├─────────────────────────────────┤
│ 1. Route (autentisering)        │  ← @login_required, check_role()
│ 2. Database (SQLite)            │  ← Parametrisert query (SQL injection-sikker)
│ 3. Password hashing (Werkzeug)  │  ← Salt + hash
│ 4. Session management           │  ← Secure cookies
│ 5. Logging (audit trail)        │  ← ActivityLog
└─────────────────────────────────┘
         │
┌────────▼────────────────┐
│   database.db (SQLite)  │  ← Lokal, ingen skytjenester
└─────────────────────────┘
```

---

## Teknologi-stack

| Lag | Teknologi | Versjon |
|-----|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) | Modern |
| **Backend** | Python, Flask | 3.8+, 3.0.0 |
| **Template-engine** | Jinja2 | (Flask) |
| **Database** | SQLite | 3+ |
| **Auth** | Werkzeug (hashing) | 3.0.1 |
| **E-post** | Flask-Mail | 0.9.1 |
| **Containerisering** | Docker, Docker Compose | latest |
| **Versjonskontroll** | Git, GitHub | - |

---

## Anbefaling for videre refactoring

### Kortsiktig (lett)
1. **Flytt routes til moduler**
   ```
   routes/
   ├── auth.py           # Login, register, passord-reset
   ├── tickets.py        # Alle ticket-operasjoner
   ├── kb.py             # Kunnskapsbase-ruter
   └── admin.py          # Admin-funksjoner
   ```
   **Fordel:** Lettere å vedlikeholde, mindre routes.py-fil

2. **Opprett services-mappe**
   ```
   services/
   ├── email_service.py   # E-post
   ├── chatbot_service.py # Chatbot-logikk
   └── file_service.py    # Vedlegg-håndtering
   ```
   **Fordel:** Separasjon av ansvar, testbar kode

3. **Lag utils-mappe**
   ```
   utils/
   ├── validators.py      # Input-validering
   ├── decorators.py      # Custom decorators (@login_required, @admin_only)
   └── helpers.py         # Hjelpefunksjoner
   ```

### Mediumsiktig (moderat)
4. **Legg til testing-rammeverk**
   - Pytest for automatisert testing
   - Mock av database
   - Testkjøring i CI/CD

5. **Innfør logging**
   - Python logging (istfor print)
   - Strukturert logging (JSON)
   - Sentral log-fil

### Langsiktig (større arbeid)
6. **Migrer til PostgreSQL**
   - SQLite OK for prototype, men PostgreSQL bedre for produksjon
   - Endringer: SQLAlchemy connection string + dialect
   - Zero breaking changes i appkoden

7. **Legg til REST API**
   - Skilt frontend fra backend
   - Flask-RESTx for dokumentasjon
   - Token-basert auth (JWT)

8. **Frontend-framework**
   - Migrer HTML/JS til React eller Vue.js
   - Modulær, testbar kode
   - Bedre brukeropplevelse (SPA)

---

## Sikkerheits-checklist

-  Passordhashing (Werkzeug)
-  Rollebasert tilgangskontroll
-  Sesjonshåndtering
-  Filtype-validering
-  SQL-injection-beskyttelse
-  HTTPS (ikke implementert, anbefales for produksjon)
-  Rate limiting (ikke implementert)
-  2FA (ikke implementert)

---

## Deployment

### Lokalt
```bash
python app/init_db.py  # Init DB
flask run              # Start app
```

### Docker
```bash
docker-compose up --build
```

### Produksjon (anbefaling)
- Bruk Gunicorn eller uWSGI
- HTTPS med Let's Encrypt
- PostgreSQL database
- Redis for sessions/caching
- Nginx reverse proxy
- Environment-variabler for secrets

---

**Sist oppdatert:** 26. januar 2026
