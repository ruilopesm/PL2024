from typing import Final, List, Optional
import ply.lex as lex
import json

from dataclasses import dataclass

@dataclass
class Produto:
    codigo: str
    nome: str
    quantidade: int
    preco: float

coins: Final[List[float]] = [
    2.00,
    1.00,
    0.50,
    0.20,
    0.10,
    0.05,
    0.02,
    0.01
]

def calculate_change(change: float) -> List[int]:
    result = []
    for coin in coins:
        result.append(int(change // coin))
        change %= coin
    
    return result

def pretty_print_change(change: List[int]) -> None:
    for i, coin in enumerate(coins):
        if change[i] > 0:
            print(f"{change[i]} coins of {coin:.2f}€")

class VendingMachine:
    tokens = (
        "LIST",
        "EXIT",
        "COIN",
        "PRODUCT"
    )

    states = (
        ("INSERTCOINS", "exclusive"),
        ("PRODUCTSELECTION", "exclusive")
    )

    t_ANY_ignore = " \t\n"
    t_INSERTCOINS_ignore = ", \t\n"

    def __init__(self):
        self.lexer: Optional[lex.Lexer] = None
        self.exit: bool = False
        
        self.amount: float = 0.0
        self.products: List[Produto] = []

    def setup(self, **kwargs) -> None:
        self.lexer = lex.lex(module=self, **kwargs)
        self.load_products()

    def load_products(self) -> None:
        with open("produtos.json", encoding="utf-8") as file:
            self.products = [Produto(**item) for item in json.load(file)]

    def t_begin_INSERTCOINS(self, t):
        r"COIN"
        t.lexer.begin("INSERTCOINS")

    def t_INSERTCOINS_COIN(self, t):
        r"2e|1e|50c|20c|10c|5c|2c|1c"
        if t.value[-1] == "c":
            t.value = int(t.value[:-1]) / 100
        elif t.value[-1] == "e":
            t.value = int(t.value[:-1])

        self.amount += t.value
        return t
    
    def t_INSERTCOINS_EXIT(self, t):
        r"EXIT"
        print("Current amount: {:.2f}".format(self.amount))
        t.lexer.begin("INITIAL")

    def t_begin_PRODUCTSELECTION(self, t):
        r"PRODUCT"
        t.lexer.begin("PRODUCTSELECTION")

    def t_PRODUCTSELECTION_PRODUCT(self, t):
        r"[0-9]{2}"
        t.lexer.begin("INITIAL")

        for product in self.products:
            if product.codigo == t.value:
                if product.quantidade <= 0:
                    print("Product out of stock")
                    return t
                
                if self.amount < product.preco:
                    print("Insufficient funds")
                    return t
                
                self.amount -= product.preco
                product.quantidade -= 1
                print("Product acquired: {}".format(product.nome))
                print("Current amount: {:.2f}€".format(self.amount))
                return t
            
        print("Product not found")
        return t
    
    def t_ANY_error(self, t):
        print("Illegal character '{}'".format(t.value[0]))
        t.lexer.skip(1)

    def t_LIST(self, t):
        r"LIST"
        for product in self.products:
            print(f"{product.codigo} - {product.nome} - {product.preco}€")
        
        return t
    
    def t_EXIT(self, t):
        r"EXIT"
        self.exit = True

        change = calculate_change(self.amount)
        pretty_print_change(change)

        print("Thank you for using our vending machine!")

def main() -> None:
    machine = VendingMachine()
    machine.setup()

    while not machine.exit:
        line = input(">>> ")
        machine.lexer.input(line)

        while True:
            token = machine.lexer.token()
            if not token:
                break


if __name__ == "__main__":
    main()
