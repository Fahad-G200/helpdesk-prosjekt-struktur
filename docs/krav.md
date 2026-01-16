# Behov og krav – Helpdesk og kunnskapsbase

## Bakgrunn
Mange elever og ansatte opplever IT-problemer som små feil, manglende tilgang eller spørsmål om programvare. Ofte blir dette håndtert muntlig eller tilfeldig, noe som gjør det vanskelig å holde oversikt og følge opp saker.

Dette prosjektet skal lage en enkel helpdesk-løsning som gir bedre struktur, oversikt og dokumentasjon av IT-henvendelser.

---

## Behovskartlegging

### Brukere (elever/ansatte)
Brukere trenger:
- En enkel måte å melde inn IT-problemer på
- Oversikt over egne saker og status
- Tydelig informasjon om hva de kan gjøre selv
- Enkle og forståelige veiledninger

### IT-support
IT-support trenger:
- Oversikt over alle innmeldte saker
- Mulighet til å prioritere og oppdatere saker
- Et system for å gi svar og veiledning
- Dokumentasjon på vanlige problemer og løsninger

---

## Funksjonelle krav

### Krav for bruker
- Bruker skal kunne logge inn
- Bruker skal kunne opprette en ny supportsak
- Bruker skal kunne se status på egne saker
- Bruker skal kunne lese kunnskapsartikler

### Krav for support/admin
- Support skal kunne se alle saker
- Support skal kunne endre status på saker
- Support skal kunne svare på saker
- Support skal kunne opprette og redigere kunnskapsartikler

---

## Ikke-funksjonelle krav
- Løsningen skal være enkel å bruke
- Grensesnittet skal være ryddig og forståelig
- Systemet skal være sikkert med innlogging og roller
- Løsningen skal være lett å videreutvikle

---

## Avgrensninger
- Prosjektet er en enkel prototype (versjon 1.0)
- Avansert sikkerhet som tofaktor og HTTPS er ikke med i første versjon
- Fokus er på funksjon, struktur og dokumentasjon

---

## Videre utvikling
I senere versjoner kan prosjektet utvides med:
- Bedre sikkerhet (HTTPS, sterkere autentisering)
- Varsler på e-post
- Mer avansert statistikk og rapporter

### Opprette sak
**Akseptansekriterier**
- Bruker kan ikke opprette sak uten tittel
- Sak lagres i databasen
- Sak får status "Åpen"
