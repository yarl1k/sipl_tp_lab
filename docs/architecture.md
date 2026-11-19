# Архітектура

Проєкт розділений на незалежне ядро, CLI, засоби візуалізації та тести.

```text
source.sipl
    |
    v
lexer.py ---> Token + SourceSpan
    |
    v
parser.py ---> typed AST (ast.py) + concrete Parse Tree
    |                         |
    |                         +--> visualization/ (text, JSON, DOT, SVG)
    v
interpreter/ ---> State + ExecutionEvent + ExecutionTrace
    |
    v
cli.py ---> parse / check / run / trace + stable JSON output
```

## Модулі

- `lexer.py` перетворює текст на токени та фіксує позиції.
- `parser.py` реалізує recursive descent за граматикою з `grammar/sipl.ebnf`.
  `parse()` повертає AST, `parse_with_tree()` — AST, Parse Tree та токени.
- `ast.py` містить власні immutable dataclass-вузли для всіх синтаксичних
  категорій.
- `source.py` задає `Token` та `SourceSpan`.
- `interpreter/state.py` представляє стан змінних.
- `interpreter/runtime.py` реалізує обчислення та обмеження кроків.
- `interpreter/events.py` і `interpreter/trace.py` задають подієву модель.
- `visualization/` експортує дерева у текст, JSON, DOT і SVG без runtime-залежностей.
- `cli.py` надає консольний інтерфейс.
- `semantics/` залишено як точку розширення для явної побудови семантичних
  термів; завдання SEM-01/02 не входять до обраного набору.

## Архітектурні принципи

1. Frontend не дублює парсер або інтерпретатор: усі клієнти використовують
   стабільне Python API або CLI.
2. AST і Parse Tree мають SourceSpan, тому вузол можна пов'язати з фрагментом
   первинного тексту.
3. Візуалізатор отримує вже побудовані структури даних і нічого не парсить.
4. CLI JSON має `schema_version`, `status`, стабільні ключі та машинозчитувані
   помилки.
5. Код ядра не потребує сторонніх runtime-пакетів.
# Візуалізація Parse Tree та AST

Візуалізація генерується безпосередньо з об'єктів, які повертає парсер.
Вона не виконує повторного аналізу вихідного тексту.

- **Parse Tree** показує конкретні граматичні конструкції та термінальні
  символи (`begin`, `:=`, `;`, числа, змінні тощо).
- **AST** показує типізовані абстрактні вузли: `Assign`, `Sequence`, `If`,
  `While`, `Arithmetic +`, `Compare >` тощо. Дужки представлені групувальними
  вузлами.

Доступні формати:

- текстове дерево для термінала;
- JSON для інтеграцій;
- DOT для подальшої обробки Graphviz;
- SVG, який генерується власним Python-кодом і не потребує Graphviz.

Приклади:

```bash
sipl parse examples/power.sipl --view both
sipl parse examples/power.sipl --format svg --view parse-tree --output parse-tree.svg
sipl parse examples/power.sipl --format svg --view ast --output ast.svg
sipl parse examples/power.sipl --format svg --view both --output comparison.svg
```

`--view both` створює один SVG з конкретними Parse Tree та абстрактним AST як дві гілки в графі для порівняння.
