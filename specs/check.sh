#!/usr/bin/env bash
# Опциональная проверка TLA+-спецификации через TLC.
# Требует Java и tla2tools.jar (переменная TLA_TOOLS или файл рядом со скриптом).
# Без них скрипт корректно завершается с подсказкой (CI не падает).
#
# Использование:
#   ./check.sh                      # корректная конфигурация (Transition.cfg)
#   ./check.sh Transition_leaky.cfg # дефектная: ожидается нарушение Consistency
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
CFG="${1:-Transition.cfg}"
JAR="${TLA_TOOLS:-$DIR/tla2tools.jar}"

if ! command -v java >/dev/null 2>&1; then
    echo "Java не найдена — проверку TLC пропускаем (см. docs/VERIFICATION.md)."
    exit 0
fi
if [ ! -f "$JAR" ]; then
    echo "tla2tools.jar не найден (TLA_TOOLS не задан) — проверку TLC пропускаем."
    echo "Скачать: https://github.com/tlaplus/tlaplus/releases"
    exit 0
fi

cd "$DIR"
echo "TLC: Transition.tla с конфигурацией $CFG"
java -XX:+UseParallelGC -cp "$JAR" tlc2.TLC -config "$CFG" Transition.tla
