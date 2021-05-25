up:
	docker-compose up -d
stop:
	docker-compose stop
restart:
	docker-compose down
	docker-compose up -d
rebuild:
	docker-compose build --no-cache
ps:
	docker-compose ps
app:
	docker-compose exec app bash
