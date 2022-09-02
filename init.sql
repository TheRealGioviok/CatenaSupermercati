-- Promozione (ID_promo, tier, punti, data_inizio, data_fine)
-- PromoProdotto (ID_promo, ID_prodotto)
-- Prodotto (ID_prodotto, nome, codice_barre, prezzo)
-- ProdottoCarrello (ID_prodotto, ID_carrello, quantità)
-- Carrello (ID_carrello)
-- Cassa (ID_cassa, punto_vendita, numero_cassa)
-- Pagamento (ID_pagamento, data_ora, ammontare)
-- Cliente (ID_cliente, ID_tessera, nome_cognome, data_nascita, codice_fiscale)
-- Acquisto (ID_acquisto, ID_carrello, ID_pagamento, ID_cliente, ID_cassa)
-- Tessera (ID_tessera, ID_cliente, tier, punti)
-- PuntoVendita (ID_punto, nome, locazione)
-- Merce (ID_merce, ID_punto, ID_lotto, prodotto, quantità, in_esposizione)
-- Lotto (ID_lotto, ID_consegna, prodotto, quantità, scadenza)
-- Consegna (ID_consegna, ID_punto, data)

DROP TABLE IF EXISTS Promozione;
DROP TABLE IF EXISTS PromoProdotto;
DROP TABLE IF EXISTS Prodotto;
DROP TABLE IF EXISTS ProdottoCarrello;
DROP TABLE IF EXISTS Carrello;
DROP TABLE IF EXISTS Cassa;
DROP TABLE IF EXISTS Pagamento;
DROP TABLE IF EXISTS Cliente;
DROP TABLE IF EXISTS Acquisto;
DROP TABLE IF EXISTS Tessera;
DROP TABLE IF EXISTS PuntoVendita;
DROP TABLE IF EXISTS Merce;
DROP TABLE IF EXISTS Lotto;
DROP TABLE IF EXISTS Consegna;

CREATE TABLE Promozione (
    ID_promo INT NOT NULL AUTO_INCREMENT,
    tier BIT(2) NOT NULL,
    punti INT NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE NOT NULL,
    PRIMARY KEY (ID_promo)
);

CREATE TABLE Prodotto (
    ID_prodotto INT NOT NULL AUTO_INCREMENT,
    nome CHAR(32) NOT NULL,
    prezzo DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (ID_prodotto)

);

CREATE TABLE PromoProdotto (
    ID_promo INT NOT NULL AUTO_INCREMENT,
    ID_prodotto INT NOT NULL,
    PRIMARY KEY (ID_promo, ID_prodotto),
    FOREIGN KEY (ID_promo) REFERENCES Promozione(ID_promo),
    FOREIGN KEY (ID_prodotto) REFERENCES Prodotto(ID_prodotto)
);

CREATE TABLE Carrello (
    ID_carrello INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (ID_carrello)
);

CREATE TABLE ProdottoCarrello (
    ID_prodotto INT NOT NULL AUTO_INCREMENT,
    ID_carrello INT NOT NULL,
    quantità INT NOT NULL,
    PRIMARY KEY (ID_prodotto, ID_carrello),
    FOREIGN KEY (ID_prodotto) REFERENCES Prodotto(ID_prodotto),
    FOREIGN KEY (ID_carrello) REFERENCES Carrello(ID_carrello)
);

CREATE TABLE PuntoVendita (
    ID_punto INT NOT NULL AUTO_INCREMENT,
    nome CHAR(32) NOT NULL,
    locazione CHAR(64) NOT NULL,
    PRIMARY KEY (ID_punto)
);

CREATE TABLE Cassa (
    ID_cassa INT NOT NULL AUTO_INCREMENT,
    ID_punto INT NOT NULL,
    numero_cassa INT NOT NULL,
    PRIMARY KEY (ID_cassa),
    FOREIGN KEY (ID_punto) REFERENCES PuntoVendita(ID_punto)
);

CREATE TABLE Consegna (
    ID_consegna INT NOT NULL AUTO_INCREMENT,
    ID_punto INT NOT NULL,
    data DATE NOT NULL,
    PRIMARY KEY (ID_consegna),
    FOREIGN KEY (ID_punto) REFERENCES PuntoVendita(ID_punto)
);

CREATE TABLE Lotto (
    ID_lotto INT NOT NULL AUTO_INCREMENT,
    ID_consegna INT NOT NULL,
    ID_prodotto INT NOT NULL,
    codice_barre CHAR(80) NOT NULL,
    scadenza DATE NOT NULL,
    PRIMARY KEY (ID_lotto),
    FOREIGN KEY (ID_consegna) REFERENCES Consegna(ID_consegna),
    FOREIGN KEY (ID_prodotto) REFERENCES Prodotto(ID_prodotto)
);

CREATE TABLE Merce (
    ID_merce INT NOT NULL AUTO_INCREMENT,
    ID_punto INT NOT NULL,
    ID_lotto INT NOT NULL,
    ID_prodotto INT NOT NULL,
    quantità INT NOT NULL,
    in_esposizione BOOLEAN NOT NULL,
    PRIMARY KEY (ID_merce),
    FOREIGN KEY (ID_punto) REFERENCES PuntoVendita(ID_punto),
    FOREIGN KEY (ID_lotto) REFERENCES Lotto(ID_lotto),
    FOREIGN KEY (ID_prodotto) REFERENCES Prodotto(ID_prodotto)
);

CREATE TABLE Pagamento (
    ID_pagamento INT NOT NULL AUTO_INCREMENT,
    data_ora DATETIME NOT NULL,
    ammontare DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (ID_pagamento)
);

CREATE TABLE Cliente (
    ID_cliente INT NOT NULL AUTO_INCREMENT,
    nome_cognome CHAR(64) NOT NULL,
    data_nascita DATE NOT NULL,
    codice_fiscale CHAR(16) NOT NULL,
    PRIMARY KEY (ID_cliente)
);

CREATE TABLE Tessera (
    ID_tessera INT NOT NULL AUTO_INCREMENT,
    ID_cliente INT NOT NULL,
    tier BIT(2) NOT NULL,
    punti INT NOT NULL,
    PRIMARY KEY (ID_tessera),
    FOREIGN KEY (ID_cliente) REFERENCES Cliente(ID_cliente)
);


CREATE TABLE Acquisto (
    ID_acquisto INT NOT NULL AUTO_INCREMENT,
    ID_carrello INT NOT NULL,
    ID_pagamento INT NOT NULL,
    ID_cliente INT, -- In quanto un cliente non registrato può comunque fare acquisti
    ID_cassa INT NOT NULL,
    PRIMARY KEY (ID_acquisto),
    FOREIGN KEY (ID_carrello) REFERENCES Carrello(ID_carrello),
    FOREIGN KEY (ID_pagamento) REFERENCES Pagamento(ID_pagamento),
    FOREIGN KEY (ID_cliente) REFERENCES Cliente(ID_cliente),
    FOREIGN KEY (ID_cassa) REFERENCES Cassa(ID_cassa)
);

