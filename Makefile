up:
	docker-compose up -d
stop:
	docker-compose stop
restart:
	docker-compose down
	docker-compose up -d
rebuild:
	docker-compose build --no-cache
test:
	docker-compose exec app pytest