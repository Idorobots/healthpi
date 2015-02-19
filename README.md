Basic (not only) Rasberry Pi 2 health monitoring server.

```
$ src/health.py --port PORT &
$ src/check.py http://localhost:PORT
```

Or run it as a Unix daemon:

```
$ src/health.py --port PORT --daemon start
$ src/check.py http://localhost:PORT
```

Start it using SSL:

```
$ src/health.py --ssl-cert certfile.pem --port PORT --daemon start
$ src/check.py https://localhost:PORT
```
