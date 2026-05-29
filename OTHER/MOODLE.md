Install Docker:

```bash
sudo apt install docker.io docker-compose -y
```

**Add your user to the Docker group** (so you don't need `sudo` every time):

```bash
sudo usermod -aG docker $USER
newgrp docker
```

