# Algorithmics Problem with Soft Constraints
## Rebeca Torrecilla & Pau Soler
---
![Language](https://img.shields.io/badge/Language-Python-blue)
![Compiler](https://img.shields.io/badge/Compiler-Codon-green)
![Course](https://img.shields.io/badge/Course-Algor%C3%ADsmia%20i%20Programaci%C3%B3%203-red)
![University](https://img.shields.io/badge/University-UPC-blue)

## Project Overview

The goal is to optimize the production sequence of cars in a manufacturing line to minimize efficiency penalties.

Each car model belongs to a class defined by a set of required upgrades (GPS, sunroof, etc.). Each upgrade station $e$ has a capacity constraint defined by $(c_e, n_e)$: for any sequence of $n_e$ cars, at most $c_e$ should require the upgrade.

Since these are **soft constraints**, violations are permitted but incur a penalty. The objective is to order the cars to minimize the **total penalty cost**.

### Penalty Calculation
For a sliding window of size $n_e$, if $k$ cars require the upgrade, the penalty is: $\text{Penalty} = \max(0, k - c_e)$.

## Requirements & Compilation

The algorithms are written in **Python** syntax but designed to be compiled with **[Codon](https://github.com/exaloop/codon)** for high performance.

### Files
The project consists of three main source files:

1.  **`exh.py`**: Exhaustive search algorithm (Backtracking/Branch & Bound).
2.  **`greedy.py`**: Greedy algorithm (Fast heuristic).
3.  **`mh.py`**: Metaheuristic approach (e.g., GRASP, Genetic Algorithm, Simulated Annealing).

### Compilation
To compile the scripts using Codon:
```bash
codon build -release exh.py
codon build -release greedy.py
codon build -release mh.py
```

## Usage
The executables read the input from Standard Input (stdin) and write the solution to a file specified as the first argument.
```bash
./executable output_file.txt < input_file.txt
```
**Note**: For exh.cc and mh.cc, the program is designed to continuously overwrite the output_file.txt whenever a better solution is found. This ensures valid output even if the execution is interrupted (Time Limit: 60 seconds).

## Input/Output format
**Input Format**
* 












