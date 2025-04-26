import os
import subprocess
from collections import deque
import signal, sys
from itertools import combinations


class Mapa:
    def __init__(self, tamanho):
        self.linhas = tamanho
        self.colunas = tamanho
        self.totvars = 0
        self.mapa = {}
        self.fila = deque()
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                self.totvars += 1
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

        for direcao in direcoes:
            nlinha = linha + direcao[0]
            ncoluna = coluna + direcao[1]
            if (
                nlinha < self.linhas
                and nlinha >= 0
                and ncoluna < self.colunas
                and ncoluna >= 0
            ):
                var = self.get_var(nlinha, ncoluna)
                adjs.append(f'{var}')
                if not self.mapa[var][-1]:
                    self.mapa[var][-1] = True
                    self.fila.append(var)

        for elem in list(self.fila):
            if self.mapa[elem][2] is not None:
                self.fila.remove(elem)
        return adjs


class CampoMinado:
    def __init__(self, mapa: Mapa, qtde_bombas: int):
        self.mapa = mapa
        self.qtde_bombas = qtde_bombas
        self.clausulas = 0
        self.bombas = []
        self.seguros = []
        self.KB: list[str] = []

    def escrever(self, conhecimento: str):
        # with open("KB", "a") as kb:
            # kb.write(conhecimento + "\n")
        self.KB.append(conhecimento)

    def gerar_clausulas(self, array: list, r: int):
        L = combinations(array, len(array) - r + 1)
        n_array = [f"-{x}" for x in array]
        U = combinations(n_array, r + 1)
        c = list(L) + list(U)
        # clausulas = [" ".join(str(num) for num in tupla) + " 0" for tupla in c]
        return c, len(c)

    # def escrever_clausulas(self, array):
    #     with open("KB", "a") as f:
    #         lines = (" ".join(map(str, row)) + " 0\n" for row in array)
    #         f.writelines(lines)

    def ler(self):
        num_posicoes = int(input())

        for _ in range(num_posicoes):
            linha, coluna, valor = map(int, input().split())

            var = self.mapa.get_var(linha, coluna)

            self.mapa.mapa[var] = [linha, coluna, valor, True]

            self.escrever(f"{-var} 0")
            self.clausulas += 1

            if valor != 0:
                adjs = mapa.adj(linha, coluna)
                clausulas, tam_clausulas = self.gerar_clausulas(adjs, valor)
                self.clausulas += tam_clausulas
                # self.escrever_clausulas(clausulas)
                # with open("KB", "a") as kb:
                #     for clausula in clausulas:
                #         kb.write(" ".join(clausula) + " 0 \n")
                
                # self.KB.extend(clausulas)
                for clausula in clausulas:
                    self.KB.append(" ".join(clausula) + " 0")
                    # self.KB.append(clausula)
                # print(self.KB)

    def verifica_sat(self, var: int, neg: bool = False) -> int:
        if neg:
            var *= -1

        # 1) monte o header
        header = f"p cnf {self.mapa.totvars} {self.clausulas + 1}\n"
        # 2) junte KB + consulta
        body   = "\n".join(self.KB)
        query  = f"{var} 0\n"
        cnf    = header + body + "\n" + query

        # with open("pergunta.cnf", "w") as p:
        #     with open("KB", "r") as kb:
        #         p.write(f"p cnf {self.mapa.totvars} {self.clausulas+1}\n")
        #         p.write(kb.read())
        #         p.write(f"{var} 0\n")

        ret = subprocess.run(
            ["clasp", "-"],
            input=cnf.encode(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            #timeout=remaining,
        ).returncode

        return ret

    def pergunta(self) -> int:
        nova_fila = deque()

        var_bombas = []
        var_seguros = []

        while self.mapa.fila:

            pos_adj = self.mapa.fila.popleft()

            # nao_abertos = []

            # if self.qtde_bombas <= 3:
            #     for linha in range(self.mapa.linhas):
            #         for coluna in range(self.mapa.colunas):
            #             var = self.mapa.get_var(linha, coluna)
            #             if self.mapa.mapa[var][2] is None:
            #                 nao_abertos.append(var)
            #     if len(nao_abertos) <= 10:
            #         clausulas, tam = self.gerar_clausulas(nao_abertos, self.qtde_bombas)
            #         self.clausulas += tam
            #         self.escrever_clausulas(clausulas)

            tem_bomba = self.verifica_sat(pos_adj, neg=True)
            if tem_bomba == 20:
                var_bombas.append(pos_adj)
                self.bombas.append(self.mapa.get_posicao(pos_adj)[:2])
                self.qtde_bombas -= 1
                continue

            e_seguro = self.verifica_sat(pos_adj)
            if e_seguro == 20:
                var_seguros.append(pos_adj)
                self.seguros.append(self.mapa.get_posicao(pos_adj)[:2])
            else:
                nova_fila.append(pos_adj)

        # with open("KB", "a") as kb:
        for seguro in var_seguros:
            # kb.write(f"{-seguro} 0\n")
            self.escrever(f"{-seguro} 0")
            self.clausulas += 1
        for bomba in var_bombas:
            self.escrever(f"{bomba} 0")
            # kb.write(f"{bomba} 0\n")
            self.clausulas += 1

        self.mapa.fila = nova_fila

    def resposta(self) -> bool:
        """ if tempo_esgotado:
            print(0)
            sys.exit(0) """

        tot_len = len(self.bombas) + len(self.seguros)
        print(tot_len)

        for s in self.seguros:
            l, c = s
            print(f"{l} {c} A")
        for b in self.bombas:
            l, c = b
            print(f"{l} {c} B")

        self.seguros = []
        self.bombas = []

        return tot_len > 0


def handler(signum, frame):
    print(0)
    sys.exit(0)

if __name__ == "__main__":

    #tempo_esgotado = False
    #start_time = time.time()

    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, 9.5)

    with open("KB", "w") as kb:
        pass

    tamanho = int(input())
    bombas = int(input())
    mapa = Mapa(tamanho)
    campominado = CampoMinado(mapa, bombas)

    res = True

    while len(campominado.mapa.fila) >= 0 and res:
        campominado.ler()
        campominado.pergunta()
        res = campominado.resposta()
