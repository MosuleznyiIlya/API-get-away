# Definition of Done

## Backend DoD

- [ ] Код написан и соответствует Coding Standards
- [ ] Unit tests написаны и проходят (coverage >= 90% для сервисов)
- [ ] Integration tests написаны для API endpoints
- [ ] Миграции созданы и протестированы
- [ ] API документация обновлена (если изменялся контракт)
- [ ] Code review пройден (минимум 1 approve)
- [ ] Линтеры проходят (flake8, black, mypy)
- [ ] Нет security vulnerabilities (bandit, safety)
- [ ] Performance impact оценен (для критичных путей)
- [ ] Логи добавлены для важных операций
- [ ] Метрики добавлены для новых функций

## Frontend DoD

- [ ] Компонент/функция реализована по UI Guidelines
- [ ] Unit tests написаны (coverage >= 80%)
- [ ] Integration tests для API interactions
- [ ] TypeScript types корректны (strict mode)
- [ ] Responsive design проверен (mobile, tablet, desktop)
- [ ] Accessibility проверена (ARIA labels, keyboard navigation)
- [ ] Code review пройден (минимум 1 approve)
- [ ] Линтеры проходят (ESLint, Prettier)
- [ ] Storybook обновлен (для компонентов)
- [ ] Error states обработаны
- [ ] Loading states обработаны

## Infrastructure DoD

- [ ] Docker образ собирается без ошибок
- [ ] Health checks работают
- [ ] Environment variables документированы
- [ ] Docker Compose конфигурация обновлена
- [ ] Monitoring и alerting настроены (если применимо)
- [ ] Deployment скрипты обновлены
- [ ] Backup strategy проверена (для БД изменений)
- [ ] Security scan пройден (Trivy, Snyk)
- [ ] Documentation обновлена
