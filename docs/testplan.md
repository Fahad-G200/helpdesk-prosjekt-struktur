# Testplan – Helpdesk og kunnskapsbase

## Formål
Formålet med testing er å sikre at helpdesk-løsningen fungerer som forventet før og under bruk. Testing skal avdekke feil tidlig og bidra til en stabil og brukervennlig løsning.

---

## Hva som testes
Følgende funksjoner skal testes:

- Innlogging
- Opprette ny supportsak
- Vise og oppdatere status på saker
- Svar fra IT-support
- Tilgangsstyring (bruker vs. support)
- Kunnskapsbase

---

## Testmiljø
- Lokal maskin
- VS Code
- Docker og Docker Compose
- Nettleser (Chrome / Firefox)

---

## Testmetoder

### Manuell testing
De fleste testene gjennomføres manuelt ved å bruke systemet slik en vanlig bruker ville gjort.

Eksempler:
- logge inn som bruker
- opprette sak
- sjekke at saken vises riktig
- logge inn som support og svare

---

### Enkel funksjonstesting
Hver funksjon testes separat for å kontrollere at:
- riktig input gir forventet resultat
- feil input håndteres på en trygg måte

---

## Testtilfeller

### Test 1: Innlogging
- **Handling:** logge inn med gyldig brukernavn og passord  
- **Forventet resultat:** brukeren blir logget inn  
- **Resultat:** OK / Ikke OK  

---

### Test 2: Feil innlogging
- **Handling:** logge inn med feil passord  
- **Forventet resultat:** feilmelding uten å avsløre detaljer  
- **Resultat:** OK / Ikke OK  

---

### Test 3: Opprette supportsak
- **Handling:** bruker oppretter ny sak  
- **Forventet resultat:** saken lagres og vises i listen  
- **Resultat:** OK / Ikke OK  

---

### Test 4: Rollebegrensning
- **Handling:** vanlig bruker prøver å se alle saker  
- **Forventet resultat:** tilgang nektes  
- **Resultat:** OK / Ikke OK  

---

### Test 5: Kunnskapsbase
- **Handling:** åpne en veiledning  
- **Forventet resultat:** innhold vises korrekt  
- **Resultat:** OK / Ikke OK  

---

## Dokumentasjon av feil
Hvis en test feiler:
- feilen beskrives kort
- årsak forsøkes identifisert
- løsning dokumenteres i CHANGELOG.md
- ny test kjøres etter fiks

---

## Videre testing
Etter hvert som nye funksjoner legges til, skal:
- nye tester legges inn i denne testplanen
- gamle tester kjøres på nytt for å sikre at ingenting har blitt ødelagt