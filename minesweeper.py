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

    def adj(self, linha, coluna):
        adjs = []

        for dl, dc in [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]:
            nl, nc = linha+dl, coluna+dc
            if 0 <= nl < self.linhas and 0 <= nc < self.colunas:
              var = self.get_var(nl, nc)
              adjs.append(str(var))
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
        self.KB.append(conhecimento)

    def gerar_clausulas(self, array: list, r: int):
        L = combinations(array, len(array) - r + 1)
        n_array = [f"-{x}" for x in array]
        U = combinations(n_array, r + 1)
        c = list(L) + list(U)
        return c, len(c)

    def analise_local(self, adjs, valor):
        b = []
        a = []
        u = []
        for adj in adjs:
            adj = int(adj)
            posicao = self.mapa.mapa[adj]["posicao"]
            match posicao:
                case "B":
                    b.append(adj)
                case "A":
                    a.append(adj)
                case "U":
                    u.append(adj)
                case _:
                    continue
        clausulas_geradas = False
        tb = len(b)
        tu = len(u)
        for p in u:
            m = self.mapa.mapa[p]
            if tb == valor:
                m["posicao"] = "A"
                self.seguros.append([m["linha"], m["coluna"]])
                self.escrever(f"{-p} 0")
                clausulas_geradas = True
            elif tu + tb == valor:
                m["posicao"] = "B"
                self.bombas.append([m["linha"], m["coluna"]])
                self.escrever(f"{p} 0")
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

            # verificar se já está em seguros e remover caso sim
            try:
                self.seguros.remove([linha, coluna])
            except Exception as e:
                pass

            self.mapa.mapa[var].update({"valor": valor, "visitado": True, "posicao": "A"})

            self.escrever(f"{-var} 0")
            self.clausulas += 1

            if valor != 0:
                adjs = self.mapa.vizinhos[var]

                clausulas_geradas = self.analise_local(adjs, valor)

                for elem in list(self.mapa.fila):
                    if self.mapa.mapa[elem]["posicao"] != "U":
                        self.mapa.fila.remove(elem)

                if not clausulas_geradas:

                    clausulas, tam_clausulas = self.gerar_clausulas(adjs, valor)
                    self.clausulas += tam_clausulas

                    for clausula in clausulas:
                        self.KB.append(" ".join(clausula) + " 0")

    def verifica_sat(self, var: int, neg: bool = False) -> int:
        if neg:
            var *= -1

        header = f"p cnf {self.mapa.totvars} {self.clausulas + 1}\n"
        body   = "\n".join(self.KB)
        query  = f"{var} 0\n"
        cnf    = header + body + "\n" + query

        ret = subprocess.run(
            ["clasp", "-"],
            input=cnf.encode(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode

        return ret

    def pergunta(self) -> int:
        nova_fila = deque()

        var_bombas = []
        var_seguros = []

        while self.mapa.fila:

            pos_adj = self.mapa.fila.popleft()
            pos = self.mapa.get_posicao(pos_adj)

            tem_bomba = self.verifica_sat(pos_adj, neg=True)
            if tem_bomba == 20:
                var_bombas.append(pos_adj)
                self.bombas.append([pos["linha"], pos["coluna"]])
                self.qtde_bombas -= 1
                continue

            e_seguro = self.verifica_sat(pos_adj)
            if e_seguro == 20:
                var_seguros.append(pos_adj)
                self.seguros.append([pos["linha"], pos["coluna"]])
            else:
                nova_fila.append(pos_adj)

        for seguro in var_seguros:
            self.escrever(f"{-seguro} 0")
            self.mapa.mapa[seguro].update({"posicao": "A"})
            self.clausulas += 1
        for bomba in var_bombas:
            self.escrever(f"{bomba} 0")
            self.mapa.mapa[bomba].update({"posicao": "B"})
            self.clausulas += 1

        self.mapa.fila = nova_fila

    def resposta(self) -> bool:

        tot_len = len(self.bombas) + len(self.seguros)
        if self.qtde_bombas == 0:
            print(0)
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

    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, 10.0)

    tamanho = int(input())
    bombas = int(input())
    mapa = Mapa(tamanho)
    campominado = CampoMinado(mapa, bombas)

    res = True

    while len(campominado.mapa.fila) >= 0 and res:
        campominado.ler()
        campominado.pergunta()
        res = campominado.resposta()
