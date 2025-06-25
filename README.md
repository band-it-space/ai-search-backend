## 📦 Опис репозиторію

Цей репозиторій містить серверну частину проєкту **AI Search Backend**, який реалізує пошук товарів за змістом у великій неструктурованій базі даних.

Основні компоненти:
- **FastAPI** — для створення високопродуктивного REST API;
- **Milvus** — векторна база даних для семантичного пошуку;
- **OpenAI Embeddings API** — для побудови векторних представлень запитів і товарів;
- **Docker** — для контейнеризації та простого розгортання на сервері;
- **Prometheus / MinIO** — додаткові сервіси для моніторингу та зберігання, за потреби.

Проєкт призначений для розгортання на AWS EC2 (Ubuntu 22.04) і включає повний стек для семантичного пошуку товарів у неструктурованих даних.

## ⚙️ Встановлення на сервері AWS (Ubuntu 22.04)

Цей розділ містить **повний набір команд**, які необхідно виконати вручну на чистому EC2-сервері з Ubuntu 22.04 для запуску проєкту.

### 1. Оновлення системи

```bash
sudo apt update && sudo apt upgrade -y
```

---

### 2. Встановлення Docker

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Перевірка встановлення:

```bash
docker --version
docker compose version
```

---

### 3. Дозвіл запуску Docker без `sudo` (необов'язково)

```bash
sudo usermod -aG docker $USER
```

Після цього **вийдіть з системи та увійдіть знову**, або перезапустіть SSH-сесію.

---

### 4. Встановлення Python і pip

```bash
sudo apt install -y python3 python3-pip
```

Перевірка версій:

```bash
python3 --version
pip3 --version
```

---

### 5. Клонування або завантаження проєкту

> Якщо репозиторій розміщено на GitHub:

```bash
git clone https://github.com/band-it-space/ai-search-backend.git
cd ai-search-backend
```

Або передайте архів через SCP/FileZilla та перейдіть у папку проєкту.

---

### 6. Створення `.env` файлу

Створіть файл `.env` у корені проєкту та додайте потрібні змінні середовища. Наприклад:

```env
MILVUS_HOST="milvus"
MILVUS_PORT="19530"
MILVUS_COLLECTION="goods_import"
EMBEDDING_DIM=3072
OPENAI_API_KEY=sk-proj-
ASSISTANT_ID=asst_
```

---

### 7. Перевірка структури перед запуском

У корені проєкту повинні бути файли:

-   `docker-compose.yml`
-   `Dockerfile`
-   `requirements.txt`
-   `milvus.yaml`
-   папка `app/`
-   файл `.env`

---

### 8. Запуск проєкту

```bash
docker compose up -d --build
```

Ця команда збере образ FastAPI, запустить всі контейнери у фоновому режимі.

---

### 9. Перевірка статусу контейнерів

```bash
docker compose ps
```

Усі сервіси повинні бути в статусі `Up (healthy)` або просто `Up`.

---

### 10. Доступ до інтерфейсів

-   **FastAPI Swagger**: [http://your-server-ip:8000/docs](http://your-server-ip:8000/docs)
-   **FastAPI Redoc**: [http://your-server-ip:8000/redoc](http://your-server-ip:8000/redoc)
-   **MinIO Web UI**: [http://your-server-ip:9001](http://your-server-ip:9001)
    Логін: `minioadmin`, Пароль: `minioadmin`
-   **Milvus Monitoring (Prometheus)**: [http://your-server-ip:9091/healthz](http://your-server-ip:9091/healthz)

---

### 11. Зупинка проєкту

```bash
docker compose down
```

Якщо потрібно видалити всі дані (етcd, minio, milvus):

```bash
docker compose down
rm -rf volumes/
```
