# Smart Attendance System using ESP32-Cam and Flask

> A modern IoT-based **Smart Attendance System** that captures images using an **ESP32-Cam**, detects faces using a **Flask backend**, and maintains real-time attendance records viewable through a sleek web dashboard.

---

##  Project Overview

This project transforms a simple ESP32-Cam into an intelligent attendance monitoring system.  
Whenever motion is detected, the ESP32-Cam captures an image and sends it to a Flask web server, where face detection and attendance logging occur automatically.
It’s lightweight, runs on affordable hardware, and brings together **IoT, Computer Vision, and Web Technologies** to demonstrate a real-world smart automation solution.

---

##  Key Features

- **ESP32-Cam Integration** – Sends captured images to the server.    
- **Flask Web Server** – Handles image uploads, processes detection, and maintains attendance records.  
- **Web Dashboard** – Clean HTML interface to view real-time attendance logs.  
- **Local or Network Deployment** – Works on local Wi-Fi or can be hosted on a remote server.  
- **Simple and Reliable Architecture** – Uses standard REST endpoints for ESP-to-Flask communication.  

---

## 🖼️ System Architecture



```
 ┌────────────────────┐
 │   ESP32-Cam        │
 │  (captures image)  │
 └─────────┬──────────┘
           │
 HTTP POST │ image + metadata
           ▼
 ┌────────────────────┐
 │   Flask Server     │
 │  (detects + logs)  │
 └─────────┬──────────┘
           │
           ▼
 ┌────────────────────┐
 │  Web Dashboard     │
 │ (view attendance)  │
 └────────────────────┘
```



---

## 🧩 Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Hardware** | ESP32-Cam Module |
| **Backend** | Python Flask |
| **Frontend** | HTML5, CSS3, Bootstrap |
| **Database** | CSV / SQLite (Configurable) |
| **Networking** | Wi-Fi communication using HTTP |

---

## ⚙️ Setup Instructions

### 1️⃣ ESP32-Cam Firmware Upload
1. Open **Arduino IDE**.  
2. Load the example **File → Examples → ESP32 → Camera → CameraWebServer**.  
3. Replace Wi-Fi credentials and server IP with your Flask server IP.  
4. Comment out extra `startCameraServer()` definitions (if present).  
5. Upload to your ESP32-Cam board.

### 2️⃣ Flask Server Setup
```bash
git clone https://github.com/surya070/esp32-attendance-system.git
cd esp32-attendance-system
pip install -r requirements.txt
cd backend
python app.py
````

Then visit `http://localhost:5000` or your local IP on another device in the same network.

---


<img width="2497" height="1049" alt="image" src="https://github.com/user-attachments/assets/76071fa5-d02f-4c07-aea1-5f6b91a75f30" />

<img width="2490" height="1022" alt="image" src="https://github.com/user-attachments/assets/ca75c1db-f007-4c86-8465-7f491996bdd0" />


