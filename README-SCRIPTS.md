# TUNARA local service management

Start all services:

```bash
./start-tunara.sh
```

Check status:

```bash
./status-tunara.sh
```

Stop application services while keeping PostgreSQL running:

```bash
./stop-tunara.sh
```

Stop everything, including PostgreSQL:

```bash
./stop-tunara.sh --with-database
```

Restart application services:

```bash
./restart-tunara.sh
```

Logs are written to `logs/`. Generated audio and local Python environments remain excluded from Git.
