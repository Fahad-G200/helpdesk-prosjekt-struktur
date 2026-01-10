# Feilsøking

## Docker viser "Welcome to nginx" i stedet for siden min
Årsak:
- nginx finner ikke index.html eller containeren bruker gammel build

Løsning:
1. Sjekk at `docs/index.html` finnes
2. Bygg på nytt:
   docker rm -f helpdesk
   docker build -t helpdesk-app .
   docker run -d --name helpdesk -p 8080:80 helpdesk-app
3. Åpne i nettleser: http://127.0.0.1:8080

## localhost virker ikke, men 127.0.0.1 virker
Årsak:
- noen maskiner har DNS/hosts-innstillinger som gjør at localhost ikke peker riktig

Løsning:
- bruk alltid http://127.0.0.1:8080 i dette prosjektet

## Backend starter ikke
Sjekk:
- at venv er aktivert
- at requirements er installert
- at databasen er initialisert

Kommandoer:
source venv/bin/activate
pip install -r requirements.txt
python -c "from app.db import init_db; init_db()"
flask --app app run --debug