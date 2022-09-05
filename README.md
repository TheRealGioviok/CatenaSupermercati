# CatenaSupermercati
Progetto Basi di Dati
## Setup ##
Per setuppare il progetto, caricare sul motore mysql i file ```init.sql``` e ```operation.sql``` in sequenza.
Per setuppare i dati di esempio, caricare i file ```1.sql```,```2.sql```,```3.sql```,```4.sql```,```5.sql``` in sequenza.
Per installare i moduli richiesti per eseguire ```app.py```, basta usare il comando ```pip install -r requirements.txt```.

## Uso dell'interfaccia grafica ##
Avviare semplicemente con ```app.py [checkoutId]```. ```checkoutID``` identifica la cassa che esegue l'interfaccia grafica.  Se non specificato, defaulta a ```0```.
Per il corretto funzionamento della GUI, si presuppone l'accesso su rete locale comune al database.
### Aggiungere e rimuovere prodotti ###
L'interfaccia grafica permette di aggiungere e togliere merce dal carrello in base ad un codice a barre. 
Il comportamento dello scanner viene simulato da un box di input.
Accanto ad esso, può essere inserita una quantità: positiva per aggiungere un prodotto, negativa per toglierlo.
### Aggiungere una tessera fedeltà ###
Può anche essere selezionata una tessera cliente. Il comportamento dello scanner tessere è, ancora una volta, simulato da un input box.
### Applicare sconti, calcolare il totale, eseguire o annullare acquisto ###
Ci sono 4 pulsanti colorati, ognuno con una funzione diversa:
 - ```=``` (pulsante verde)     : permette di finalizzare l'acquisto, dovrebbe essere premuto solo dopo aver "ricevuto" il pagamento
 - ```UP!``` (pulsante blu)     : pulsante toggle, permette di scegliere se usare o meno i punti della tessera fedeltà. Non ha effetto se non è stata selezionata una tessera.
 - ```X``` (pulsante rosso)     : cancella tutti i dati di acquisto, resettando anche il cliente e tessera scansionata
 - ```Calc``` (pulsante giallo) : calcola il prezzo totale ed eventuale sconto, mostrandolo in alto a destra. Lo sconto è non nullo solo se c'è una tessera fedeltà
