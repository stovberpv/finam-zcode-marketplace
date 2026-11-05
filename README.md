<img src="assets/finam-logo.svg" width="48" alt="Финам">

# finam · marketplace для ZCode

Общие инструменты команды для работы с Jira и GitLab.

## Routine · 0.1.0 alpha

<img src="plugins/routine/assets/icon.png" width="128" alt="Routine">

Единый формат задач Jira, описаний MR и результатов проектного ревью. Два скилла: инициализация проекта и сопровождение текущей работы.

**[Установка и примеры команд для коллег](docs/quickstart.md)**

В ZCode: **Settings → Plugins → Create → Add marketplace** → `https://github.com/stovberpv/finam-zcode-marketplace.git` → **Personal → finam → routine → Install**.

- `/routine_init` — исследовать проект и согласовать настройки, правила и исполнителя ревью.
- `/routine` — оформить Jira/MR, вызвать проектное ревью и оформить его результат.

[Требования и устройство плагина](plugins/routine/README.md) · [Контракт проекта](plugins/routine/references/project-contract.md) · [Шаблоны](plugins/routine/templates/README.md)

Настройки проекта: `.harness/workflow/project.yaml`. Код, коммиты и push остаются у проектных инструментов. Для Jira нужны официальный Atlassian MCP и TWG, для GitLab — настроенный glab. Плагин не устанавливает эти зависимости.

## Разработка

```sh
python3 scripts/build_plugin.py
python3 -m unittest discover -s tests -v
```

Тесты разработки требуют PyYAML; сборка использует стандартную библиотеку Python. Архив для локальной установки создаётся в `dist/`.

При обновлении менять version в `marketplace.json` и `.zcode-plugin/plugin.json` вместе. Затем в ZCode обновить источник marketplace и проверить обновления плагина.

Структурные проверки выполнены. Реальная установка и работа интеграций в конкретной версии ZCode должны быть проверены на пилоте.
