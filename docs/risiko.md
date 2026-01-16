# Risikoanalyse

| Trussel | Konsekvens | Tiltak |
|-------|------------|--------|
| Svake passord | Uautorisert tilgang | Passord hashes og valideres |
| Datatap | Tap av brukersaker | Regelmessig backup anbefales |
| Uautorisert tilgang | Brudd på personvern | Rollebasert tilgang (bruker/support) |
| SQL-injeksjon | Datamanipulering | Bruk av parameteriserte spørringer |
| Feilkonfigurasjon | Tjenesten nede | Docker for konsistent drift |
