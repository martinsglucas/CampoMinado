import subprocess
from collections import deque
import signal, sys
from itertools import combinations
from io import StringIO
from pysat.solvers import Solver

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
                self.mapa[self.totvars] = {
                    "linha": linha, 
                    "coluna": coluna, 
                    "valor": None, 
                    "visitado": False, 
                    "posicao": "U"
                    }
                self.mapa[linha, coluna] = self.totvars
        self.vizinhos = {}
        for key, val in self.mapa.items():
            if not isinstance(key, int):
                continue
            self.vizinhos[key] = self.adj(val["linha"], val["coluna"])

    def get_posicao(self, var) -> dict:
        return self.mapa[var]

    def get_var(self, linha, coluna) -> int:
        return self.mapa[linha, coluna]

    def adj(self, linha, coluna) -> list[int]:
        adjs = []

        for dl, dc in [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]:
            nl, nc = linha+dl, coluna+dc
            if 0 <= nl < self.linhas and 0 <= nc < self.colunas:
              var = self.get_var(nl, nc)
              adjs.append(var)
        return adjs

class CampoMinado:
    def __init__(self, mapa: Mapa, qtde_bombas: int):
        self.mapa = mapa
        self.qtde_bombas = qtde_bombas
        self.clausulas = 0
        self.bombas = []
        self.seguros = []
        self.KB: list[list[int]] = []
        self.solver = Solver(name="m22")
        # self.num_revelados = 0

    def escrever(self, conhecimento: list[int]):
        self.KB.append(conhecimento)
        self.solver.add_clause(conhecimento)
        self.clausulas += 1

    def gerar_clausulas(self, array: list[int], r: int):
        for comb in combinations(array, len(array) - r + 1):
            self.escrever(list(comb))
        n_array = [-x for x in array]
        for comb in combinations(n_array, r + 1):
            self.escrever(list(comb))

    def analise_local(self, adjs, valor):
        b = []
        a = []
        u = []
        for adj in adjs:
            posicao = self.mapa.mapa[adj]["posicao"]
            if posicao == "B": b.append(adj)
            elif posicao == "A": a.append(adj)
            else: u.append(adj)
        clausulas_geradas = False
        tb = len(b)
        tu = len(u)
        for p in u:
            m = self.mapa.mapa[p]
            if tb == valor:
                m.update({"posicao": "A", "visitado": True})
                self.seguros.append([m["linha"], m["coluna"]])
                self.escrever([-p])
                self.clausulas += 1
                clausulas_geradas = True
            elif tu + tb == valor:
                m.update({"posicao": "B", "visitado": True})
                self.bombas.append([m["linha"], m["coluna"]])
                self.escrever([p])
                self.clausulas += 1
                # self.num_revelados += 1
                clausulas_geradas = True
                self.qtde_bombas -= 1
            else:
                if not m["visitado"]:
                    m["visitado"] = True
                    self.mapa.fila.append(p)
        return clausulas_geradas

    def ler(self):
        num_posicoes = int(input())

        for _ in range(num_posicoes):
            linha, coluna, valor = map(int, input().split())

            var = self.mapa.get_var(linha, coluna)

            try:
                self.seguros.remove([linha, coluna])
            except ValueError:
                pass

            self.mapa.mapa[var].update({"valor": valor, "visitado": True, "posicao": "A"})
            # self.num_revelados += 1

            self.escrever([-var])

            if valor != 0:
                adjs = self.mapa.vizinhos[var]

                if not self.analise_local(adjs, valor):
                    self.gerar_clausulas(adjs, valor)

                self.mapa.fila = deque(
                    elem for elem in self.mapa.fila
                    if self.mapa.mapa[elem]["posicao"] == "U"
                )

    def pergunta(self) -> int:
        nova_fila = deque()

        var_bombas = []
        var_seguros = []

        while self.mapa.fila:

            pos_adj = self.mapa.fila.popleft()
            pos = self.mapa.get_posicao(pos_adj)

            if not self.solver.solve(assumptions=[-pos_adj]):
                var_bombas.append(pos_adj)
                self.bombas.append([pos["linha"], pos["coluna"]])
                self.qtde_bombas -= 1
                continue

            if not self.solver.solve(assumptions=[pos_adj]):
                var_seguros.append(pos_adj)
                self.seguros.append([pos["linha"], pos["coluna"]])
            else:
                nova_fila.append(pos_adj)

        for seguro in var_seguros:
            self.escrever([-seguro])
            self.mapa.mapa[seguro]["posicao"] = "A"
            self.clausulas += 1
        for bomba in var_bombas:
            self.escrever([bomba])
            self.mapa.mapa[bomba]["posicao"] ="B"
            # self.num_revelados += 1
            self.clausulas += 1

        self.mapa.fila = nova_fila

    def resposta(self):

        tot_len = len(self.bombas) + len(self.seguros)
        # descobrir = (self.mapa.linhas * self.mapa.colunas) - self.num_revelados

        # if descobrir == self.qtde_bombas:
        #     tot_len += self.qtde_bombas

        if self.qtde_bombas == 0 or tot_len == 0:
            print(0)
            sys.exit(0)
        
        print(tot_len)

        for l, c in self.seguros:
            print(f"{l} {c} A")
        for l, c in self.bombas:
            print(f"{l} {c} B")
        
        # if descobrir == self.qtde_bombas:
        #     for var in range(1,self.mapa.totvars+1):
        #         p = self.mapa.mapa[var]
        #         if p["posicao"] == "U":
        #             p["posicao"] = "B"
        #             print(f"{p["linha"]} {p["coluna"]} B")
        #             self.qtde_bombas -= 1
        #     sys.exit(0)

        self.seguros.clear()
        self.bombas.clear()

def handler(signum, frame):
    print(0)
    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, 9.9)

    tamanho = int(input())
    bombas = int(input())
    mapa = Mapa(tamanho)
    campominado = CampoMinado(mapa, bombas)

    while True:
        campominado.ler()
        campominado.pergunta()
        campominado.resposta()
