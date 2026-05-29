Install Docker:

```bash
sudo apt install docker.io docker-compose -y
```

**Add your user to the Docker group** (so you don't need `sudo` every time):

```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Create a folder and navigate into it:**

```bash
mkdir moodle && cd moodle
```

Create the Docker Compose file:

```bash
vi docker-compose.yml
```

Then paste this inside:

```yaml
services:
  moodle:
    image: php:8.1-apache
    ports:
      - "8080:80"
    volumes:
      - ./moodle:/var/www/html
    depends_on:
      - mariadb

  mariadb:
    image: mariadb:10.6
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=moodle
      - MYSQL_USER=moodle
      - MYSQL_PASSWORD=moodlepassword
    volumes:
      - mariadb_data:/var/lib/mysql

volumes:
  mariadb_data:
```

> **Tip:** You can change `moodlepassword` and `rootpassword` to passwords of your choice — just make sure they match in both services.

Then run:

```bash
docker compose up -d
```