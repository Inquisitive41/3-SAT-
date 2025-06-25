import numpy as np
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_dimacs(filename):
    clauses = []
    max_var = 0
    if not os.path.exists(filename):
        logging.error(f"Файл {filename} не найден.")
        return [], 0
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("c") or line.startswith("p"):
                    continue
                try:
                    clause = [int(x) for x in line.split() if int(x) != 0]
                    if clause:
                        clauses.append(clause)
                        max_var = max(max_var, max(abs(l) for l in clause))
                except Exception as e:
                    logging.warning(f"Ошибка парсинга строки: {line.strip()} — {e}")
    except Exception as e:
        logging.error(f"Ошибка чтения файла: {e}")
        return [], 0
    logging.info(f"Загружено {len(clauses)} клауз из {filename}")
    return clauses, max_var


def build_matrix(clauses, n_vars):
    m = len(clauses)
    M = np.zeros((m, n_vars), dtype=int)
    for i, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit) - 1
            if 0 <= var < n_vars:
                M[i, var] = 1 if lit > 0 else -1
            else:
                logging.warning(f"Переменная вне диапазона: {lit}")
    logging.info(f"Построена матрица {m}x{n_vars}")
    return M


def solve_sat(M, max_iter=100):
    n_vars = M.shape[1]
    # Детеминированная инициализация: все нули
    x = np.zeros(n_vars, dtype=int)
    logging.info(f"Начальное присваивание: {x}")
    for it in range(max_iter):
        satisfied = np.any(M * (1 - 2 * x) >= 0, axis=1)
        if np.all(satisfied):
            logging.info(f"SAT найден на {it} итерации")
            return "SAT", x
        improved = False
        for i in range(n_vars):
            x[i] = 1 - x[i]
            new_satisfied = np.any(M * (1 - 2 * x) >= 0, axis=1)
            if np.sum(new_satisfied) > np.sum(satisfied):
                satisfied = new_satisfied
                improved = True
                logging.info(f"Улучшение: переменная {i} -> {x[i]}")
            else:
                x[i] = 1 - x[i]
        if not improved:
            logging.info(f"Нет улучшений на {it} итерации, выход")
            break
    logging.info("UNSAT — решение не найдено")
    return "UNSAT", None


def matrix_rank_analysis(M):
    try:
        rank = np.linalg.matrix_rank(M)
        logging.info(f"Ранг матрицы: {rank} из {M.shape[1]}")
        return rank
    except Exception as e:
        logging.error(f"Ошибка вычисления ранга: {e}")
        return None


# Пример использования
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "example.cnf"
    clauses, n_vars = parse_dimacs(filename)
    if not clauses or n_vars == 0:
        exit(1)
    M = build_matrix(clauses, n_vars)
    matrix_rank_analysis(M)
    result, assignment = solve_sat(M)
    print(f"Result: {result}")
    if assignment is not None:
        print(f"Assignment: {assignment[:n_vars]}")
