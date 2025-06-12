# 🚀 FileShipper

**FileShipper** is a web-based app for lightning-fast file transfers between devices on the same local network—no internet, no fuss. Just scan, send, and share.  

![FileShipper Logo](static/images/logo.png)

---

## 🌟 Features

- ⚡ **Seamless Local File Sharing** — Transfer files without internet
- 🔍 **Real-Time Device Discovery** — Auto-detect nearby devices
- 🔐 **User Authentication** — Safeguard transfers with login protection
- 📱 **QR Code Connectivity** — Connect by scanning a QR
- 🗂️ **File Management** — Upload, organize, and manage files
- 💻 **Cross-Platform Compatibility** — Use any modern browser
- 🌙 **Dark Mode UI** — Comfortable interface for night owls  

---

## 💻 System Requirements

- 🐍 Python 3.8 or newer  
- 🍃 MongoDB  
- 🌐 Modern browser (Chrome, Firefox, Safari, Edge)  
- 📶 Devices connected to the same local network  

---

## ⚙️ Installation Guide

### 📁 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FileShipper.git
cd FileShipper
```

### 🧪 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🍃 4. Start MongoDB

Make sure MongoDB is installed and running.  
🔗 [Download MongoDB](https://www.mongodb.com/try/download/community)

### 🛠️ 5. Run Migrations

```bash
python manage.py makemigrations filetransfer
python manage.py migrate
```

### 👤 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 🔧 7. Launch Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

App available at: `http://<your-ip-address>:8000`

---

## 📱 Usage Instructions

### 🔐 Login  
Use your superuser credentials to sign in.

### 📤 Upload Files  
Go to **Files** → Select and upload files.

### 🚀 Send Files  
1. Go to **Send**  
2. Pick files and select the target device  
3. Hit **Send**

### 📥 Receive Files  
1. Navigate to **Receive**  
2. Accept incoming transfers  
3. Download and enjoy

### 🔗 Connect Devices  
- All devices must be on the same WiFi 🌐  
- Use QR scanning for quick linking 🤳  

---

## 🌐 Network Configuration

- All devices must be on the same network  
- Port **8000** (HTTP) and **45678 UDP** (device discovery) must be open  

---

## 🧰 Troubleshooting

**❓ Can't Find Devices?**  
- Same network? ✔️  
- Port 8000 + UDP 45678 open? ✔️  

**🔌 Connection Issues?**  
- Check your IP in the **Help** section  
- Run the health check URL  
- Restart the server if needed  

**📁 File Transfer Failed?**  
- Check storage space 💾  
- Ensure file size is within Django limits  
- Stabilize your WiFi connection 🌐  

---

## 🛠️ Tech Stack

- Django 4.0.3  
- MongoDB via Djongo  
- Django REST Framework  
- JavaScript & browser APIs  

---

## 🤝 Contributing

1. 🍴 Fork the repo  
2. 🛠 Create a branch: `git checkout -b my-feature`  
3. ✅ Make your edits  
4. 📬 Submit a pull request  

---

## 📄 License

Licensed under the MIT License.  
See [LICENSE](LICENSE) for full details.

---

