# CatenaSupermercati
Progetto Basi di Dati
## Setup ##
Per setuppare il progetto, caricare sul motore mysql i file ```init.sql``` e ```operation.sql``` in sequenza.
Per setuppare i dati di esempio, caricare i file ```1.sql```,```2.sql```,```3.sql```,```4.sql```,```5.sql``` in sequenza.<p>
Essi generano un supermercato con una cassa, una consegna con diversi lotti di diversi prodotti, spostandone alcuni in esposizione, attivando inoltre promozioni su alcuni prodotti.<p>
Per installare i moduli richiesti per eseguire ```app.py```, basta usare il comando ```pip install -r requirements.txt```.<p>
Inoltre è presente un file, ```app.pyw``` contenente lo stesso codice di ```app.py```, avviato però senza finestra di terminale.

## Generazione custom dei dati ##
Il file ```datageneration.py``` include la logica di generazione dei dati di esempio del database.
Per eseguirlo, sono necessari i moduli elencati in ```datagenrequirements.txt```. Per installarli, basta usare il comando ```pip install -r datagenrequirements.txt```.<p>
Qualora volesse solo cambiarsi il numero di dati generati, basta avviare lo script da linea di comando come segue:<p>
```python datageneration.py [numberofnames] [numberofproducts] [numberoflots]```.<p>
Questo permette di modificare alcuni parametri. Si nota che il numero di promozioni generate è un quarto del numero di prodotti, e che il 70% dei prodotti verrà associato ad una promozione.

## Uso dell'interfaccia grafica ##
Avviare semplicemente con ```app.py [checkoutId]```. ```checkoutID``` identifica la cassa che esegue l'interfaccia grafica.  Se non specificato, defaulta a ```1```.<p>
Per il corretto funzionamento della GUI, si presuppone l'accesso su rete locale comune al database che deve essere chiamato ```catena```, che è il nome dato in ```init.sql```.
### Aggiungere e rimuovere prodotti ###
L'interfaccia grafica permette di aggiungere e togliere merce dal carrello in base ad un codice a barre. 
Il comportamento dello scanner viene simulato da un box di input.
Il box di input supporta, oltre che all'input tastiera classico, le shortcut seguenti:
 - ```CTRL``` + ```BACKSPACE``` : Cancella l'intera stringa nel box
 - ```CTRL``` + ```V```         : Incolla i contenuti della clipboard nel box
Accanto ad esso, può essere inserita una quantità: positiva per aggiungere un prodotto, negativa per toglierlo.
### Aggiungere una tessera fedeltà ###
Può anche essere selezionata una tessera cliente. Il comportamento dello scanner tessere è, ancora una volta, simulato da un input box.
### Applicare sconti, calcolare il totale, eseguire o annullare acquisto ###
Ci sono 4 pulsanti colorati, ognuno con una funzione diversa:
 - ```=``` (pulsante verde)     : permette di finalizzare l'acquisto, dovrebbe essere premuto solo dopo aver "ricevuto" il pagamento
 - ```UP!``` (pulsante blu)     : pulsante toggle, permette di scegliere se usare o meno i punti della tessera fedeltà. Non ha effetto se non è stata selezionata una tessera.
 - ```X``` (pulsante rosso)     : cancella tutti i dati di acquisto, resettando anche il cliente e tessera scansionata
 - ```Calc``` (pulsante giallo) : calcola il prezzo totale ed eventuale sconto, mostrandolo in alto a destra. Lo sconto è non nullo solo se c'è una tessera fedeltà
## Esempio aspetto della GUI ## 
![immagine](https://user-images.githubusercontent.com/64363733/188345401-11fbbddf-fc9c-4233-add5-431e8783dbd6.png)
