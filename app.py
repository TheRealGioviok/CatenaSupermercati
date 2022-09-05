# Lets test the library

import mysql.connector
import sys

from GUI import *
barcodes = None
products = None
promotions = None
dbResponse = None
checkoutCode = 1
currentCard = None
currentTier = 0
currentCardPoints = 0
db = None

def moneyFormat(price):
    price = round(price, 2)
    string = str(round(price,2))
    # Add the right amount of zeros.
    # if price ends in .0
    if string[-2:] == ".0":
        # add a 0
        string += "0"
    elif price == int(price):
        string += ".00"
    return string

# The getCard function will return the card associated to a certain number.
def getCard(component):
    tiers = ["Family","Business","Enterprise"]
    global currentCard, currentTier, currentCardPoints, dbResponse, db
    
    gui = component.gui
    card = gui.getComponent("ibox3").getString(True)
    if card == "":
        return
    dbResponse.execute("SELECT * FROM Tessera WHERE ID_tessera = %s", (card,))
    card = dbResponse.fetchone()
    print("card->",card)
    if card:
        currentCard = card
        currentTier = card[2]
        print("Now current tier is", currentTier)
        currentCardPoints = card[3]
        # Lock the card info into the input box.
        gui.getComponent("ibox3").lock("ID: " + str(card[0]) + " - " + tiers[currentTier] + " - Punti: " + str(card[3]))
        # Lock the scan button.
        gui.getComponent("scan2Button").lock()
    else:
        currentCard = None
        currentTier = 0
        currentCardPoints = 0
        # Unlock the card info into the input box.
        gui.getComponent("ibox3").unlock()
        # Unlock the scan button.
        gui.getComponent("scan2Button").unlock()
        # Tell the user that the card is not valid.
        gui.getComponent("namePrice").setText("Tessera non valida!")

def terminateTransaction(component, nulled = False):
    global dbResponse, currentCard, currentCardPoints, currentTier
    gui = component.gui
    # Clear the list.
    gui.getComponent("list").clear()
    # Clear the barcode.
    gui.getComponent("ibox1").clear()
    # Clear the quantity.
    gui.getComponent("ibox2").clear()
    # Clear the total price.
    gui.getComponent("namePrice").setText("Acquisto " + ("annullato" if nulled else "terminato") + " con successo!")
    # Clear the current card
    gui.getComponent("ibox3").clear()
    currentCard = None
    currentCardPoints = 0
    currentTier = 0
    # Unlock the card info into the input box.
    gui.getComponent("ibox3").unlock()
    # Unlock the scan button.
    gui.getComponent("scan2Button").unlock()
    # return 
    return

def undoTransaction(component):
    terminateTransaction(component, True)

def calc(component):
    gui = component.gui
    # Now, we calculate the total price of the shoplist.
    # We do this withour using the database, because we have the list in memory.
    totalPrice = 0
    totalPoints = currentCardPoints

    llist = gui.getComponent("list")
    for item in llist.getItems():
        totalPrice += item.price
        # We update the currentCardPoints.
        totalPoints += item.points
    # Round the totalPrice to 2 decimals.
    totalPrice = round(totalPrice, 2)
    # Check if we want to use points.
    usePoints = gui.getComponent("usePoints").getChecked()
    # Calculate the discount.
    discount = 0
    usedPoints = 0
    originalPrice = totalPrice
    CHANGE = 0.1
    if usePoints:
        # Check how many points to use:
        # if the user more than enough points to pay, we don't want to overcharge him.

        if totalPoints > totalPrice / CHANGE:
            usedPoints = round(totalPrice / CHANGE)
            totalPrice = 0
            totalPoints -= usedPoints
        else:
            usedPoints = totalPoints
            totalPrice -= totalPoints * CHANGE
            totalPoints = 0

    pointDiff = totalPoints - currentCardPoints
    print("Pointdiff", pointDiff)
    # Display the total price and the used points.
    toShow = "Totale: " + moneyFormat(originalPrice) + "€ - " + moneyFormat(
        usedPoints * CHANGE) + " € = " + moneyFormat(totalPrice) + "€"
    gui.getComponent("namePrice").setText(toShow)
    return 

def pay(component):
    global dbResponse, currentCard, currentCardPoints, currentTier, checkoutCode
    gui = component.gui
    cartId = None
    # First, we create a new shoplist, and get back the id.
    dbResponse.execute("SELECT aggiungiCarrello()")
    cartId = dbResponse.fetchone()
    # Now, we calculate the total price of the shoplist.
    # We do this withour using the database, because we have the list in memory.
    totalPrice = 0
    totalPoints = currentCardPoints

    llist = gui.getComponent("list")
    for item in llist.getItems():
        totalPrice += item.price
        # We update the currentCardPoints.
        totalPoints += item.points
    # Round the totalPrice to 2 decimals.
    totalPrice = round(totalPrice, 2)
    # Check if we want to use points.
    usePoints = gui.getComponent("usePoints").getChecked()
    # Calculate the discount.
    discount = 0
    usedPoints = 0
    originalPrice = totalPrice
    CHANGE = 0.1
    if usePoints:
        # Check how many points to use:
        # if the user more than enough points to pay, we don't want to overcharge him.
        
        if totalPoints > totalPrice / CHANGE:
            usedPoints = round(totalPrice / CHANGE)
            totalPrice = 0
            totalPoints -= usedPoints
        else:
            usedPoints = totalPoints
            totalPrice -= totalPoints * CHANGE
            totalPoints = 0
    
    pointDiff = totalPoints - currentCardPoints
    print("Pointdiff", pointDiff)
    # Display the total price and the used points.
    toShow = "Totale: " + moneyFormat(originalPrice) + "€ - " + moneyFormat(usedPoints * CHANGE) + " € = " + moneyFormat(totalPrice) + "€"
    gui.getComponent("namePrice").setText(toShow)

    # We add a payment to the database.
    dbResponse.execute("SELECT aggiungiPagamento(NOW(), %s)", (totalPrice,))
    paymentId = dbResponse.fetchone()

    # Add the products to the cart.
    for item in llist.getItems():
        query = "SELECT aggiungiProdottoCarrello(%s, \"%s\", %s)"
        query = query % (cartId[0], item.barcode, item.quantity)
        print(query)
        dbResponse.execute(query)
        # print the result.
        print(dbResponse.fetchall())
    
    # Add the purchase to the database.
    query = "SELECT aggiungiAcquisto(%s, %s, %s, %s, %s)"
    query = query % (cartId[0], checkoutCode, paymentId[0], currentCard[0] if currentCard else "NULL", pointDiff)
    print(query)
    
    dbResponse.execute(query)
    # print the result.
    print(dbResponse.fetchall())

    # Happily commit the changes.
    db.commit()

    terminateTransaction(component, False)
    return

    



# The scanCode function will be called when the scan button is clicked.
# It will return the price associated with the product associated to the barcode.
def scanCode(barcodeQ, barcodes, products):
    
    # We will return the price of the product associated to the barcode.
    for barcode in barcodes:
        if barcode[1] == barcodeQ:
            for product in products:
                if product[0] == barcode[0]:
                    return product     
    return 0

# The scanCard function will be called when the scan card button is clicked.
# It will return the fidelity points associated to the card number.

def showScan(component):
    global barcodes, products, promotions
    gui = component.gui
    barcode = gui.getComponent("ibox1").getString(True)
    quantity = gui.getComponent("ibox2").getString(True)
    # convert to int
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1
    
    if quantity == 0:
        return
    
    
    namePriceText = gui.getComponent("namePrice")
    product = scanCode(barcode, barcodes, products)

    # Search for the best promotion for the product.
    
    
    toShow = ""
    
    if product == 0:
        toShow = "Prodotto non trovato"
    else:
        toShow = product[1] + " " + str(product[2]) + "€ x " + str(quantity) + " = " + str(round(product[2] * quantity,2)) + "€"
        namePriceText.setText(toShow)
        bestPoints = 0
        for promotion in promotions:
            print(promotion)
            if promotion[1] == product[0] and promotion[2] <= currentTier:
                if promotion[3] > bestPoints:
                    bestPoints = promotion[3]

        llist = gui.getComponent("list")
        llist.addItem(Item(product[1], round(
            product[2] * quantity, 2), quantity, bestPoints * quantity, barcode))

    
    namePriceText.setText(toShow)
    

class Item:
    def __init__(self, name, price, quantity, points, barcode):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.points = points
        self.barcode = barcode
    


def mainLoop(gui):
    pass

def main():
    # The checkoutCode is given in the launch arguments. If not, default to 1.
    global checkoutCode
    if len(sys.argv) > 1:
        checkoutCode = sys.argv[1]
    else:
        checkoutCode = 1
    marketCode = None
    global barcodes, products, promotions, dbResponse, db
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database = "catena"
    )
    dbResponse = db.cursor()
    dbResponse.execute("SELECT getNomePuntoVendita(" + str(checkoutCode) + ")")
    # We expect one row.
    marketName = dbResponse.fetchall()[0][0]
    # We also want the market code.
    dbResponse.execute("SELECT ID_punto FROM PuntoVendita WHERE nome = '" + marketName + "'")
    marketCode = dbResponse.fetchall()[0][0]
    # Load the product list
    products = []
    dbResponse.execute("SELECT * from Prodotto")
    for row in dbResponse:
        # The third element of the row is the price, which is a Decimal. We need to convert it to a float.
        toApp = (row[0], row[1], float(row[2]))
        products.append(toApp)
    # Load the barcode list
    dbResponse.execute( "SELECT Merce.ID_prodotto, Lotto.codice_barre FROM Merce, Lotto WHERE Merce.ID_punto = __REPLACE AND Merce.in_esposizione = 1 AND Merce.ID_lotto = Lotto.ID_lotto;".replace("__REPLACE", str(marketCode)))
    barcodes = []
    for row in dbResponse:
        barcodes.append(row)
    # Load promotions
    promotions = []
    dbResponse.execute("SELECT PromoProdotto.ID_promo, PromoProdotto.ID_prodotto, tier, punti FROM PromoProdotto, Promozione WHERE data_inizio <= CURRENT_DATE AND data_fine >= CURRENT_DATE AND PromoProdotto.ID_promo = Promozione.ID_promo;")
    for row in dbResponse:
        promotions.append(row)
    print(promotions)

    
    # Create the GUI.
    gui = GUI(fullscreen=False, background="images/background.png", icon="images/icon.png", title="Checkout")
    # Register a font.
    gui.registerFont("default", "arial", 20)
    # Create inputBox.
    codiceBarreInput = InputBox("ibox1",(20,696),(600,50),
        ((0,0,0), (180,180,180), (0,0,0),(55,55,55)),
        gui.getFont("default"),
        None,
        0,
        None,
        None,
        None,
        "Codice barre"
    )
    # register the inputBox.
    gui.addComponent(codiceBarreInput)

    # Create quantity inputBox.
    quantityInput = InputBox("ibox2",(630,696),(130,50),
    ((0,0,0), (180,180,180), (0,0,0),(55,55,55)),
        gui.getFont("default"),
        None,
        0,
        None,
        None,
        None,
        "Quantità"
    )
    # register the inputBox.
    gui.addComponent(quantityInput)

    # Create quantity inputBox.
    cardInput = InputBox("ibox3", (840, 696), (380, 50),
                             ((0, 0, 0), (180, 180, 180), (0, 0, 0), (55, 55, 55)),
                             gui.getFont("default"),
                             None,
                             0,
                             None,
                             None,
                             None,
                             "Numero Tessera"
                             )

    # register the inputBox.
    gui.addComponent(cardInput)

    # Create the scan button.
    scanButton = Button("scanButton", (770,696),(50,50),((0,0,0), (100,100,100), (180,180,180),(0,0,0)),"Scan",gui.getFont("default"),showScan,None,1,None,None)
    # Register the scan button.
    gui.addComponent(scanButton)

    # Create the scan button.
    scanButton2 = Button("scan2Button", (1240, 696), (50, 50), ((0, 0, 0), (100, 100, 100), (
        180, 180, 180), (0, 0, 0)), "Scan", gui.getFont("default"), getCard, None, 1, None, None)
    # Register the scan button.
    gui.addComponent(scanButton2)

    # Create the usePoints button.
    usePointsButton = ToggleButton("usePoints",(1240, 626), (50,50), ((0,0,0), (100,100,255), (100,100,135), (255,255,255)), "UP!", gui.getFont("default"), None, 1, None, None, None)
    # Register the usePoints button.
    gui.addComponent(usePointsButton)

    # Create the calculate button.
    calcButton = Button("calcButton", (1240, 556), (50,50), ((0,0,0), (255,255,0), (238,232,170),(0,0,0)),"Calc",gui.getFont("default"),calc,None,1,None,None)
    # Register the calculate button.
    gui.addComponent(calcButton)

    # Create the pay button.
    payButton = Button("payButton", (1310, 696), (50, 50), ((0, 0, 0), (100, 216, 100), (100,180,100),(255,255,255)),"=",gui.getFont("default"), pay, None, 1, None, None)
    # Register the pay button.
    gui.addComponent(payButton)

    # Create the undoTransaction button.
    undoTransactionButton = Button("undoTransactionButton", (1310, 626), (50, 50), ((0, 0, 0), (255, 100, 100), (180,100,100),(255,255,255)),"X",gui.getFont("default"), undoTransaction, None, 1, None, None)
    # Register the undoTransaction button.
    gui.addComponent(undoTransactionButton)

    # Create the textComponent.
    textComponent = TextComponent("namePrice", "", gui.getFont("default"), (900,100),0, color = (0,0,0), gui = None, setup = None, step = None)
    # Register the textComponent.
    gui.addComponent(textComponent)

    # Create text labels
    itemNameLabel = TextComponent("itemNameLabel", "Prodotto", gui.getFont("default"), (20, 30), 0, color = (0,0,0), gui = None, setup = None, step = None)
    gui.addComponent(itemNameLabel)
    itemQuantityLabel = TextComponent("itemQuantityLabel", "Quantità", gui.getFont("default"), (550, 30), 0, color = (0,0,0), gui = None, setup = None, step = None)
    gui.addComponent(itemQuantityLabel)
    itemPriceLabel = TextComponent("itemPriceLabel", "Prezzo", gui.getFont("default"), (655, 30), 0, color = (0,0,0), gui = None, setup = None, step = None)
    gui.addComponent(itemPriceLabel)
    itemPointsLabel = TextComponent("itemPointsLabel", "Punti", gui.getFont("default"), (750, 30), 0, color = (0,0,0), gui = None, setup = None, step = None)
    gui.addComponent(itemPointsLabel)

    # Create the list component.
    listC = listComponent("list",(20,60), (800,600), ((0,0,0), (210,210,210),(150,150,150),(0,0,0)), gui.getFont("default"),None, 0, 24, None, None, None)
    # Register the list component.
    gui.addComponent(listC)

    try:
        gui.run()
    except Exception as e:
        print(e)
    
    dbResponse.close()
    db.close()

if __name__ == "__main__":
    main()
