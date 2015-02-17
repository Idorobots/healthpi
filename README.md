Basic (not only) Rasberry Pi 2 health monitoring server.

```
$ src/health.py PORT &
$ src/check.py localhost:PORT
```

Or run it as a Unix daemon:

```
$ src/health.py --daemon start
$ src/check.py localhost:8000
```
