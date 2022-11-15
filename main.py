from api_google import BuscadorUBS
from pprint import pprint

def main():
    origem = "rua ivanise lopes lordão, 124"
    buscador = BuscadorUBS()
    buscador.load_ubs('ends_1.xlsx', 'Dados gerais')
    mais_proximo = buscador.proximo_de(origem)
    
    pprint(mais_proximo)
    
if __name__ == '__main__':
    main()

