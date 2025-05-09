# ⚙️ 01. Local Setup: Python, Docker, HomeBrew, Git on macOS

In this section, we'll set up the local environment required to run the workshop labs. By the end, you'll have:
- Python binary / environment for generating synthetic log data
- Docker and Docker Compose for running ClickHouse, Grafana, and log shippers

---

## 📦 Prerequisites

### ✅ 1. (optional) Install Python 3 (via Homebrew)

If you don’t have Homebrew yet, install it first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

reference: [https://docs.brew.sh/Installation](https://docs.brew.sh/Installation)

```bash
# using brew to install python3
brew install python

# verify the installation
python3 --version
pip3 --version

```

### ✅ 2. Install Docker Desktop for Mac

Download and install Docker from the official site: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

```bash
# verify the installation
docker --version
docker compose version

```

### ✅ 3. (Optional) Install Docker Compose for Mac on older Desktop version

```bash
# install through brew
brew install docker-compose

# verify the installation
docker-compose --version
```

### ✅ 4. Install git

```bash
brew install git

# verify the installation
git --version
```

reference: [https://git-scm.com/downloads/mac](https://git-scm.com/downloads/mac)

### ✅ 5. Download the repository files

```bash
# download the repo through git
git clone https://github.com/quoeamaster/devOpsSG2025.git
cd devOpsSG2025

# the folder structure of devOpsSG2025
.
├── docker_files
│   ├── clickhouse-init-db.sql
│   └── docker-compose.yml
├── LICENSE
├── README.md
└── src
    ├── anomaly_detection.py
    └── log_generator.py
```

<div style="text-align:center; margin-top: 20px; font-size: 20px;">

🔧 [prev - home](../README.md) &nbsp;&nbsp;&nbsp; 🔍 [next - clickhouse](02-clickhouse.md)

</div>