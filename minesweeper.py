from itertools import combinations
import os


class Mapa():
  def __init__(self, tamanho):
    self.linhas = tamanho
    self.colunas = tamanho
    self.totvars = 1
    self.mapa = {}
    # self.rmapa = {}
    for linha in range(self.linhas):
      for coluna in range(self.colunas):
        self.mapa[self.totvars] = [linha, coluna]
        self.mapa[linha, coluna] = self.totvars
        self.totvars += 1
  def get_posicao(self, var):
    return self.mapa[var]
  def get_var(self, linha, coluna):
    return self.mapa[linha, coluna]
  def adj(self, linha, coluna):
    direcoes = [[-1,-1], [0,-1], [1,-1], [1,0], [1,1], [0,1], [-1,1], [-1,0]]
    adjs = []
    nadjs = []
    for direcao in direcoes:
      nlinha = linha + direcao[0]
      ncoluna = coluna + direcao[1]
      if nlinha < self.linhas and nlinha >= 0 and ncoluna < self.colunas and ncoluna >=0:
        adjs.append([nlinha, ncoluna])
        nadjs.append(self.get_var(nlinha, ncoluna))
    return adjs, nadjs

class CampoMinado():
  def __init__(self, mapa: Mapa, bombas: int):
    self.mapa = mapa
    self.bombas = bombas
  def escrever(self, conhecimento: str):
    # with open("KB", '+a') as KB:
    #   KB.write(conhecimento)
    os.system(f'echo "{conhecimento}" >> KB')
  def analisar(self):
    pass
  def ler(self,):
    num_posicoes = int(input("numero de posicoes: "))

    for pos in range(num_posicoes):
      linha = int(input("linha: "))
      coluna = int(input("coluna: "))
      valor = int(input("valor: "))

      # TODO: verificar se isso está certo
      self.escrever(-self.mapa.get_var(linha,coluna))

      adjs, nadjs = mapa.adj(linha, coluna)
    
      # print("adjs: ", adjs)
      # print("nadjs: ", nadjs)
      # TODO: quando o len(nadjs)-valor+1 é igual a 1, tá criando a clausula errada
      clausulas = list(combinations(nadjs, len(nadjs)-valor+1))
      if clausulas:
        clausulas.append([-num for num in nadjs])

      fclausulas = [' '.join(str(num) for num in tupla)+ ' 0' for tupla in clausulas]

      for clausula in fclausulas:
        self.escrever(clausula)


if __name__ == '__main__':

  os.system('echo "" > KB')
  tamanho = int(input("tamanho do mapa: "))
  bombas = int(input("quantidade de bombas: "))
  mapa = Mapa(tamanho)
  # print(mapa.mapa)
  campominado = CampoMinado(mapa, bombas)
  while True:
    campominado.ler()
