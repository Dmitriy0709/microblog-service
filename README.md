# Microblog Service

Бэкенд корпоративного сервиса микроблогов + статический фронтенд.

## Запуск (Docker Compose)
```bash
git clone <ваш-репозиторий>
cd microblog-service
# распакуйте фронтенд файлы в ./frontend
cp backend/.env.example backend/.env  # опционально
docker-compose up -d
