import sys
from codicefiscale import codicefiscale
from faker import Faker

fake = Faker("it_IT")

def generateNames(n=100):
    string = ""
    for _ in range(n):
        name = fake.first_name()
        surname = fake.last_name()
        name = name + " " + surname
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=100)
        cf = codicefiscale.encode(
            name = name.split()[0],
            surname = name.split()[1],
            birthdate = fake.date_of_birth().strftime("%d/%m/%Y"),
            sex = fake.random_element(elements=('M', 'F')),
            birthplace = "Catania"
        )
        # create query string
        query = 'Select aggiungiCliente(\"%s\", \"%s\", \"%s\", true, %s);\n'
        # execute query (name, surname, birthdate, cf)
        string += query % (name, birth_date, cf, fake.random_int(min=1, max=100))
    return string
        
def generateProductNames(n=100):
    string = ""
    for _ in range(n):
        name = fake.word()
        # random price between 0.01 and 100 (2 decimal places)
        price = round(fake.random_int(min=1, max=10000) / 100, 2)
        # create query string
        query = 'Select aggiungiProdotto(\"%s\", %s);\n'
        # execute query (name, price)
        string += query % (name, price)
    return string

def generateStorage(n=1000):
    # Create Lots
    string = "Select aggiungiConsegna(1,CURRENT_DATE);\n"
    for _ in range(n):
        deliveryId = 1
        productId = fake.random_int(min=1, max=100)
        # The barcode is a random 13 digit string
        barcode = fake.random_int(min=1000000000000, max=9999999999999)
        # random quantity between 1 and 1000
        quantity = fake.random_int(min=1, max=1000)
        # The expiration date is a random date between today and 20 year from now
        expirationDate = fake.date_between(start_date="today", end_date="+20y")
        # create query string (product id, quantity, barcode, delivery, expiration date)
        query = 'Select aggiungiLotto(%s, %s, \"%s\", %s, \"%s\");\n'
        # execute query
        string += query % (productId, quantity, barcode, deliveryId, expirationDate)
        # also generate the spostaMerce query
        # random quantity between 1 and quantity
        quantity = fake.random_int(min=1, max=quantity)
        # barcode is the same as the one generated for the lot
        # supermarketid is 1
        # create query string (supermarketid, barcode, quantity)
        query = 'Select spostaMerce(1, \"%s\", %s);\n'
        # execute query
        string += query % (barcode, quantity)
    return string


def generateBaseData():
    str = ""
    str += "SELECT aggiungiPuntoVendita(\"Test\",\"Via test 123\",1);\n"
    return str

def generatePromos(n=100):
    string = ""
    for _ in range(25):
        query = 'INSERT INTO promozione (tier, punti, DATA_INIZIO, DATA_FINE) VALUES (%s,%s,\"%s\",\"%s\");\n'
        # execute query
        string += query % (fake.random_int(min=0, max=2), fake.random_int(min=1, max=100), fake.date_between(start_date="today", end_date="+1y"), fake.date_between(start_date="+1y", end_date="+2y"))
    return string

def generatePromotions(n=100):
    string = generatePromos(n//4)
    # Associate promotions to random products
    for _ in range(1,100):
        # 70% chance of having a promotion
        if fake.boolean(chance_of_getting_true=70):
            productId = _
            # insert a random promotion
            query = 'INSERT INTO PROMOPRODOTTO (ID_PROMO, ID_PRODOTTO) VALUES (%s, %s);\n'
            string += query % (fake.random_int(min=1, max=25), productId)
    return string




if __name__ == "__main__":
    argv = sys.argv
    numberOfNames = argv[1] if len(argv) > 1 else 100
    numberOfProducts = argv[2] if len(argv) > 2 else 100
    numberOfLots = argv[3] if len(argv) > 3 else 1000

    # Write the base data to a file
    with open("1.sql", "w") as f:
        f.write(generateBaseData())

    # Write the output to a file
    with open("2.sql", "w") as f:
        f.write(generateNames(int(numberOfNames)))

    with open("3.sql", "w") as f:
        f.write(generateProductNames(int(numberOfProducts)))

    with open("4.sql", "w") as f:
        f.write(generateStorage(int(numberOfLots)))

    with open("5.sql", "w") as f:
        f.write(generatePromotions(int(numberOfProducts)))



