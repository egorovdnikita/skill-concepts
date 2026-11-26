# skill-concepts

Скилл Claude «concepts»: генерация, правки и аудит UI-концептов (HTML, Figma через MCP, Next/Tailwind/Shadcn).

## Как устроена синхронизация

| Где | Роль | Как обновляется |
|---|---|---|
| claude.ai → Skills → `concepts` | источник правды | правки через карточки «Обновить скилл» в чате |
| GitHub `egorovdnikita/skill-concepts` | зеркало и история версий | после каждой правки в сессии + ежедневная задача по расписанию сравнивает и пушит |
| Mac `~/.claude/skills/concepts` | копия для локального Claude Code | `git pull` каждые 30 минут (launchd), ставится `scripts/install-local.sh` |

Правь скилл в claude.ai, а не здесь: правки в репо поверх будут перезаписаны при следующей синхронизации.

## Локальная установка (один раз)

```sh
gh repo clone egorovdnikita/skill-concepts /tmp/skill-concepts && bash /tmp/skill-concepts/scripts/install-local.sh
```

Скрипт клонирует репо в `~/.claude/skills/concepts` (старую папку переименует в `.bak.*`) и ставит launchd-агент `com.egorovdnikita.skill-concepts`, который подтягивает обновления каждые 30 минут и при входе в систему.

Удалить автообновление: `launchctl unload ~/Library/LaunchAgents/com.egorovdnikita.skill-concepts.plist && rm ~/Library/LaunchAgents/com.egorovdnikita.skill-concepts.plist`.
