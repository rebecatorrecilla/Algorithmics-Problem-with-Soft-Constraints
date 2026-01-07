import subprocess
import os
import glob
import sys
import time

# --- CONFIGURACIÓ GLOBAL ---
# Aquestes variables s'actualitzaran segons l'input de l'usuari
SOURCE_FILE = ""      
EXECUTABLE = ""       
CHECKER = "./checker"          # El programa validador
BENCH_DIR = "public_benchs"    # Carpeta on hi ha els tests
OUTPUT_FILE = "sort.txt"       # Fitxer temporal per guardar la sortida
MAX_EXEC_TIME = 10.0           # Temps màxim d'execució per test (en segons)

# Colors per la terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def compile_code():
    """Compila el codi utilitzant codon."""
    print(f"{BOLD}--- 1. COMPILANT {SOURCE_FILE} ---{RESET}")
    try:
        # Executem la comanda de compilació
        cmd = ["codon", "build", "-release", SOURCE_FILE]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{GREEN}Compilació exitosa!{RESET}\n")
            return True
        else:
            print(f"{RED}Error de compilació:{RESET}")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print(f"{RED}Error: No s'ha trobat la comanda 'codon'. Assegura't que està instal·lada.{RESET}")
        return False

def run_benchmarks():
    """Executa els tests un per un."""
    print(f"{BOLD}--- 2. EXECUTANT TESTS AMB {EXECUTABLE} (Timeout: {MAX_EXEC_TIME}s) ---{RESET}")
    
    # Busquem tots els fitxers .txt a la carpeta de benchs
    test_files = sorted(glob.glob(os.path.join(BENCH_DIR, "*.txt")))
    
    if not test_files:
        print(f"No s'han trobat fitxers .txt a la carpeta {BENCH_DIR}")
        return

    # Comprovem que el checker existeix
    if not os.path.exists(CHECKER):
        print(f"{RED}Error: No s'ha trobat el fitxer '{CHECKER}'{RESET}")
        return

    total_tests = len(test_files)
    passed = 0
    failed = 0

    for test_path in test_files:
        test_name = os.path.basename(test_path)
        runtime_error = False
        timeout_reached = False
        
        # 1. EXECUTAR L'ALGORISME
        # Equival a: ./executable sort.txt < test.txt
        try:
            start_time = time.time()
            with open(test_path, 'r') as input_f:
                # subprocess.run espera fins que el procés acaba o salta el timeout
                proc = subprocess.run(
                    [EXECUTABLE, OUTPUT_FILE], 
                    stdin=input_f, 
                    capture_output=True, 
                    text=True, 
                    timeout=MAX_EXEC_TIME
                )
            
            elapsed = time.time() - start_time
            
            if proc.returncode != 0:
                print(f"[{test_name}] {RED}ERROR EXECUTANT (Runtime Error){RESET}")
                print(proc.stderr)
                failed += 1
                runtime_error = True

        except subprocess.TimeoutExpired:
            elapsed = MAX_EXEC_TIME
            timeout_reached = True
            # No marquem runtime_error com True, volem comprovar el resultat parcial

        except Exception as e:
            print(f"[{test_name}] {RED}EXCEPCIÓ: {e}{RESET}")
            failed += 1
            runtime_error = True

        if runtime_error:
            continue

        # 2. EXECUTAR EL CHECKER
        # Equival a: ./checker test.txt sort.txt
        try:
            check_cmd = [CHECKER, test_path, OUTPUT_FILE]
            check_res = subprocess.run(check_cmd, capture_output=True, text=True)
            
            output_checker = check_res.stdout.strip()
            
            prefix = f"[{test_name}] "
            if timeout_reached:
                prefix += f"{YELLOW}TIMEOUT ({elapsed}s){RESET} -> "
            else:
                prefix += f"DONE ({elapsed:.3f}s) -> "

            # Comprovem si el checker diu "OK"
            if "Solution is OK" in output_checker:
                passed += 1
                print(f"{prefix}{GREEN}PASS{RESET} {output_checker.replace('Solution is OK', '')}")
            else:
                failed += 1
                print(f"{prefix}{RED}FAIL{RESET}")
                print(f"   Sortida del checker:\n   {output_checker}")
                
        except Exception as e:
            print(f"[{test_name}] {RED}ERROR CHECKER: {e}{RESET}")
            failed += 1

    # --- RESUM FINAL ---
    print(f"\n{BOLD}--- RESUM ({EXECUTABLE}) ---{RESET}")
    print(f"Total: {total_tests}")
    print(f"Passats: {GREEN}{passed}{RESET}")
    print(f"Fallats: {RED}{failed}{RESET}")
    
    # Neteja (opcional)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

if __name__ == "__main__":
    # Comprovem els arguments d'entrada
    if len(sys.argv) != 2:
        print(f"{RED}Error: Has d'especificar l'algorisme a provar.{RESET}")
        print(f"Ús: python3 run_tests.py <greedy|exh|mh>")
        sys.exit(1)

    algo = sys.argv[1].lower()
    valid_algos = ["greedy", "exh", "mh"]

    if algo not in valid_algos:
        print(f"{RED}Error: L'algorisme '{algo}' no és vàlid.{RESET}")
        print(f"Opcions vàlides: {', '.join(valid_algos)}")
        sys.exit(1)

    # Actualitzem les variables globals segons l'input
    SOURCE_FILE = f"{algo}.py"
    EXECUTABLE = f"./{algo}"

    # Comprovem que el fitxer font existeix
    if not os.path.exists(SOURCE_FILE):
        print(f"{RED}Error: No s'ha trobat el fitxer '{SOURCE_FILE}'.{RESET}")
        sys.exit(1)

    # Executem el flux normal
    if compile_code():
        run_benchmarks()