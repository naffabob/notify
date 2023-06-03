# Notify
Это сервис уведомлений, который осуществляет рассылку сообщений клиентам по определенным критериям.
Каждая рассылка определяется временем рассылки, телефонным кодом оператора и тегами, которые также задаются клиентам.
Сервис рассылки работает по API с внешней службой отправки смс-сообщений.

## Установка
Скачайте проект с gitlab:
```commandline
git clone https://gitlab.com/naffabob/notify.git
```
Перейдите в директорию проекта:
```commandline
cd notify 
```
После этого запустите все сервисы одной командой:
```commandline
docker-compose up -d --build
```
Остановить работу сервиса:
```commandline
docker-compose stop
```


## API
http://localhost:8000/ - api проекта

http://localhost:8000/tags/ - теги

http://localhost:8000/clients/ - клиенты

http://localhost:8000/mailings/ - рассылки

http://localhost:8000/mailings/stats/ - общая статистика по рассылкам

http://localhost:8000/api/mailings/<pk>/stats/ - детальная статистика по рассылке

Токен и url API внешнего сервиса отправки можно задать в [.env](.env)

Рассылка осуществляется с помощью ```Celery``` с брокером ```RabbitMQ```. Логика рассылки описана в [tasks.py](api/tasks.py)

## Выполненные дополнительные задания
3. подготовить docker-compose для запуска всех сервисов проекта одной командой
