# AI-logg (2026)

## Hvordan jeg brukte KI i prosjektet
Jeg brukte KI (ChatGPT/Copilot) som et støtteverktøy gjennom hele utviklingsprosessen av helpdesk-prosjektet. KI ble brukt til å:

- forstå og strukturere helpdesk-nivåer (nivå 1–3) og hvordan disse brukes i praksis
- foreslå en logisk oppbygning av systemet (innlogging, dashboard, saker, varsler)
- få hjelp til å designe et profesjonelt og moderne brukergrensesnitt (HTML/CSS)
- forbedre brukeropplevelse og visuell sammenheng mellom sider
- feilsøke tekniske problemer i Flask/Jinja (routing, templates, endpoint-konflikter, ImportError)
- forstå hvorfor enkelte sider ikke fungerte (manglende path, feil arving av templates)
- forbedre struktur i backend (routes, templates, base.html) uten å endre funksjonalitet unødvendig
- sikre filopplasting (secure_filename, filtype-sjekk, tilgangskontroll)
- feilsøke Docker-problemer:
  - manglende mapper
  - feil bruk av `localhost` vs `127.0.0.1`
  - container som ikke startet riktig
- skrive bedre og mer profesjonell dokumentasjon (README, testplan, changelog)
- formulere commit-meldinger og changelog på en profesjonell og ryddig måte

KI ble også brukt til å forklare *hvorfor* noe ikke fungerte, ikke bare *hva* som måtte endres.

---

## Hva jeg gjorde selv
Selv om jeg brukte KI aktivt, var det jeg som gjorde det faktiske arbeidet i prosjektet:

- jeg bestemte selv hvilke forslag fra KI som skulle brukes eller forkastes
- jeg skrev og limte inn kode manuelt i prosjektet og la inn endringer i riktige filer
- jeg bygget opp filstrukturen (templates, routes, static, Docker)
- jeg testet alle endringer lokalt og i Docker
- jeg rettet feil som oppstod underveis og verifiserte at fixes faktisk fungerte
- jeg tilpasset løsningen til kravene i skoleprosjektet (tverrfaglig oppgave)
- jeg tok bevisste valg rundt sikkerhet, struktur og brukervennlighet
- jeg skilte innlogging fra resten av applikasjonen (`auth_base.html`) for bedre design og flyt
- jeg dokumenterte prosjektet slik at lærere kan vurdere det (README/TODO/CHANGELOG/AI-logg)

Alle større endringer ble testet før de ble beholdt, og jeg beholdt kun løsninger som faktisk fungerte i praksis.

---

## Eksempler på konkret KI-bruk
- KI foreslo hvordan jeg kunne lage en egen `auth_base.html` for innlogging
- KI forklarte hvorfor dashboard og innlogging ikke burde være på samme side
- KI hjalp meg å rydde opp i CSS uten å ødelegge eksisterende kode
- KI forklarte hvordan Jinja-arv fungerer (`extends`, `block`)
- KI hjalp med feilsøking av routing og endpoint-konflikter i Flask
- KI ble brukt til å skrive ryddige og strukturerte changelogs og commit-meldinger

---

## Viktig vurdering
KI ble brukt som et **verktøy**, ikke som en erstatning for egen innsats.  
Jeg brukte KI på samme måte som dokumentasjon, Stack Overflow eller lærebok.

- Jeg forstod endringene før jeg beholdt dem
- Jeg testet alltid løsninger selv
- Jeg tok egne valg basert på prosjektkrav
- Jeg har oversikt over hvordan løsningen fungerer

Prosjektet er mitt eget arbeid, der KI har vært en støtte for læring, feilsøking og kvalitet – ikke en automatisk generator av ferdig løsning.
