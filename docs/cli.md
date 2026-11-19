# CLI

Після встановлення доступна команда `sipl`. У середовищі розробки можна
використати `python -m sipl`.

## Команди

```bash
sipl parse examples/power.sipl
sipl parse examples/power.sipl --view ast
sipl parse examples/power.sipl --format json
sipl parse examples/power.sipl --format svg --view parse-tree --output parse-tree.svg
sipl parse examples/power.sipl --format svg --view ast --output ast.svg
sipl parse examples/power.sipl --format svg --view both --output comparison.svg
sipl parse examples/power.sipl --format dot --view ast --output ast.dot

sipl check examples/power.sipl
sipl check examples/power.sipl --format json

sipl run examples/power.sipl --set X=5 --set Y=2
sipl run examples/factorial.sipl --set N=5 --set R=1 --format json

sipl trace examples/power.sipl --set X=5 --set Y=2
sipl trace examples/power.sipl --set X=5 --set Y=2 --format json
```

## Параметри

- `--format text|json` доступний для `check`, `run`, `trace`.
- `parse` додатково підтримує `dot` та `svg`.
- `parse --view parse-tree|ast|both` обирає представлення. Для `dot` і `svg` можна вибрати одне дерево або `both` для порівняльного графа.
- `--set X=VALUE` задає початкове значення; параметр можна повторювати.
- `--max-steps N` задає ліміт виконання для `run` і `trace`.
- коди завершення: `0` — успіх, `1` — помилка обробки або виконання.

`parse` повертає власні Parse Tree та AST. `check` лише перевіряє синтаксис;
`run` повертає кінцевий стан; `trace` додатково повертає впорядковані події.
# JSON API та формат Trace

Усі JSON-відповіді мають `schema_version: "1.0"` та `status: "ok"` або
`status: "error"`. Успішний результат виконання має поля `final_state` і
`steps`; `trace` додатково має `events`. Вхідний стан передається через CLI
і повертається як `initial_state`.

## Parse

```json
{
  "schema_version": "1.0",
  "status": "ok",
  "parse_tree": { "type": "nonterminal", "name": "Program", "children": [] },
  "ast": { "type": "Program", "body": {} }
}
```

Приклад вище показує форму об'єкта; `children` та AST-вузли в реальній
відповіді містять повне дерево. Кожен AST/Parse Tree вузол має `span` із
нульовими offset та однобазовими line/column.

## Run

```json
{
  "schema_version": "1.0",
  "status": "ok",
  "final_state": { "R": 25, "X": 5, "Y": 0 },
  "steps": 10,
  "initial_state": { "X": 5, "Y": 2 }
}
```

Значення `steps` — кількість входів у вузли операторів. Складені оператори,
блоки та `skip` також рахуються.

## Trace event

Кожна подія має `sequence`, `type`, `message`, `span`, `state`, `details`.
Типи подій: `ProgramStarted`, `BeforeStatement`, `VariableChanged`,
`ConditionChecked`, `AfterStatement`, `ProgramFinished`, `ProgramFailed`.

`ConditionChecked.details` містить `construct` (`if` або `while`), `result`
та `iteration`. `VariableChanged.details` містить ім'я й старе/нове значення.

## Помилки

```json
{
  "schema_version": "1.0",
  "status": "error",
  "error": {
    "type": "ParseError",
    "message": "Очікувався ...",
    "span": {}
  }
}
```
