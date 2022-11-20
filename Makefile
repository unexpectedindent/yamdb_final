build:
	sudo docker-compose -f infra/docker-compose.yaml up -d --build
remove:
	sudo docker image rm infra_web
stop:
	sudo docker stop infra_web_1 infra_nginx_1 infra_db_1
logs-web:
	sudo docker container logs infra_web_1
logs-nginx:
	sudo docker container logs infra_nginx_1
enter-web:
	sudo docker exec -it infra_web_1 bash
collectstatic:
    sudo docker-compose exec web python manage.py collectstatic --no-input
migrate:
    sudo docker-compose exec web python manage.py migrate
create-su:
    sudo docker-compose exec web python manage.py createsuperuser
copy:
    scp infra/docker-compose.yaml up_percase@123.123.123.123:/directory
