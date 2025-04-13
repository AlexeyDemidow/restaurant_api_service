## API-сервис бронирования столиков в ресторане

---
REST API для бронирования столиков в ресторане.<br>
Сервис позволяет создавать, просматривать и удалять брони, а также управлять столиками и временными слотами.

### Установка и запуск

- Клонируем репозиторий `git clone https://github.com/AlexeyDemidow/restaurant_api_service.git`
- Устанавливаем зависимости `pip install -r requirements.txt`
- Создаем `.env` файл и заполняем его по образцу `.env.example`
- Создаем docker-образ `docker build -t docker_image_name .`
- Запускаем контейнеры `docker compose up`
- Переходим по ссылке http://localhost/docs и попадаем в документацию проекта

