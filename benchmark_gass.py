import subprocess
import sys
import time
import numpy as np
import os
import csv


# Генерация случайного 3-SAT CNF
def generate_cnf(filename, n_vars, n_clauses, sat=True, seed=None):
    rng = np.random.default_rng(seed)
    with open(filename, "w") as f:
        f.write(f"p cnf {n_vars} {n_clauses}\n")
        for _ in range(n_clauses):
            clause = set()
            while len(clause) < 3:
                var = rng.integers(1, n_vars + 1)
                sign = rng.choice([-1, 1])
                clause.add(sign * var)
            f.write(" ".join(map(str, clause)) + " 0\n")
        # Для SAT-примеров добавим одну клаузу, которая точно выполнима
        if sat:
            f.write(f"{rng.choice([1, -1]) * rng.integers(1, n_vars+1)} 0\n")


# Парсинг логов для метрик
def parse_metrics(output):
    metrics = {
        "rank": None,
        "iterations": None,
        "result": None,
        "warnings": 0,
        "errors": 0
    }
    for line in output.splitlines():
        if "Ранг матрицы:" in line:
            try:
                metrics["rank"] = int(
                    line.split("Ранг матрицы:")[1].split("из")[0].strip()
                )
            except:
                pass
        if "SAT найден на" in line or "Решение найдено через модульный фильтр" in line:
            metrics["iterations"] = 0  # Для модульного фильтра итерации не считаются
        if "Результат:" in line or "Result:" in line:
            metrics["result"] = line.split(":")[-1].strip()
        if "WARNING" in line or "Предупреждение" in line:
            metrics["warnings"] += 1
        if "ERROR" in line or "Ошибка" in line:
            metrics["errors"] += 1
    return metrics


def run_solver(filename, modulo=19):
    start = time.time()
    result = subprocess.run(
        [sys.executable, "P_NP.py", filename], capture_output=True, text=True
    )
    elapsed = time.time() - start
    metrics = parse_metrics(result.stdout + result.stderr)
    metrics["time_sec"] = elapsed
    return metrics, result.stdout + result.stderr


# Основной бенчмарк
sizes = [10, 50, 100, 500, 1000]
clauses_per_var = 4
results = []

os.makedirs("benchmarks", exist_ok=True)

for n_vars in sizes:
    n_clauses = n_vars * clauses_per_var
    for sat in [True, False]:
        fname = (
            f"benchmarks/test_{n_vars}v_{n_clauses}c_{'sat' if sat else 'unsat'}.cnf"
        )
        generate_cnf(fname, n_vars, n_clauses, sat=sat, seed=n_vars * 100 + int(sat))
        metrics, log = run_solver(fname)
        metrics.update(
            {
                "file": fname,
                "n_vars": n_vars,
                "n_clauses": n_clauses,
                "sat_target": "SAT" if sat else "UNSAT",
            }
        )
        results.append(metrics)
        print(
            f"{fname}: {metrics['result']} за {metrics['time_sec']:.3f} сек, ранг={metrics['rank']}, предупреждений={metrics['warnings']}, ошибок={metrics['errors']}"
        )

# Сохраняем в CSV
with open("benchmark_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "file",
            "n_vars",
            "n_clauses",
            "sat_target",
            "result",
            "rank",
            "time_sec",
            "warnings",
            "errors",
        ],
    )
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("Бенчмарк завершён. Результаты сохранены в benchmark_results.csv")
