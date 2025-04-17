from itertools import combinations
import os
import subprocess


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
                # PENSANDO: 
                # self.mapa[self.totvars] = 
                # {
                #   "linha": linha, 
                #   "coluna": coluna, 
                #   "valor": None, 
                #   "visited": False
                # }
                self.mapa[self.totvars] = [linha, coluna, None, False]
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
                if self.mapa[self.get_var(nlinha, ncoluna)][-1] != True and self.get_var(nlinha, ncoluna) not in self.fila:
                    # print(self.mapa[self.get_var(nlinha, ncoluna)][-1])
                    self.mapa[self.get_var(nlinha, ncoluna)][-1] = True
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
        self.bombas = []
        self.seguros = []

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
        num_posicoes = int(input())

        for _ in range(num_posicoes):
            linha, coluna, valor = map(int, input().split())

            self.mapa.mapa[self.mapa.get_var(linha, coluna)] = [linha, coluna, valor]

            self.escrever(f"{-self.mapa.get_var(linha, coluna)} 0")

            if valor != 0:
                adjs, nadjs = mapa.adj(linha, coluna)
                clausulas, tam_clausulas = self.gerar_clausulas(nadjs, valor)
                self.clausulas += tam_clausulas + 1

                for clausula in clausulas:
                    self.escrever(clausula)

    def verifica_sat(self, var:int, neg: bool = False) -> int:
        if neg:
            var *= -1
        os.system('cat KB > pergunta')
        os.system(f'echo "{var} 0" >> pergunta')
        # os.system("rm -f pergunta.cnf")  # Remove se já existir
        os.system(f'echo "p cnf {self.mapa.totvars} {self.clausulas+1}" > pergunta.cnf')
        os.system("cat pergunta >> pergunta.cnf")

        ret = os.system("clasp pergunta.cnf > /dev/null 2>&1")
        exit_code = ret >> 8
        return exit_code

    def pergunta(self) -> int:
        nova_fila = []
        while self.mapa.fila:

            pos_adj = self.mapa.fila.pop(0)
            # os.system("cat KB > pergunta")
            os.system('rm -f pergunta.cnf')

            # print(f"\nDecidindo {self.mapa.get_posicao(pos_adj)[:2]}...\n")
            tem_bomba = self.verifica_sat(pos_adj, neg=True)
            if tem_bomba == 20:
                # print(f'{self.mapa.get_posicao(pos_adj)[:2]} é BOMBA')
                self.bombas.append(self.mapa.get_posicao(pos_adj)[:2])
                # escrever na base de conhecimento e incrementar self.clausulas
                os.system(f'echo "{pos_adj} 0" >> KB')
                self.clausulas += 1
                continue

            # Remove a última linha de pergunta
            os.system("sed -i '$d' pergunta")

            e_seguro = self.verifica_sat(pos_adj)
            if e_seguro == 20:
                # print(f'{self.mapa.get_posicao(pos_adj)[:2]} é SEGURO')
                self.seguros.append(self.mapa.get_posicao(pos_adj)[:2])
                # escrever na base de conhecimento e incrementar self.clausulas
                os.system(f'echo "{-pos_adj} 0" >> KB')
                self.clausulas += 1
            else:
                # print(f"{self.mapa.get_posicao(pos_adj)[:2]} ainda NÂO SEI")
                nova_fila.append(pos_adj)

        self.mapa.fila = nova_fila

    def resposta(self) -> int:
        tot_len = len(self.bombas) + len(self.seguros)
        print(tot_len)
        for s in self.seguros:
            l, c = s
            print(f'{l} {c} A')
        for b in self.bombas:
            l, c = b
            print(f'{l} {c} B')

        self.seguros = []
        self.bombas = []

        return tot_len > 0


if __name__ == "__main__":

    os.system("cd /tmp/")
    os.system("rm -f KB")
    tamanho = int(input())
    bombas = int(input())
    mapa = Mapa(tamanho)
    # print(mapa.mapa)
    campominado = CampoMinado(mapa, bombas)

    campominado.ler()
    campominado.pergunta()
    res = campominado.resposta()


    while len(campominado.mapa.fila) >= 0 or res:
        campominado.ler()
        campominado.pergunta()
        res = campominado.resposta()
