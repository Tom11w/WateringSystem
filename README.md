# WateringSystem

[Watering system page](http://hub.local:5000)

## Todo

- Set Up nginx as reverse proxy for http and https

## Set Flask App to Start on Boot

Create a systemd service file:
`/etc/systemd/system/watering_system.service`

### Enable and start the service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable watering_system
sudo systemctl start watering_system
```

### Monitor logs live

```sh
journalctl -f -u watering_system.service
```

### Get Service Status

```sh
systemctl status watering_system.service
```

## Creating a virtual env

```sh
python3 -m venv .venv
```

### Activating virtual enviroment and install requirement

```sh
cd watereringsystem
source .venv/bin/activate
pip install -r requirements.txt
```
