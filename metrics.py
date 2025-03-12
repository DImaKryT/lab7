import radon.metrics as rm
import radon.raw as rr
import radon.complexity as rc
import re

# Шлях до файлу, який потрібно аналізувати
script_path = "testing2SW.py"

def read_code(filepath):
    """Зчитує код із файлу"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def calculate_metrics(code):
    """Обчислення базових метрик"""
    raw_metrics = rr.analyze(code)
    complexity_metrics = rc.cc_visit(code)
    maintainability = rm.mi_visit(code, True)

    # Підрахунок загальної цикломатичної складності
    total_complexity = sum(block.complexity for block in complexity_metrics)

    # Підрахунок кількості операторів та операндів (Холстеда)
    operators = re.findall(r"\b(if|for|while|return|def|class|try|except)\b", code)
    operands = re.findall(r"[a-zA-Z_][a-zA-Z_0-9]*", code)
    
    n1, n2 = len(set(operators)), len(set(operands))
    N1, N2 = len(operators), len(operands)

    # Метрика Холстеда
    volume = (N1 + N2) * (n1 + n2)

    return {
        "LOC": raw_metrics.loc,  # Кількість рядків коду
        "SLOC": raw_metrics.sloc,  # Кількість значущих рядків
        "Maintainability Index": maintainability,
        "Cyclomatic Complexity": total_complexity,
        "Halstead Volume": volume
    }

def zolnovsky_simmons_theyer(metrics):
    """Обчислення гібридної метрики"""
    a, b, c, d = metrics["Cyclomatic Complexity"], metrics["Halstead Volume"], metrics["LOC"], metrics["SLOC"]
    return 0.3 * a + 0.4 * b + 0.2 * c + 0.1 * d

if __name__ == "__main__":
    code = read_code(script_path)
    metrics = calculate_metrics(code)
    hybrid_metric = zolnovsky_simmons_theyer(metrics)

    print(" **Результати аналізу коду**:")
    for key, value in metrics.items():
        print(f"-- {key}: {value}")
    
    print(f"\n **Гібридна метрика Зольновського-Сіммонса-Тейера**: {hybrid_metric:.2f}")
