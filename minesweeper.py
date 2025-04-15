from itertools import combinations
import os


class Mapa:
    def __init__(self, tamanho):
        self.linhas = tamanho
        self.colunas = tamanho
        self.totvars = 0
        self.mapa = {}
        self.fila = []
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                self.totvars += 1
                self.mapa[self.totvars] = [linha, coluna, None]
                self.mapa[linha, coluna] = self.totvars

    def get_posicao(self, var):
        return self.mapa[var]

    def get_var(self, linha, coluna):
        return self.mapa[linha, coluna]

    def adj(self, linha, coluna):
        direcoes = [
            [-1, -1],
            [0, -1],
            [1, -1],
            [1, 0],
            [1, 1],
            [0, 1],
            [-1, 1],
            [-1, 0],
        ]
        adjs = []
        nadjs = []

        for direcao in direcoes:
            nlinha = linha + direcao[0]
            ncoluna = coluna + direcao[1]
            if (
                nlinha < self.linhas
                and nlinha >= 0
                and ncoluna < self.colunas
                and ncoluna >= 0
            ):
                adjs.append([nlinha, ncoluna])
                nadjs.append(self.get_var(nlinha, ncoluna))
                if self.mapa[self.get_var(nlinha, ncoluna)][2] != 0 and self.get_var(nlinha, ncoluna) not in self.fila:
                    self.fila.append(self.get_var(nlinha, ncoluna))

        for elem in self.fila:
            if self.mapa[elem][2] != None:
                self.fila.remove(elem)

        return adjs, nadjs


class CampoMinado:
    def __init__(self, mapa: Mapa, bombas: int):
        self.mapa = mapa
        self.bombas = bombas
        self.clausulas = 0

    def escrever(self, conhecimento: str):
        os.system(f'echo "{conhecimento}" >> KB')

    def analisar(self):
        pass

    def gerar_clausulas(self, array: list, r: int):
        c1 = list(combinations(array, len(array) - r + 1))
        n_array = list(map(lambda x: -x, array))
        c2 = list(combinations(n_array, r+1))
        c = c1 + c2
        clausulas = [" ".join(str(num) for num in tupla) + " 0" for tupla in c]
        return clausulas, len(clausulas)

    def ler(self):
        num_posicoes = int(input("numero de posicoes: "))

        for _ in range(num_posicoes):
            linha, coluna, valor = map(int, input().split())

            self.mapa.mapa[self.mapa.get_var(linha, coluna)] = [linha, coluna, valor]

            # TODO: enfileirar/ empilhar essas posicoes para, depois, fazer perguntas sobre elas
            self.escrever(f"{-self.mapa.get_var(linha, coluna)} 0")

            if valor != 0:
                adjs, nadjs = mapa.adj(linha, coluna)
                clausulas, tam_clausulas = self.gerar_clausulas(nadjs, valor)
                self.clausulas += tam_clausulas + 1

                for clausula in clausulas:
                    self.escrever(clausula)

    def pergunta(self) -> int:
        while self.mapa.fila:
            pos_adj = self.mapa.fila.pop(0)
            os.system("cat KB > pergunta")
            # os.system(f'echo "-{pos_adj} 0" >> pergunta') # pergunta se é bomba0
            os.system(f'echo "{pos_adj} 0" >> pergunta') # pergunta se é seguro
            os.system("rm -f pergunta.cnf")  # Remove se já existir
            os.system(f'echo "p cnf {self.mapa.totvars} {self.clausulas+1}" > pergunta.cnf')
            os.system("cat pergunta >> pergunta.cnf")
            print(f"Decidindo {self.mapa.get_posicao(pos_adj)[:2]}...")
            ret = os.system("clasp pergunta.cnf > /dev/null 2>&1")
            # ret = os.system("clasp pergunta.cnf")
            exit_code = ret >> 8

            if exit_code == 10:
                print("SAT")
            elif exit_code == 20:
                # print(f"UNSAT: bomba {self.mapa.get_posicao(pos_adj)[:2]}")
                print(f"UNSAT: abre {self.mapa.get_posicao(pos_adj)[:2]}")


if __name__ == "__main__":

    os.system("rm -f KB")
    tamanho = int(input("tamanho do mapa: "))
    bombas = int(input("quantidade de bombas: "))
    mapa = Mapa(tamanho)
    # print(mapa.mapa)
    campominado = CampoMinado(mapa, bombas)

    campominado.ler()
    campominado.pergunta()

    while len(campominado.mapa.fila) != 0:
        campominado.ler()
        campominado.pergunta()
