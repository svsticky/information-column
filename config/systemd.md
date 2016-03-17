# Running zuild as a systemd service

1. Copy `zuild.service` to `/etc/systemd/system` AND ensure all paths are correct (user is currently `admin` but this might change)
2. `sudo systemctl daemon-reload`
3. `sudo systemctl start zuild`
4. `sudo systemctl enable zuild`

`zuild` will now start on boot and update on the interval specified in config, inspect output using `journalctl -u zuild`.
