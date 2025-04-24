import os
import subprocess
from collections import deque
import signal, sys, time


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
                adjs.append(var)
                if (not self.mapa[var][-1]):
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

    def escrever(self, conhecimento: str):
        with open("KB", "a") as kb:
            kb.write(conhecimento + "\n")

    def _combinacoes_str(self, array: list[int], r: int) -> list[str]:
        
        resultados: list[str] = []

        def helper(prefix: list[str], restos: list[int], k: int):
            if k == 0:
                resultados.append(" ".join(prefix) + " 0")
                return
            if len(restos) < k:
                return
            helper(prefix + [str(restos[0])], restos[1:], k - 1)
            helper(prefix, restos[1:], k)

        helper([], array, r)
        return resultados

    def gerar_clausulas(self, array: list[int], r: int):
        n = len(array)
        L = self._combinacoes_str(array, n - r + 1)
        negados = [-x for x in array]
        U = self._combinacoes_str(negados, r + 1)

        clausulas = L + U
        return clausulas, len(clausulas)


    # def _combinacoes(self, array: list, r: int) -> list:
    #     if r == 0:
    #         return [[]]
    #     if len(array) < r:
    #         return []
        
    #     com_primeiro = self._combinacoes(array[1:], r-1)
    #     com_primeiro = [[array[0]] + comb for comb in com_primeiro]

    #     sem_primeiro = self._combinacoes(array[1:], r)

    #     return com_primeiro + sem_primeiro


    # def gerar_clausulas(self, array: list, r: int):
    #     L = self._combinacoes(array, len(array) - r + 1)
    #     n_array = list(map(lambda x: -x, array))
    #     U = self._combinacoes(n_array, r + 1)
    #     c = L + U
    #     clausulas = [" ".join(str(num) for num in tupla) + " 0" for tupla in c]
    #     return clausulas, len(clausulas)

    def ler(self):
        num_posicoes = int(input())

        for _ in range(num_posicoes):
            linha, coluna, valor = map(int, input().split())

            var = self.mapa.get_var(linha, coluna)

            self.mapa.mapa[var] = [linha, coluna, valor, True]

            self.escrever(f"{-var} 0")

            if valor != 0:
                adjs = mapa.adj(linha, coluna)
                clausulas, tam_clausulas = self.gerar_clausulas(adjs, valor)
                self.clausulas += tam_clausulas + 1
                with open("KB", "a") as kb:
                    for clausula in clausulas:
                        # self.escrever(clausula)
                        kb.write(clausula + "\n")


    def verifica_sat(self, var: int, neg: bool = False) -> int:
        if neg:
            var *= -1

        """ tempo = time.time() - start_time
        restante = 9.5 - tempo

        if restante <= 0:
            print(0) """

        with open("pergunta.cnf", "w") as p:
            with open("KB", "r") as kb:
                p.write(f"p cnf {self.mapa.totvars} {self.clausulas+1}\n")
                p.write(kb.read())
                p.write(f"{var} 0\n")

        ret = subprocess.run(
            ["clasp", "pergunta.cnf"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            #timeout=restante
        ).returncode

       
        
        return ret

    def pergunta(self) -> int:
        nova_fila = deque()
        while self.mapa.fila:

            pos_adj = self.mapa.fila.popleft()

            tem_bomba = self.verifica_sat(pos_adj, neg=True)
            if tem_bomba == 20:
                self.bombas.append(self.mapa.get_posicao(pos_adj)[:2])
                # self.escrever(f"{pos_adj} 0")
                self.clausulas += 1
                continue

            e_seguro = self.verifica_sat(pos_adj)
            if e_seguro == 20:
                self.seguros.append(self.mapa.get_posicao(pos_adj)[:2])
                # self.escrever(f"{-pos_adj} 0")
                self.clausulas += 1
            else:
                nova_fila.append(pos_adj)

        with open("KB", "a") as kb:
            for seguro in self.seguros:
                l, c = seguro
                kb.write(f"{-self.mapa.get_var(l,c)} 0\n")
            for bomba in self.bombas:
                l, c = bomba
                kb.write(f"{self.mapa.get_var(l,c)} 0\n")


        self.mapa.fila = nova_fila

    def resposta(self) -> int:
        if tempo_esgotado:
            print(0)
            sys.exit(0)
            return False

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
    global tempo_esgotado
    tempo_esgotado = True

if __name__ == "__main__":
    
    tempo_esgotado = False

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
    
    