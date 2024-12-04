import random

#Functions
def main():
    n_buy = 0
    n_sell = 0
    for i in range(1, 101):
        state = random.randint(0, 1)
        if state == 0:
            n_stock = random.randint(1, 5)
            n_buy += n_stock
        else:
            n_stock = random.randint(1, 5)
            n_sell += n_stock

    return n_buy, n_sell

if __name__ == "__main__":
    buy, sell = main()
    print(buy, sell, buy - sell, buy + sell) 