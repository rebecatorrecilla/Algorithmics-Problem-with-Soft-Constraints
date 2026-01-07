# METAHEURÍSTICA
# Pau Soler & Rebeca Torrecilla

from yogi import read
import sys
import time
import math
import random


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

    C, M, K = read(int), read(int), read(int) 
    Ce: list[int] = [read(int) for _ in range(M)] 
    Ne: list[int] = [read(int) for _ in range(M)]
    num_cotxes: list[int] = [] # Llista de quantitat de cotxes que s'han de fer de cada classe.
    Matriu_millores: list[list[int]] = [] # Col: classes, Files: si el cotxe té la millora o no.
    for _ in range(K):
        classe = read(int) 
        num_c = read(int) # Nombre de cotxes que hem de fer de la classe
        millores: list[int] = [read(int) for _ in range(M)] # Llista de quines millores té el cotxe d'aquesta classe
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

    # Iterem pel nombre de millores
    for m in range(entrada.M): 

        # Si el cotxe té la millora que estem mirant
        if entrada.Matriu_millores[sol[k]][m] == 1: 
            inici_fin = max(0, k - (entrada.Ne[m] - 1))
            comptador = 0
            
            # Iterem dins la finestra de cotxes
            for i in range(inici_fin, k + 1):
                if entrada.Matriu_millores[sol[i]][m] == 1: 
                    comptador += 1
                    
            # La penalització puja quan excedim el nombre de millores permeses en l'estació actual
            if comptador > entrada.Ce[m]:
                penalitzacio += (comptador - entrada.Ce[m])
                
    return penalitzacio


def penalitzacio_finestra(sol: list[int], idx: int, estacio_idx: int, entrada: Dades):
    """
    Retorna la penalització d'una estació concreta donada la posició 'idx' actual

    · pos: posició actual dins la finestra
    · count: comptador que codifica el nombre de millores necessàries de la finestra
    · cotxe_cls: conté la classe del cotxe segons la posició en la que ens trobem
    """
    
    ne = entrada.Ne[estacio_idx]
    ce = entrada.Ce[estacio_idx]
    count = 0
    
    for k in range(ne):
        pos = idx + k
        if 0 <= pos < len(sol):
            cotxe_cls = sol[pos]
            if cotxe_cls != -1 and entrada.Matriu_millores[cotxe_cls][estacio_idx] == 1:
                count += 1
                
    if count > ce:
        return count - ce
    return 0


def calcul_delta(sol: list[int], i:int, j: int, entrada: Dades) -> int:
    """
    Funció que porta a terme l'intercanvi entre dos indexos de la solució parcial
    i retorna la diferencia de penalització abans i després del canvi. Una delta negativa
    indicará que l'intercanvi realitzat ha donat lloc a una solució amb menor penalització
    i convé quedar-nos-la. 

    · pen_pre: penalització abans de l'intercanvi d'índexos
    · pen_pos: penalització després de l'intercanvi d'índexos
    · starts: set que conté els índexos de les finestres que envolten els índexos a intercanviar (i, j)
    """
    
    delta = 0

    for m in range(entrada.M):
        finestra = entrada.Ne[m]

        starts: set[int] = set()
        for s in range(i - finestra + 1, i + 1): starts.add(s)
        for s in range(j - finestra + 1, j + 1): starts.add(s)

        pen_pre = 0
        pen_pos = 0

        valid: list[int] = []

        # Càlcul de la penalització de la solució original
        for s in starts:
            if s >= -(finestra - 1) and s < entrada.C:
                valid.append(s)
                pen_pre += penalitzacio_finestra(sol, s, m, entrada)

        # Càlcul de la penalització de la solució amb els índexs (i, j) intercanviats
        sol[i], sol[j] = sol[j], sol[i]
        
        for s in valid:
            pen_pos += penalitzacio_finestra(sol, s, m, entrada)

        sol[i], sol[j] = sol[j], sol[i]
        
        delta += (pen_pos - pen_pre)
        
    return delta


# --- FUNCIONS PRINCIPALS DE BÚSQUEDA (GRASP, GREEDY, LOCAL SEARCH (SA)) ---


def local_search(pen_greedy: int, millor_sol: list[int], pen_min_global: list[float], entrada: Dades, temps_ini: float):
    """ 
    Simulated Annealing (SA). Cridem aquesta funció després d'obtenir una solució mitjançant 
    el mètode greedy. A partir d'aquí ens encarreguem de millorar-la mitjançant intercanvis aleatoris 
    de cotxes en les seves posicions per tal d'obtenir el resultat amb la menor penalització possible. 
    
    · temp: quant més alt sigui la temperatura la probabilitat d'agafar una pitjor solució que l'actual será més elevada
    · prob: probabilitat de Boltzmann
    · delta: variable que codifica la diferència de penalitzacions entre la solució posterior i l'anterior a l'intercanvi d'índexos
    """

    temp = 100.0
    min_temp = 0.001
    alpha = 0.995
    sol_actual = millor_sol[:]
    pen_actual = pen_greedy

    millor_sol_local = sol_actual[:]
    millor_pen_local = pen_actual

    it = 0

    while temp > min_temp:
        it += 1

        # Escollim dues posicions aleatòries de la solució
        i = random.randint(0, entrada.C - 1)
        j = random.randint(0, entrada.C - 1)
        if i == j: continue

        # La delta indicará si l'intercanvi dona lloc a una millor solució que la que teniem
        delta = calcul_delta(sol_actual, i, j, entrada)

        aceptar = False
        if delta < 0:
            aceptar = True
        else:
            # Amb la probabilitat de Boltzmann intercanviem o no la solució actual per una
            # pitjor per tal d'escapar de mínims locals
            prob = math.exp(-delta/temp)
            if random.random() < prob:
                aceptar = True

        if aceptar:
            sol_actual[i], sol_actual[j] = sol_actual[j], sol_actual[i]
            pen_actual += delta

            if pen_actual < millor_pen_local:
                millor_pen_local = pen_actual
                millor_sol_local = sol_actual[:]

                if millor_pen_local < pen_min_global[0]:
                    pen_min_global[0] = millor_pen_local

                    write_output(millor_sol_local, int(millor_pen_local), temps_ini)

        # Cada 10 iteracions actualitzem la temperatura (va disminuint)
        if it % 10 == 0: temp *= alpha
    
    return millor_sol_local, millor_pen_local


def calcula_penalitzacions_total(sol: list[int], entrada: Dades) -> int:
    """
    Donada una solució, calcula el nombre de penalitzacions que fa aquesta solució en total.

    · n_pen: variable a retornar, codifica la penalització total de la solució.
    · sol_ext: extensió de la solució amb cotxes sense millores (índex -1) per tal de poder mirar les finestres finals
    · comptador: enter que diu quants cotxes de la finestra actual necessiten millora
    """
    n_pen = 0
    M = len(entrada.Ce)
    sol_ext = sol + [-1]*(max(entrada.Ne)-1) 

    # Iterem pels cotxes de la finestra
    for i in range(len(sol_ext)): 
        # Iterem pel nombre de millores
        for m in range(M): 
            inici_fin = max(0, i - (entrada.Ne[m] - 1))
            finestra: list[int] = sol_ext[inici_fin:i+1] # Finestra a comprovar
            comptador = sum(entrada.Matriu_millores[idx][m] for idx in finestra if (idx != -1 and entrada.Matriu_millores[idx][m] == 1)) 
            
            if comptador > entrada.Ce[m]:
                # La penalització augmenta quan en la finestra tenim més millores de les que estan permeses en l'estació actual
                n_pen += (comptador - entrada.Ce[m]) 

    return n_pen


def greedy(entrada: Dades, rand: float) -> list[int]:
    """
    Funció que implementa un algorisme greedy. Comencem ordenant les classes de més a menys millores.
    Seguidament, escollim el cotxe amb més millores a fer que NO ens saturi cap de les finestres. 
    Si cap compleix això, escollim el que menys penalització generi.

    · rand: variable que codifica què tan aleatori volem que sigui el greedy (de 0 a 1)
    · ordenacio: llista que emmagatzema la solució a retornar
    · n_idx: llista que conté de manera ordenada (de millor a pitjor) les classes de cotxes a posar abans en la solució 
    · c_act: variable que codifica la millor classe de cotxe a posar a continuació
    """
    ordenacio: list[int] = [-1]*entrada.C 
    n_idx = sorter_opt(entrada.Matriu_millores)
    cotxes_restants: list[int] = entrada.num_cotxes[:]

    # Iterem pel nombre de cotxes que volem fer
    for i in range(entrada.C): 
        millor_c = -1
        min_pen = float("inf")

        # Iterem per les diferents classes
        for j in range(entrada.K): 
            c_act = n_idx[j]

            # Si ens queden cotxes d'aquesta classe per fer
            if cotxes_restants[c_act] > 0: 
                ordenacio[i] = c_act # Posem el candidat
                pen = penalitzacio_potencial(ordenacio, i, entrada) # Calculem quant penalitza posar aquest cotxe

                # Si trobem un cotxe que no penalitza, el posem
                if pen == 0: 
                    millor_c = c_act
                    min_pen = 0
                    break

                # Si hem trobat un cotxe que penalitza menys que el millor trobat, el guardem
                if pen < min_pen: 
                    millor_c = c_act
                    min_pen = pen

        # GREEDY: escollim la millor opció
        if random.random() > rand:
            ordenacio[i] = millor_c
            cotxes_restants[millor_c] -= 1
        else:
            # RCL: triem una opció a l'atzar entre els millors classes candidates
            candidats: list[int] = [k for k in range(entrada.K) if cotxes_restants[k] > 0] 
            eleccio = random.choice(candidats)
            ordenacio[i] = eleccio
            cotxes_restants[eleccio] -= 1

    return ordenacio


def grasp(entrada: Dades, pen_min_global: list[float], sol_greedy: list[int], temps_ini: float):
    """
    Funció que realitza l'algorisme GRASP, construiex una solució i porta a terme seguidament
    la seva millora mitjançant una local search (en aquest cas, Simulated Annealing)

    · randomness: variable que codifica què tan aleatori volem que sigui el greedy (de 0 a 1)
    · sol_greedy: solució construida mitjançant l'algorisme voraç
    · pen_greedy: penalització de la solució greedy calculada
    """
    
    randomness = 1 
    
    for i in range(entrada.C): sol_greedy[i] = -1

    # Construim la solució inicial
    if pen_min_global[0] == float('inf'):
        # Si és la primera iteració escollim la millor solució greedy
        sol_greedy = greedy(entrada, 0)
    else:
        # Si no és el primer cop que cridem la funció, hem de continuar buscant 
        # però ara en una altra localització una mica més aleatòria per evitar mínims locals
        sol_greedy = greedy(entrada, randomness)

    pen_greedy = calcula_penalitzacions_total(sol_greedy, entrada)
    if pen_greedy < pen_min_global[0]:
        pen_min_global[0] = pen_greedy
        print(pen_greedy) 
        write_output(sol_greedy, int(pen_greedy), temps_ini)

    # Millorem la solució actual amb una búsqueda local (SA)
    local_search(int(pen_greedy), sol_greedy, pen_min_global, entrada, temps_ini)


def main():
    entrada = llegeix_entrada()
    sol_greedy: list[int] = [-1] * entrada.C
    pen_min_global: list[float] = [float('inf')]
    temps_ini = time.time()

    while True:
        grasp(entrada, pen_min_global, sol_greedy, temps_ini)


if __name__ == '__main__':
    main() 


