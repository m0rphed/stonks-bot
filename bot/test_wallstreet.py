from time import sleep
from wallstreet import Stock, Call, Put
s = Stock('ROSN')

while True:
    print("PRICE: ", s.price)
    print("Change: ", s.change)
    print("Last: ", s.last_trade, "\n")
    sleep(10)