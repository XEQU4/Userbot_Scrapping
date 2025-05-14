# 📬 Userbot_Scrapping

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Telethon](https://img.shields.io/badge/Telethon-async-success)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![uv](https://img.shields.io/badge/Tool-uv-orange)

---

## 📋 Description

**Userbot_Scrapping** is an automated solution for **mass mailing** in Telegram groups combined with **survey data collection** via an associated **[Chatbot_Analyzing](https://github.com/XEQU4/Chatbot_Analyzing)**.

It parses public chats, sends vacancy offers with a link to the survey bot, and collects user feedback automatically into a centralized PostgreSQL database.

---

## 🛠️ Technologies Used

* **Python** — backend logic
* **Telethon** — asynchronous Telegram client
* **PostgreSQL** — database management
* **uv** — fast dependency manager
* **python-socks\[asyncio]** — proxy support for scalable mailing

---

## ⚙️ Functionality

* **Session Management**:

  * Preload sessions into the database or create them dynamically.
  * Additional script for session creation and verification.

* **Automated Chat Parsing**:

  * Parses chats every **45–75 minutes**.
  * Configurable list of chats stored in the database.

* **Controlled Messaging**:

  * Each account sends **one message per cycle**.
  * After **5 mailing cycles**, accounts **sleep for 12–24 hours**.

* **Integration with [Chatbot_Analyzing](https://github.com/XEQU4/Chatbot_Analyzing)**:

  * Link to the survey is included in each message.
  * Survey results are sent directly to managers along with the respondent's profile link.

* **Flexible Message Editing**:

  * Both the **message text** and **attached image** for mailing can be easily updated in the `/our_message/` directory.

* **Database-Driven Control**:

  * Manage chats, sessions, and parameters dynamically via the database — no need to stop the bot.

---

## 📄 Environment Variables

Example `.env` settings:

```dotenv
# PostgreSQL connection string
DSN="postgres://user:password@localhost:5432/database"
```

---

## 🚀 Installation and Launch

> ⚡ This project uses **uv** for fast and reliable environment management.

### 1. Clone the repository:

```bash
   git clone https://github.com/XEQU4/SpammerBot.git
   cd SpammerBot
```

### 2. Install dependencies:

```bash
   pip install -U uv
   uv venv
   uv sync
```

### 3. Set up the `.env` file:

```bash
   cp .env.example .env
   # Then edit your credentials inside
```

## 4. Prepare session and proxy files:

Make sure to correctly fill in the session and proxy data inside:
```
   sessions/sessions_datas.txt
   sessions/proxies_datas.txt
```

### 5. Run the bot:

```bash
   uv run app/main.py
```

Or launch a session creation tool:

```bash
   uv run sessions/create_sessions.py
```

---

## 📷 Screenshots

![](assets/mailing.png)
![](assets/mailing_console.png)
![](assets/project_structure.png)

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

---

**Author:** [XEQU](https://github.com/XEQU4)
