# Personvern og sikkerhet – Helpdesk og kunnskapsbase

## Hva slags data systemet lagrer
Systemet skal lagre det som trengs for å kunne gi brukerstøtte og følge opp saker.

Eksempler på data:
- brukernavn (evt. e-post)
- passord (skal aldri lagres i klartekst)
- supportsaker (tittel, beskrivelse, status, dato)
- svar/kommentarer fra support
- kunnskapsartikler (veiledninger)

---

## Dataminimering (vi lagrer bare det som er nødvendig)
For å ta hensyn til personvern lagres kun informasjon som trengs for:
- innlogging
- oppfølging av saker
- dokumentasjon av løsning

Systemet skal ikke lagre:
- fødselsnummer
- privat adresse
- unødvendig sensitive opplysninger

Hvis en bruker skriver inn sensitiv informasjon i en ticket, bør support be brukeren fjerne det.

---

## Tilgangsstyring (roller)
Løsningen bruker roller for å hindre at feil personer får tilgang.

- **Bruker**
  - kan se og redigere egne saker
  - kan lese kunnskapsartikler

- **Support/Admin**
  - kan se alle saker
  - kan svare og oppdatere status
  - kan publisere veiledninger

Dette hindrer at en vanlig bruker kan se andre sine saker.

---

## Passord og innlogging
Passord skal behandles sikkert:
- passord lagres ikke som vanlig tekst
- passord skal hashe(s) (kryptert lagring)
- systemet skal kunne håndtere feil innlogging uten å gi for mye informasjon

---

## Logging (med tanke på personvern)
Logger brukes for feilsøking og drift, men skal ikke inneholde sensitive data.

Eksempler på det som kan logges:
- at en sak ble opprettet
- at en status ble endret
- feil i systemet (uten passord/persondata)

Eksempler på det som ikke skal logges:
- passord
- hele innholdet i en ticket hvis den kan inneholde sensitive data

---

## Risiko og tiltak (enkelt)
Mulige risikoer:
- en bruker får tilgang til andre sine saker
- passord kommer på avveie
- database blir tilgjengelig fra feil sted
- data blir slettet uten backup

Tiltak:
- rollebasert tilgangsstyring
- hashing av passord
- database kun tilgjengelig internt (segmentering)
- backup-script (planlagt i `infra/scripts/backup.sh`)

---

## Videre forbedringer (senere versjoner)
- HTTPS (kryptert trafikk) hvis løsningen publiseres på nett
- strengere passordkrav
- automatisk utlogging etter tid
- bedre rutiner for sletting/arkivering av gamle saker