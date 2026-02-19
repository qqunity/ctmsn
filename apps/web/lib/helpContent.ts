export const TASK_DESCRIPTION = `
## Лабораторная работа: Семантические сети и форсинг

### Цель работы
Освоить методы построения и анализа семантических сетей с использованием
параметризации, трёхзначной логики и механизма форсинга.

### Порядок выполнения
1. **Загрузите сценарий** — выберите сценарий из выпадающего списка и нажмите «Загрузить».
2. **Изучите граф** — рассмотрите концепты (узлы) и предикаты (рёбра) семантической сети.
3. **Создайте переменные** — определите переменные с доменами значений.
4. **Задайте контекст** — присвойте значения переменным (частичная подстановка).
5. **Составьте формулы** — создайте логические формулы из атомов (факты, равенства) и связок (NOT, AND, OR, IMPLIES).
6. **Проверьте форсинг** — определите, вынуждает ли текущий контекст истинность формулы.
7. **Проанализируйте результат** — изучите таблицу уравнений и статус вычислений.

### Критерии оценки
- Корректность построения семантической сети
- Правильность определения переменных и контекстов
- Верная интерпретация результатов форсинга
`.trim();

export interface GlossaryEntry {
  term: string;
  termEn: string;
  definition: string;
}

export const GLOSSARY: GlossaryEntry[] = [
  {
    term: "Концепт",
    termEn: "Concept",
    definition:
      "Базовый элемент семантической сети — именованная сущность (узел графа). Примеры: «Человек», «Рыба», «Удочка».",
  },
  {
    term: "Предикат",
    termEn: "Predicate",
    definition:
      "Именованное отношение между концептами (ребро графа). Задаёт арность и семантику связи. Примеры: «является», «имеет», «ловит».",
  },
  {
    term: "Факт",
    termEn: "Statement / Fact",
    definition:
      "Конкретный экземпляр предиката, связывающий конкретные концепты. Например: «Человек ловит Рыбу».",
  },
  {
    term: "Домен",
    termEn: "Domain",
    definition:
      "Множество допустимых значений переменной. Может быть конечным перечислением или диапазоном.",
  },
  {
    term: "Переменная",
    termEn: "Variable",
    definition:
      "Параметр с именем и доменом. Используется для параметризации сети — подстановки конкретных значений.",
  },
  {
    term: "Контекст",
    termEn: "Context",
    definition:
      "Частичное присваивание значений переменным. Определяет конкретную «точку зрения» на параметризованную сеть.",
  },
  {
    term: "Формула",
    termEn: "Formula",
    definition:
      "Логическое выражение в трёхзначной логике. Строится из атомов (FactAtom, EqAtom) и связок (NOT, AND, OR, IMPLIES).",
  },
  {
    term: "Форсинг",
    termEn: "Forcing",
    definition:
      "Механизм проверки: вынуждает ли данный контекст истинность формулы при всех возможных доопределениях переменных.",
  },
];

export type TruthValue = "T" | "F" | "U";

export interface TruthTableRow {
  inputs: TruthValue[];
  output: TruthValue;
}

export interface TruthTable {
  name: string;
  headers: string[];
  rows: TruthTableRow[];
}

export const TRUTH_TABLES: TruthTable[] = [
  {
    name: "NOT",
    headers: ["A", "¬A"],
    rows: [
      { inputs: ["T"], output: "F" },
      { inputs: ["F"], output: "T" },
      { inputs: ["U"], output: "U" },
    ],
  },
  {
    name: "AND",
    headers: ["A", "B", "A ∧ B"],
    rows: [
      { inputs: ["T", "T"], output: "T" },
      { inputs: ["T", "F"], output: "F" },
      { inputs: ["T", "U"], output: "U" },
      { inputs: ["F", "T"], output: "F" },
      { inputs: ["F", "F"], output: "F" },
      { inputs: ["F", "U"], output: "F" },
      { inputs: ["U", "T"], output: "U" },
      { inputs: ["U", "F"], output: "F" },
      { inputs: ["U", "U"], output: "U" },
    ],
  },
  {
    name: "OR",
    headers: ["A", "B", "A ∨ B"],
    rows: [
      { inputs: ["T", "T"], output: "T" },
      { inputs: ["T", "F"], output: "T" },
      { inputs: ["T", "U"], output: "T" },
      { inputs: ["F", "T"], output: "T" },
      { inputs: ["F", "F"], output: "F" },
      { inputs: ["F", "U"], output: "U" },
      { inputs: ["U", "T"], output: "T" },
      { inputs: ["U", "F"], output: "U" },
      { inputs: ["U", "U"], output: "U" },
    ],
  },
  {
    name: "IMPLIES",
    headers: ["A", "B", "A → B"],
    rows: [
      { inputs: ["T", "T"], output: "T" },
      { inputs: ["T", "F"], output: "F" },
      { inputs: ["T", "U"], output: "U" },
      { inputs: ["F", "T"], output: "T" },
      { inputs: ["F", "F"], output: "T" },
      { inputs: ["F", "U"], output: "T" },
      { inputs: ["U", "T"], output: "T" },
      { inputs: ["U", "F"], output: "U" },
      { inputs: ["U", "U"], output: "U" },
    ],
  },
];

export const TOOLTIPS: Record<string, string> = {
  undo: "Отменить последнее действие (Ctrl+Z)",
  redo: "Повторить отменённое действие (Ctrl+Shift+Z)",
  exportJson: "Скачать workspace как JSON-файл",
  importJson: "Загрузить workspace из JSON-файла",
  exportPng: "Сохранить граф как PNG-изображение",
  help: "Открыть справку: задание, логика, глоссарий",
};
