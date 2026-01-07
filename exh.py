# EXHAUSTIU
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


def write_output(sol: list[int], pen: int, temps_ini: float):
    """
    Donada una solució, un nombre de penalitzacions i un temps inicial, 
    calcula el temps total d'execució i ho escriu en el fitxer de sortida indicat.
    """

    temps_exec = round(time.time() - temps_ini, 1)
    if len(sys.argv) >= 2:
        output_filename = sys.argv[1]
        with open(output_filename, 'w') as f:
            f.write(f"{pen} {temps_exec:.1f}\n")
            f.write(" ".join([str(elem) for elem in sol]) + "\n")
    else:
        print(pen, temps_exec)
        print(" ".join([str(elem) for elem in sol]))


def cls_max(entrada: Dades) -> int:
    """ 
    Retornem la classe amb més cotxes (doncs començarem iterant 
    amb aquesta en la cerca exhaustiva)
    """

    maxim = 0
    for n in range(len(entrada.num_cotxes)):
        if entrada.num_cotxes[maxim] < entrada.num_cotxes[n]:
            maxim = n
    
    return maxim


def penalitzacio(sol: list[int], k: int, entrada: Dades) -> int:
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


def prediccio(entrada: Dades, k: int) -> int:
    """
    Calcula i retorna una fita inferior del cost d'acabar una solució parcial donada.
    Calcula en funció dels espais que queden per omplir (està ple fins al índex k)
    """
    
    penalitzacio: int = 0
    for j in range(entrada.M): #iterem pel nombre de millores
        mill_cotxes: int = 0
        for i in range(entrada.K): #iterem pel nombre de classes
            # Nombre de cotxes que necessiten millora
            mill_cotxes += entrada.Matriu_millores[i][j] * entrada.num_cotxes[i]

        # Nombre de finestres que no se solapen
        finestres_no_solap = ((entrada.C - k) // entrada.Ne[j]) if ((entrada.C - k) % entrada.Ne[j]) == 0 else ((entrada.C - k) // entrada.Ne[j] + 1)

        # Nombre màxim de cotxes que es poden afegir sense penalització
        max_cotxes = finestres_no_solap * entrada.Ce[j]

        if mill_cotxes > max_cotxes:
            # Si tenim més cotxes per millorar dels que estan permesos en l'estació
            # hem d'afegir una penalització
            penalitzacio += mill_cotxes - max_cotxes

    return penalitzacio


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


def cerca_exhaustiva_rec(k: int, sol: list[int], entrada: Dades, pen: int, 
                     pen_min: list[float], classe:int, temps_ini: float):
    """ 
    Funció principal de la cerca exahustiva. Donada una solució parcial, explora les solucions que segueixen d'aquesta,
    podant pel camí les branques que portaran a solucions pitjors que la millor trobada fins al moment (pen_min)

    · k: índex actual. La solució està completa fins a k-1.
    · sol: solució parcial actual.
    · pen: penalització acumulada de la solució parcial fins a la posició k-1.
    · pen_min: millor penalització trobada fins ara
    """
    
    # Poda
    if pen > pen_min[0]: return #si ja hem penalitzat més que la mínima penalització trobada
    if pen + prediccio(entrada, k) > pen_min[0]: return #si aquesta solució acabarà penalitzant més per força

    # Final 
    if k == entrada.C: 
        cost_real = calcula_penalitzacions_total(sol, entrada) #cost real; el que fem servir per la poda no conté les finestres finals
        if cost_real < pen_min[0]: 
            write_output(sol, cost_real, temps_ini)
            pen_min[0] = cost_real
        return

    # Cerca
    for i in range(entrada.K):
        if entrada.num_cotxes[(classe + i) % entrada.K] > 0:
            # Afegim un cotxe a la solució parcial i continuem la cerca
            sol[k] = (classe + i) % entrada.K
            entrada.num_cotxes[sol[k]] -= 1
            cerca_exhaustiva_rec(k + 1, sol, entrada, pen + penalitzacio(sol, k, entrada), pen_min, classe, temps_ini)
            # Desfem l'elecció
            entrada.num_cotxes[sol[k]] += 1


def cerca_exhaustiva(entrada: Dades):
    """
    Donada una entrada, inicialitza la cerca exhaustica per tal d'iniciar la cerca recursiva
    """
    classe = cls_max(entrada) #classe amb més penalitzacions de totes
    sol: list[int] = [0] * entrada.C
    pen_min_ref:list[float] = [float('inf')]
    temps_ini = time.time()
    cerca_exhaustiva_rec(0, sol, entrada, 0, pen_min_ref, classe, temps_ini)


def main():
    entrada = llegeix_entrada()
    cerca_exhaustiva(entrada)
    

if __name__ == '__main__':
    main() 
