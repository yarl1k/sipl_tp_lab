# SIPL Language Toolkit

[![CI](https://github.com/yarl1k/sipl_tp_lab/actions/workflows/ci.yml/badge.svg)](https://github.com/yarl1k/sipl_tp_lab/actions/workflows/ci.yml)

## Обрані завдання

| ID | Реалізація                                                                                   |
|-|----------------------------------------------------------------------------------------------|
| CORE-01 | EBNF, лексика, позитивні й негативні conformance fixtures                                    |
| CORE-02 | Recursive descent parser, власні AST-вузли, `SourceSpan`, Parse Tree                         |
| CORE-03 | Інтерпретатор, стан змінних, ліміт кроків                                                    |
| CORE-04 | Події `BeforeStatement`, `AfterStatement`, `VariableChanged`, `ConditionChecked`, завершення |
| CORE-05 | CLI `parse`, `check`, `run`, `trace`, структурований JSON                                    |
| CORE-06 | Conformance suite з очікуваною AST-формою, станом або категорією помилки                     |
| VIS-01 | Parse Tree: текст, JSON, DOT, SVG                                                            |
| VIS-02 | AST: текст, JSON, DOT, SVG; окреме представлення від Parse Tree                              |
| REL-01 | GitHub Actions: Ruff, mypy, pytest/coverage, build                                           |
| REL-02 | SemVer, CHANGELOG, workflow GitHub Release                                                   |
| | Разом: 10.5 балів                                                                            |

## Структура

```text
sipl/
├── grammar/
│   └── sipl.ebnf
├── src/sipl/
│   ├── parser.py
│   ├── lexer.py
│   ├── ast.py
│   ├── source.py
│   ├── errors.py
│   ├── serialization.py
│   ├── cli.py
│   ├── interpreter/
│   └── visualization/
├── examples/
├── tests/
│   └── conformance/
└── docs/
```

Додатково є `.github/workflows/`, `pyproject.toml`, `README.md` і `CHANGELOG.md`.
Також присутні додаткові файли, що покращують якість коду та спрощують роботу, наприклад `errors.py`

## Встановлення для розробки

Потрібен Python 3.12 або новіший.

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Сторонніх runtime-залежностей у ядра немає. Dev-залежності потрібні лише для
тестів, перевірок якості та збірки.

## Швидкий запуск

```bash
sipl check examples/power.sipl
sipl parse examples/power.sipl --view both
sipl run examples/power.sipl --set X=5 --set Y=2
sipl trace examples/power.sipl --set X=5 --set Y=2
```

## Візуалізація

```bash
sipl parse examples/power.sipl --format svg --view parse-tree --output parse-tree.svg
sipl parse examples/power.sipl --format svg --view ast --output ast.svg
sipl parse examples/power.sipl --format svg --view both --output comparison.svg
sipl parse examples/power.sipl --format dot --view ast --output ast.dot
```

## Тестування

```bash
pytest
pytest --cov=sipl --cov-report=term-missing --cov-fail-under=80
ruff check src tests
mypy src/sipl
```

Conformance fixtures розташовані в `tests/conformance/valid/` та
`tests/conformance/invalid/`; очікувані AST-форми, стани та типи помилок описані
в `tests/conformance/cases.json`. У поточній перевірці: 38/38 автоматичних тестів,
24/24 conformance cases і 91.4% загального покриття пакета.

## Пакування та реліз

```bash
python -m build
```

```bash
git tag v0.1.0
git push origin v0.1.0
```

Workflow `.github/workflows/release.yml` збирає wheel/sdist, створює GitHub
Release.

## Додаткова інформація

- Оператори введення/виведення відсутні в SIPL; початкові значення задаються
  через `--set X=VALUE`.
- Використовується одна велика латинська літера для імені змінної.
- Підтримуються лише конструкції, перелічені в `docs/language-spec.md`.
- Для захисту від нескінченних циклів діє `--max-steps` (типово 100 000).
