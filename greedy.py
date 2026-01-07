# GREEDY
# Pau Soler & Rebeca Torrecilla

from yogi import read
import time
import sys

class Dades:
    """
    Estructura de dades per l'input.
    
    VARIABLES:
    · C: nombre natural (>0) que representa el nombre de cotxes
    · M: nombre natural (>0) que representa les millores
    · K: nombre natural (>0) que representa les classes
    · ce: vector d'enters que representa el nombre de cotxes d'una finestra que es poden millorar en l'estació 'e' sense patir penalització
    · ne: vector d'enters que representa les mides de les finestres de cada millora
    · cls: enter amb el nombre de cotxes de cada classe K_i
    · mill: matriu de booleans que indica les millores que necessita cada classe (representada en files). Posem 1 si la millora de la estació i (columna i) és necessària, 0 altrament. 
    """

    C: int
    M: int
    K: int
    Ce: list[int]
    Ne: list[int]
    num_cotxes: list[int]
    Matriu_millores: list[list[int]]

    def __init__(self, C: int, M: int, K: int, Ce: list[int], Ne: list[int], num_cotxes: list[int], Matriu_millores: list[list[int]]):
        self.C = C
        self.M = M
        self.K = K
        self.Ce = Ce
        self.Ne = Ne
        self.num_cotxes = num_cotxes
        self.Matriu_millores = Matriu_millores


def llegeix_entrada() -> Dades:
    """ 
    Llegim les dades d'entrada i ho posem a una estructura de Dades 
    """

    C, M, K = read(int), read(int), read(int) #Cotxes, Millores, Classes
    Ce: list[int] = [read(int) for _ in range(M)] #Nombre de cotxes que podem millorar en cada estació sense penalització
    Ne: list[int] = [read(int) for _ in range(M)] #Mida de la finestra de cada millora
    num_cotxes: list[int] = [] #Llista de quantitat de cotxes que s'han de fer de cada classe.
    Matriu_millores: list[list[int]] = [] #Col: classes, Files: si el cotxe té la millora o no.
    for _ in range(K):
        classe = read(int) #No l'utilitzarem
        num_c = read(int) #numero de cotxes que hem de fer de la classe
        millores: list[int] = [read(int) for _ in range(M)] #llista de quines millores té el cotxe d'aquesta classe
        Matriu_millores.append(millores)
        num_cotxes.append(num_c)

    entrada: Dades = Dades(C, M, K, Ce, Ne, num_cotxes, Matriu_millores)
    return entrada


def write_output(sol: list[int], pen: int, temps_exec: float):
    """
    Donada una solució, un nombre de penalitzacions i un temps d'execució, 
    ho escriu en el fitxer de sortida indicat.
    """
    if len(sys.argv) >= 2:
        output_filename = sys.argv[1]
        with open(output_filename, 'w') as f:
            f.write(f"{pen} {temps_exec:.1f}\n")
            f.write(" ".join([str(elem) for elem in sol]) + "\n")
    else:
        print(pen, temps_exec)
        print(" ".join([str(elem) for elem in sol]))


def sorter_opt(M: list[list[int]]) -> list[int]:
    """
    Donada una matriu, ordena les files de gran a petita segons la suma dels valors de la fila.
    Retorna una llista indicant a quin índex s'ha mogut l'índex original
    (n_idx[idx] = "index on es troba ara la fila que abans estava a l'índex idx")
    """
    return [i for i, _ in sorted(enumerate(M), key=lambda x: sum(x[1]), reverse = True)]


def penalitzacio_potencial(sol: list[int], k: int, entrada: Dades) -> int:
    """
    Calcula la penalizació afegida que ha suposat afegir un cotxe a la posició k
    
    · penalització: variable a retornar, conté la penalització acumulada d'una finestra
    · inici_fi: estableix el rang de la finestra a comprovar per cada millora
    · comptador: codifica el nombre de millores de la finestra actual
    """

    penalitzacio = 0
    
    for m in range(entrada.M): #iterem pel nombre de millores
        if entrada.Matriu_millores[sol[k]][m] == 1: #si el cotxe té la millora que estem mirant
            inici_fin = max(0, k - (entrada.Ne[m] - 1))
            comptador = 0
            for i in range(inici_fin, k + 1): #iterem dins la finestra de cotxes
                if entrada.Matriu_millores[sol[i]][m] == 1: 
                    comptador += 1
            if comptador > entrada.Ce[m]:
                penalitzacio += (comptador - entrada.Ce[m])
                
    return penalitzacio


def greedy(entrada: Dades) -> list[int]:
    """
    Funció que implementa un algorisme greedy. Comencem ordenant les classes de més a menys millores.
    Seguidament, escollim el cotxe amb més millores a fer que NO ens saturi cap de les finestres. 
    Si cap compleix això, escollim el que menys penalització generi.

    · ordenacio: llista que emmagatzema la solució a retornar
    · n_idx: llista que conté de manera ordenada (de millor a pitjor) les classes de cotxes a posar abans en la solució 
    · c_act: variable que codifica la millor classe de cotxe a posar a continuació
    """

    ordenacio: list[int] = [-1]*entrada.C #solució
    n_idx = sorter_opt(entrada.Matriu_millores)

    for i in range(entrada.C): #iterem pel nombre de cotxes que volem fer
        millor_c = -1
        min_pen = float("inf")
        for j in range(entrada.K): #iterem per les diferents classes
            c_act = n_idx[j]
            if entrada.num_cotxes[c_act] > 0: #si ens queden cotxes d'aquesta classe per fer
                ordenacio[i] = c_act #posem el candidat
                pen = penalitzacio_potencial(ordenacio, i, entrada) #calculem quant penalitza posar aquest cotxe
                if pen == 0: #si trobem un cotxe que no penalitza, el posem
                    millor_c = c_act
                    min_pen = 0
                    break
                if pen < min_pen: #si hem trobat un cotxe que penalitza menys que el millor trobat, el guardem
                    millor_c = c_act
                    min_pen = pen
        
        ordenacio[i] = millor_c
        entrada.num_cotxes[millor_c] -= 1
    
    return ordenacio


def calcula_penalitzacions_total(sol: list[int], entrada: Dades) -> int:
    """
    Donada una solució, calcula el nombre de penalitzacions que fa aquesta solució en total.

    · n_pen: variable a retornar, codifica la penalització total de la solució.
    · sol_ext: extensió de la solució amb cotxes sense millores (índex -1) per tal de poder mirar les finestres finals
    · comptador: enter que diu quants cotxes de la finestra actual necessiten millora
    """
    
    n_pen = 0
    M = len(entrada.Ce)
    sol_ext = sol + [-1]*(max(entrada.Ne)-1) #extenem la solució amb cotxes sense millores (índex -1) per tal de poder mirar les finestres finals.

    for i in range(len(sol_ext)): #iterem pels cotxes de la finestra
        for m in range(M): #iterem pel nombre de millores
            inici_fin = max(0, i - (entrada.Ne[m] - 1))
            finestra: list[int] = sol_ext[inici_fin:i+1] #finestra que hem de comprovar
            comptador = sum(entrada.Matriu_millores[idx][m] for idx in finestra if (idx != -1 and entrada.Matriu_millores[idx][m] == 1)) #comptem quants cotxes de la finestra necessiten millora
            if comptador > entrada.Ce[m]: n_pen += (comptador - entrada.Ce[m]) #afegim en quina quantitat ens hem passat

    return n_pen


def main():
    entrada = llegeix_entrada()
    t1 = time.time()
    sol: list[int] = greedy(entrada)
    pen = calcula_penalitzacions_total(sol, entrada)
    t2 = time.time()
    temps_exec = round(t2 - t1, 1)
    write_output(sol, pen, temps_exec)

    return


if __name__ == "__main__":

    main()
