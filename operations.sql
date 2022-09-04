DROP PROCEDURE IF EXISTS caricaCatalogo;
DROP PROCEDURE IF EXISTS caricaCodiciProdotto;
DROP PROCEDURE IF EXISTS caricaPromozioni;
DROP FUNCTION IF EXISTS aggiungiProdotto;
DROP FUNCTION IF EXISTS aggiungiPuntoVendita;
DROP FUNCTION IF EXISTS aggiungiConsegna;
DROP FUNCTION IF EXISTS aggiungiLotto;
DROP FUNCTION IF EXISTS spostaMerce;
DROP PROCEDURE IF EXISTS selDisponibilità;
DROP FUNCTION IF EXISTS getDisponibilità;
DROP PROCEDURE IF EXISTS getScaduti; 
DROP FUNCTION IF EXISTS rimuoviScaduti;
DROP FUNCTION IF EXISTS getNomePuntoVendita;
DROP FUNCTION IF EXISTS aggiungiCarrello;
DROP FUNCTION IF EXISTS aggiungiPagamento;
DROP FUNCTION IF EXISTS aggiungiProdottoCarrello;
DROP FUNCTION IF EXISTS aggiungiAcquisto;

-- La procedura caricaCatalogo (OP.1a) restituisce il catalogo di prodotti.

DELIMITER $$
CREATE PROCEDURE caricaCatalogo ()
BEGIN
    SELECT * FROM Prodotto;
END $$
DELIMITER ;

-- La procedura caricaCodiciProdotto (OP.1b) restituisce i codici a barre dei prodotti in esposizione in un dato punto vendita, associati al prodotto.

DELIMITER $$
CREATE PROCEDURE caricaCodiciProdotto (ID_punto INT)
BEGIN
    SELECT Merce.ID_prodotto, Lotto.codice_barre FROM Merce, Lotto WHERE Merce.ID_punto = ID_punto AND Merce.in_esposizione = 1 AND Merce.ID_lotto = Lotto.ID_lotto;
END $$
DELIMITER ;


-- La procedura caricaPromozioni (OP.2) restituisce le promozioni attive associate

DELIMITER $$
CREATE PROCEDURE caricaPromozioni ()
BEGIN
    SELECT Promozione.ID_promo, Promozione.punti, Promozione.tier, PromoProdotto.ID_prodotto FROM Promozione, PromoProdotto WHERE data_inizio <= CURRENT_DATE AND data_fine >= CURRENT_DATE AND Promozione.ID_promo = PromoProdotto.ID_promo;
END $$
DELIMITER ;


-- La funzione aggiungiProdotto (OP.3) aggiunge un prodotto al database

DELIMITER $$
CREATE FUNCTION aggiungiProdotto (nome CHAR(32), prezzo DECIMAL(12,2))
RETURNS INT
BEGIN
    DECLARE ID_prodotto INT;

    INSERT INTO Prodotto (nome, prezzo) VALUES (nome, prezzo);
    SELECT LAST_INSERT_ID() INTO ID_prodotto;

    RETURN ID_prodotto;
END $$
DELIMITER ;


-- La funzione aggiungiPuntoVendita (OP.4) aggiunge un punto vendita al database
-- aggiunge inoltre delle casse, in base al numero di casse passato come parametro

DELIMITER $$
CREATE FUNCTION aggiungiPuntoVendita (nome CHAR(32), locazione CHAR(64), numero_casse INT)
RETURNS INT
BEGIN
    DECLARE ID_punto_vendita INT;
    DECLARE COUNTER INT DEFAULT 1;
    -- Aggiungi il punto vendita
    INSERT INTO PuntoVendita (nome, locazione) VALUES (nome, locazione);
    SELECT LAST_INSERT_ID() INTO ID_punto_vendita;
	
    WHILE COUNTER <= numero_casse
    DO
    	INSERT INTO cassa (ID_punto, numero_cassa) VALUES (ID_punto_vendita, COUNTER);
    	SET COUNTER := COUNTER + 1;
    END WHILE;
    RETURN ID_punto_vendita;
END $$
DELIMITER ;


-- L'operazione 5 è divisa in 2 parti:
-- Aggiunta della consegna
-- Aggiunta dei lotti (anche in magazzino)

-- La funzione aggiungiConsegna (OP.5.1) aggiunge una consegna al database

DELIMITER $$
CREATE FUNCTION aggiungiConsegna (ID_punto_vendita INT, data_consegna DATE)
RETURNS INT
BEGIN
    DECLARE ID_consegna INT;
    -- Controlla che la consegna non sia già presente nel database
    IF EXISTS (SELECT * FROM Consegna WHERE Consegna.ID_punto = ID_punto_vendita AND Consegna.data = data_consegna) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Consegna già presente nel database';
        return NULL;
    END IF;
    INSERT INTO Consegna (ID_punto, data) VALUES (ID_punto_vendita, data_consegna);
    SELECT LAST_INSERT_ID() INTO ID_consegna;
    RETURN ID_consegna;
END $$
DELIMITER ;

-- La funzione aggiungiLotto (OP.5.2) aggiunge un lotto al database

DELIMITER $$
CREATE FUNCTION aggiungiLotto (ID_prodotto INT, quantità INT, codice_barre CHAR(80), ID_consegna INT, scadenza DATE)
RETURNS INT
BEGIN
    DECLARE ID_lotto INT;
    DECLARE ID_punto INT;
    -- Controlla che il prodotto sia presente nel database
    IF NOT EXISTS (SELECT * FROM Prodotto WHERE Prodotto.ID_prodotto = ID_prodotto) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prodotto non presente nel database';
        return NULL;
    END IF;
    -- Controlla che il lotto non sia già presente nel database
    IF EXISTS (SELECT * FROM Lotto WHERE Lotto.ID_prodotto = ID_prodotto AND Lotto.ID_consegna = ID_consegna) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lotto già presente nel database';
        return NULL;
    END IF;
    -- Controlla che la consegna sia presente nel database
    IF NOT EXISTS (SELECT * FROM Consegna WHERE Consegna.ID_consegna = ID_consegna) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Consegna non presente nel database';
        return NULL;
    END IF;
    -- Controlla che la quantità sia maggiore di 0
    IF quantita < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantità non valida';
        return NULL;
    END IF;
    INSERT INTO Lotto (ID_prodotto, ID_consegna, codice_barre, scadenza) VALUES (ID_prodotto, ID_consegna, codice_barre, scadenza);
    SELECT LAST_INSERT_ID() INTO ID_lotto;
    SELECT Consegna.ID_punto INTO ID_punto FROM Consegna WHERE Consegna.ID_consegna = ID_consegna;
    -- Aggiungi la merce al magazzino
    INSERT INTO Merce (ID_punto, ID_lotto, ID_prodotto, quantità, in_esposizione) VALUES (ID_punto, ID_lotto, ID_prodotto, quantita, 0);
    RETURN ID_lotto;

END $$
DELIMITER ;


-- Operazione 6 : sposta merce da magazzino a esposizione:
-- Se la quantità in magazzino è minore della quantità da spostare,
-- restituisce un errore
-- Se la quantità in magazzino è maggiore o uguale a quella in esposizione,
-- diminuisce la quantità in magazzino e aumenta quella in esposizione (creandola, se necessario)
-- Se la quantità in magazzino è 0, la merce viene rimossa dal magazzino

DELIMITER $$
CREATE FUNCTION spostaMerce (ID_punto INT, codice_barre CHAR(80), quantitàSpostamento INT)
RETURNS INT
BEGIN
    DECLARE ID_prodotto INT;
    DECLARE ID_merce_magazzino INT DEFAULT 0;
    DECLARE ID_merce_esposizione INT DEFAULT 0;
    DECLARE quantita_merce_magazzino INT;
    DECLARE ID_lotto INT;
    SELECT Lotto.ID_lotto INTO ID_lotto FROM Lotto WHERE Lotto.codice_barre = codice_barre;
    
    SELECT Merce.ID_merce INTO ID_merce_magazzino FROM Merce WHERE Merce.ID_lotto = ID_lotto AND Merce.ID_punto = ID_punto AND Merce.in_esposizione = 0;
    SELECT Merce.ID_merce INTO ID_merce_esposizione FROM Merce WHERE Merce.ID_lotto = ID_lotto AND Merce.ID_punto = ID_punto AND Merce.in_esposizione = 1;
    
    
    -- Controlla che il lotto sia presente in magazzino
    IF ID_merce_magazzino = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lotto non presente in magazzino';
        return NULL;
    END IF;
    -- Controlla che ci sia abbastanza merce in magazzino
    SELECT quantità INTO quantita_merce_magazzino FROM Merce WHERE ID_merce = ID_merce_magazzino;
    IF quantita_merce_magazzino < quantitàSpostamento THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantità insufficiente in magazzino';
        return NULL;
    END IF;
    -- Controlla che la quantità sia maggiore di 0
    IF quantitàSpostamento < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantità non valida';
        return NULL;
    END IF;
    -- Se esiste già una merce in esposizione con lo stesso lotto, aggiorna solo la quantità
    -- Se non esiste, crea una nuova merce in esposizione
    -- Dopo aver aggiornato la quantità in magazzino, aggiorna la quantità in esposizione
    -- Infine, se la quantità in magazzino è 0, rimuove la merce dal magazzino

    IF ID_merce_esposizione = 0 THEN
        SELECT Merce.ID_prodotto from Merce WHERE Merce.ID_merce = ID_merce_magazzino INTO ID_prodotto;
        INSERT INTO Merce (ID_punto, ID_lotto, ID_prodotto, quantità, in_esposizione) VALUES (ID_punto, ID_lotto, ID_prodotto, quantitàSpostamento, 1);
        SELECT LAST_INSERT_ID() INTO ID_merce_esposizione;
    ELSE
        UPDATE Merce SET quantità = quantità + quantitàSpostamento WHERE ID_merce = ID_merce_esposizione;
    END IF;

    UPDATE Merce SET quantità = quantità - quantitàSpostamento WHERE ID_merce = ID_merce_magazzino;

    SELECT quantità INTO quantita_merce_magazzino FROM Merce WHERE ID_merce = ID_merce_magazzino;

    IF quantita_merce_magazzino = 0 THEN
        DELETE FROM Merce WHERE ID_merce = ID_merce_magazzino;
    END IF;

    RETURN ID_merce_magazzino;
END $$
DELIMITER ;


-- Operazione 7 : Operazioni di un acquisto:
-- Questa operazione è divisa in diverse parti:

-- Aggiunta di un carrello;
-- Aggiunta di un pagamento;
-- Aggiunta di un prodotto al carrello;
-- Aggiunta di un acquisto
-- Aggiunta / rimozione di punti fedeltà
-- Rimozione di prodotti dall'esposizione


DELIMITER $$
CREATE FUNCTION aggiungiCarrello ()
RETURNS INT
BEGIN
    DECLARE ID_carrello INT;
    INSERT INTO Carrello () VALUES ();
    SELECT LAST_INSERT_ID() INTO ID_carrello;
    RETURN ID_carrello;
END $$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION aggiungiPagamento (data_ora DATETIME, ammontare DECIMAL(12,2))
RETURNS INT
BEGIN
    DECLARE ID_pagamento INT;
    INSERT INTO Pagamento (data_ora, ammontare) VALUES (data_ora, ammontare);
    SELECT LAST_INSERT_ID() INTO ID_pagamento;
    RETURN ID_pagamento;
END $$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION aggiungiProdottoCarrello (ID_carrello INT, codice_barre char(80), quantitàAggiunta INT)
RETURNS INT
BEGIN
    -- Se il prodotto è già presente nel carrello, aggiorna la quantità
    -- Se il prodotto non è presente nel carrello, aggiunge il prodotto al carrello
    DECLARE q_prodotto_carrello INT DEFAULT 0;
    DECLARE ID_merce INT;
    DECLARE ID_prodotto INT;
    DECLARE ID_lotto INT;
    SELECT Lotto.ID_lotto INTO ID_lotto FROM Lotto WHERE Lotto.codice_barre = codice_barre;
    SELECT Lotto.ID_prodotto INTO ID_prodotto FROM Lotto WHERE Lotto.codice_barre = codice_barre;

    -- Controlla che ci sia abbastanza merce
    IF (SELECT quantità from Merce WHERE Merce.ID_lotto = ID_lotto AND in_esposizione = 1) < quantitàAggiunta THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantità insufficiente in esposizione';
        return NULL;
    END IF;

    SELECT ProdottoCarrello.quantità INTO q_prodotto_carrello FROM ProdottoCarrello WHERE ProdottoCarrello.ID_carrello = ID_carrello AND ProdottoCarrello.ID_prodotto = ID_prodotto;
    
    IF q_prodotto_carrello = 0 THEN
    	INSERT INTO ProdottoCarrello (ID_carrello, ID_prodotto, quantità) VALUES (ID_carrello, ID_prodotto, quantitàAggiunta);
    ELSE
    	UPDATE ProdottoCarrello SET quantità = quantità + quantitàAggiunta WHERE ProdottoCarrello.ID_carrello = ID_carrello AND ProdottoCarrello.ID_prodotto = ID_prodotto;
    END IF;
    
    -- Rimuove il prodotto dall'esposizione
    UPDATE Merce SET quantità = quantità - quantitàAggiunta WHERE Merce.ID_lotto = ID_lotto AND in_esposizione = 1 ;
    -- Se la quantità è 0, rimuove il prodotto dall'esposizione
    DELETE FROM Merce WHERE quantità = 0 AND in_esposizione = 1;
    
    SELECT ProdottoCarrello.quantità INTO q_prodotto_carrello FROM ProdottoCarrello WHERE ProdottoCarrello.ID_carrello = ID_carrello AND ProdottoCarrello.ID_prodotto = ID_prodotto;
    
    return q_prodotto_carrello;
   
END $$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION aggiungiAcquisto (ID_carrello INT, ID_cassa INT, ID_pagamento INT, ID_tessera INT, puntiDiff INT)
RETURNS INT
BEGIN
    -- Aggiunge un acquisto al database
    DECLARE ID_acquisto INT;
    DECLARE ID_clienteAcquistante INT DEFAULT NULL;
    

    -- Controlla che nessun acquisto abbia lo stesso pagamento o lo stesso carrello
    SELECT ID_acquisto INTO ID_acquisto FROM Acquisto WHERE Acquisto.ID_carrello = ID_carrello OR Acquisto.ID_pagamento = ID_pagamento;
    IF ID_acquisto IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Acquisto già presente';
        return NULL;
    END IF;

    -- Cerca di trovare il cliente associato alla tessera (se esiste)
    IF ID_tessera <> 0 THEN
        SELECT ID_cliente INTO ID_clienteAcquistante FROM Tessera WHERE tessera.ID_tessera = ID_tessera;
    END IF;

    -- Se presente, aggiunge o sottrae i punti fedeltà alla tessera cliente
    IF ID_clienteAcquistante IS NOT NULL THEN
        UPDATE Tessera SET punti = punti + puntiDiff WHERE ID_cliente = ID_clienteAcquistante;
    END IF;

    -- Aggiunge l'acquisto al database
    INSERT INTO Acquisto (ID_carrello, ID_cassa, ID_pagamento, ID_cliente) VALUES (ID_carrello, ID_cassa, ID_pagamento, ID_clienteAcquistante);
    SELECT LAST_INSERT_ID() INTO ID_acquisto;
    RETURN ID_acquisto;
END $$
DELIMITER ;

-- Operazione 9: controllo della disponibilità di un prodotto

-- Diamo due versioni: la prima, restituisce direttamente la select, la seconda, restituisce una quantità (in esposizione)
DELIMITER $$
CREATE PROCEDURE selDisponibilità (ID_prodotto INT, ID_punto_vendita INT)
BEGIN
    SELECT ID_lotto, ID_prodotto, quantità, in_esposizione FROM Merce WHERE Merce.ID_prodotto = ID_prodotto AND ID_punto_vendita = ID_punto_vendita;
END $$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION getDisponibilità (ID_prodotto INT, ID_punto_vendita INT)
RETURNS INT
BEGIN
    DECLARE q_disponibile INT DEFAULT 0;
    SELECT SUM(quantità) INTO q_disponibile FROM Merce WHERE Merce.ID_prodotto = ID_prodotto AND in_esposizione = 1;
    RETURN q_disponibile;
END $$
DELIMITER ;

-- Operazione 10: rimozione della merce scaduta
DELIMITER $$
CREATE PROCEDURE getScaduti (ID_punto_vendita INT)
BEGIN
    SELECT * FROM Merce WHERE Merce.ID_punto_vendita = ID_punto_vendita AND Merce.ID_lotto IN (SELECT ID_lotto FROM Lotto WHERE Lotto.data_scadenza < CURDATE());
END $$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION rimuoviScaduti (ID_punto_vendita INT)
RETURNS INT
BEGIN
    DECLARE q_rimosse INT DEFAULT 0;
    SELECT COUNT(*) INTO q_rimosse FROM Merce WHERE Merce.ID_punto_vendita = ID_punto_vendita AND Merce.ID_lotto IN (SELECT ID_lotto FROM Lotto WHERE Lotto.data_scadenza < CURDATE());
    DELETE FROM Merce WHERE Merce.ID_punto_vendita = ID_punto_vendita AND Merce.ID_lotto IN (SELECT ID_lotto FROM Lotto WHERE Lotto.data_scadenza < CURDATE());
    RETURN q_rimosse;
END $$
DELIMITER ;

-- OP.11 : La funzione aggiungiCliente aggiunge un cliente al database, creando inoltre, se richiesto, una tessera
DELIMITER $$
CREATE FUNCTION aggiungiCliente (nome_cognome CHAR(64), data_nascita DATE, codice_fiscale CHAR(16), crea_tessera BOOLEAN, tier BIT(2))
RETURNS INT
BEGIN
    DECLARE ID_cliente_aggiunto INT;
    DECLARE ID_tessera_aggiunta INT;

    INSERT INTO Cliente (nome_cognome, data_nascita, codice_fiscale) VALUES (nome_cognome, data_nascita, codice_fiscale);
    SELECT LAST_INSERT_ID() INTO ID_cliente_aggiunto;

    IF crea_tessera THEN
        INSERT INTO Tessera (tier, ID_cliente) VALUES (tier, ID_cliente_aggiunto);
        SELECT LAST_INSERT_ID() INTO ID_tessera_aggiunta;

    END IF;

    RETURN ID_cliente_aggiunto;
END $$
DELIMITER ;

-- OP.12 : La funzione aggiungiTessera aggiunge una tessera al database, collegandola ad un cliente già esistente
DELIMITER $$
CREATE FUNCTION aggiungiTessera (ID_cliente INT, tier BIT(2))
RETURNS INT
BEGIN
    DECLARE ID_tessera_aggiunta INT;

    INSERT INTO Tessera (tier, ID_cliente) VALUES (tier, ID_cliente);
    SELECT LAST_INSERT_ID() INTO ID_tessera_aggiunta;

    RETURN ID_tessera_aggiunta;
END $$
DELIMITER ;

-- Op.13 : la funzione getNomePuntoVendita restituisce il nome di un punto vendita dato l'ID di una cassa
DELIMITER $$
CREATE FUNCTION getNomePuntoVendita (ID_cassa INT)
RETURNS CHAR(64)
BEGIN
    DECLARE nome_punto_vendita CHAR(64);
    SELECT nome INTO nome_punto_vendita FROM PuntoVendita WHERE PuntoVendita.ID_punto = (SELECT ID_punto FROM Cassa WHERE Cassa.ID_cassa = ID_cassa);
    RETURN nome_punto_vendita;
END $$
DELIMITER ;







