import subprocess
import sys


def run_solver(filename):
    result = subprocess.run(
        [sys.executable, "P_NP.py", filename], capture_output=True, text=True
    )
    return result.stdout + result.stderr


def test_sat():
    output = run_solver("example.cnf")
    assert "Result: SAT" in output, "SAT-тест не пройден!"
    print("SAT-тест: OK")


def test_unsat():
    output = run_solver("example_unsat.cnf")
    assert "Result: UNSAT" in output, "UNSAT-тест не пройден!"
    print("UNSAT-тест: OK")


if __name__ == "__main__":
    test_sat()
    test_unsat()
    print("Все тесты пройдены успешно.")
