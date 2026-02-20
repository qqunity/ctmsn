# Сценарий lab1_university — Лабораторная работа 1

Предметная область «Университет». Вводный сценарий для знакомства с системой построения семантических сетей.

## Концепты (6)

| ID          | Описание                  |
|-------------|---------------------------|
| university  | Университет               |
| dept_cs     | Кафедра ИВТ               |
| course_db   | Курс «Базы данных»        |
| course_ai   | Курс «Искусственный интеллект» |
| ivanov      | Преподаватель Иванов       |
| petrov      | Студент Петров             |

## Предикаты (5, бинарные)

| Имя          | Роли              | Описание                |
|--------------|--------------------|-------------------------|
| belongs_to   | (part, whole)      | Принадлежит             |
| teaches      | (teacher, course)  | Преподаёт               |
| enrolled_in  | (student, course)  | Записан на курс         |
| works_at     | (person, place)    | Работает в              |
| studies_at   | (student, department) | Учится на кафедре    |

## Факты (7)

1. `belongs_to(dept_cs, university)` — кафедра ИВТ принадлежит университету
2. `works_at(ivanov, dept_cs)` — Иванов работает на кафедре ИВТ
3. `teaches(ivanov, course_db)` — Иванов преподаёт «Базы данных»
4. `teaches(ivanov, course_ai)` — Иванов преподаёт «ИИ»
5. `enrolled_in(petrov, course_db)` — Петров записан на «Базы данных»
6. `enrolled_in(petrov, course_ai)` — Петров записан на «ИИ»
7. `studies_at(petrov, dept_cs)` — Петров учится на кафедре ИВТ

## Переменные (3)

| Имя     | Домен                   | Начальное значение |
|---------|-------------------------|--------------------|
| student | {petrov}                | —                  |
| course  | {course_db, course_ai}  | course_db          |
| teacher | {ivanov}                | —                  |

## Цель (goal)

```
enrolled_in(petrov, course_db) AND studies_at(petrov, dept_cs) AND teaches(ivanov, course_db)
```

Все три факта присутствуют в сети — forcing возвращает TRUE.

## Условия (constraints)

1. `belongs_to(dept_cs, university)` — TRUE
2. `works_at(ivanov, dept_cs)` — TRUE
3. `NOT teaches(petrov, course_db)` — TRUE (Петров не преподаёт)
