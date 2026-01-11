# Risikoanalyse – Helpdesk-løsning

## Formål
Formålet med risikoanalysen er å identifisere mulige trusler mot systemet og foreslå tiltak som reduserer risikoen for datatap, misbruk eller driftsstans.

## Identifiserte risikoer og tiltak

### 1. Uautorisert tilgang til brukerkontoer
- **Risiko:** Brukere kan få tilgang til andres kontoer
- **Tiltak:** Passord hashes, rollebasert tilgang, begrenset innsyn

### 2. Datatap
- **Risiko:** Database kan bli slettet eller ødelagt
- **Tiltak:** Regelmessig backup av database

### 3. Injeksjonsangrep (XSS / SQL)
- **Risiko:** Ondsinnet input fra brukere
- **Tiltak:** Input-validering og bruk av parameteriserte SQL-spørringer

### 4. Misbruk av systemet
- **Risiko:** Brukere kan sende inn upassende eller sensitive data
- **Tiltak:** Veiledning til brukere og manuell kontroll av saker

## Vurdering
Med foreslåtte tiltak vurderes risikoen som lav til middels. Løsningen er egnet som skole- og prototypeprosjekt.