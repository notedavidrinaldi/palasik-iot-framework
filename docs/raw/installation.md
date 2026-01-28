---
title: "Installation Guide"
weight: 5
---

# Installation Guide  
## PALASIK on Raspberry Pi 3B  
*Edge-based IoT Trust & Policy Framework*

---

## 1. Tujuan Instalasi

Dokumen ini menjelaskan tahapan instalasi **PALASIK Framework**
pada **Raspberry Pi 3B** sebagai **IoT Security Gateway**.

Setelah instalasi selesai, Raspberry Pi akan mampu:
- Menerima data perangkat IoT
- Mengevaluasi kepercayaan perangkat (Trust Engine)
- Menentukan kebijakan keamanan (Policy Engine)
- Melakukan enforcement secara lokal (edge)

---

## 2. Spesifikasi Minimum

### 2.1 Perangkat Keras

| Komponen | Spesifikasi |
|--------|------------|
| Board | Raspberry Pi 3 Model B |
| CPU | Quad Core ARM Cortex-A53 |
| RAM | 1 GB |
| Storage | MicroSD ≥ 16 GB (Class 10) |
| Network | Ethernet / Wi-Fi |
| Power | 5V 2.5A |

---

### 2.2 Perangkat Lunak

| Komponen | Versi |
|-------|------|
| OS | Raspberry Pi OS Lite (64-bit) |
| Node.js | ≥ v18 LTS |
| Node-RED | ≥ v3.x |
| Python | ≥ 3.9 |
| Git | Latest |
| Firewall | iptables / nftables |

---

## 3. Instalasi Sistem Operasi

### 3.1 Download Raspberry Pi OS

Gunakan **Raspberry Pi OS Lite (64-bit)**  
Direkomendasikan untuk edge security karena:
- Ringan
- Stabil
- Dukungan jangka panjang

---

### 3.2 Flash OS ke MicroSD

Gunakan **Raspberry Pi Imager**:

1. Pilih OS → *Raspberry Pi OS Lite (64-bit)*
2. Pilih Storage → MicroSD
3. Klik **Advanced Settings**
   - Enable SSH
   - Set hostname (contoh: `palasik-gateway`)
   - Set username & password
4. Flash

---

### 3.3 Boot Pertama

1. Masukkan MicroSD ke Raspberry Pi
2. Sambungkan LAN / Wi-Fi
3. Nyalakan Raspberry Pi
4. Login via SSH

```bash
ssh pi@palasik-gateway.local
```

## 4. Konfigurasi Dasar Sistem
### 4.1 Update Sistem
```bash 
sudo apt update && sudo apt upgrade -y
```

###4.2 Set Timezone
```bash
sudo raspi-config
```

Pilih:
```bash
Localisation Options → Timezone → Asia → Jakarta
```

### 4.3 Aktifkan Firewall Dasar
```bash
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

##5. Instalasi Dependensi Inti
###5.1 Install Git
```bash
sudo apt install git -y
```
### 5.2 Install Node.js (LTS)
```bash 
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

Cek versi:
```bash
node -v
npm -v
```

### 5.3 Install Node-RED
```bash
sudo npm install -g --unsafe-perm node-red
```

Aktifkan auto-start:
```bash
sudo systemctl enable nodered.service
```

Jalankan:
```bash
node-red
```

Akses via browser:
```bash
http://<IP_RPI>:1880
```

##6. Struktur Direktori PALASIK

Buat direktori utama project:
```bash
mkdir -p ~/palasik
cd ~/palasik
```

Struktur direkomendasikan:
``` bash 
palasik/
├── trust-engine/
│   ├── trust_score.py
│   └── rules.json
├── policy-engine/
│   ├── policy.yaml
│   └── enforcer.sh
├── logs/
├── node-red/
│   └── flows.json
└── docs/
```

##7. Instalasi Trust Engine
###7.1 Trust Engine (Python)
```bash
sudo apt install python3 python3-pip -y
pip3 install numpy pandas
```

Contoh file trust_score.py:
```bash
def calculate_trust(device):
    score = 1.0
    if device["failed_auth"] > 3:
        score -= 0.3
    if device["anomaly"]:
        score -= 0.4
    return max(score, 0)
```

## 8. Instalasi Policy Engine
### 8.1 Policy Definition

Contoh policy.yaml:
```bash
policies:
  - name: allow_trusted
    condition: trust_score >= 0.8
    action: ALLOW

  - name: restrict_limited
    condition: trust_score >= 0.5
    action: RESTRICT

  - name: quarantine_untrusted
    condition: trust_score < 0.5
    action: QUARANTINE
```

###8.2 Enforcement Script

Contoh enforcer.sh:
```bash
#!/bin/bash
DEVICE_IP=$1
iptables -A INPUT -s $DEVICE_IP -j DROP
```

Aktifkan:
```bash
chmod +x enforcer.sh
```

##9. Integrasi dengan Node-RED

Node-RED berperan sebagai:

Data collector

Trust evaluator trigger

Policy executor
```mermaid
flowchart LR
    DEVICE --> NR[Node-RED]
    NR --> TE[Trust Engine]
    TE --> PE[Policy Engine]
    PE --> ACTION[Firewall / MQTT / API]
```
##10. Validasi Instalasi
###10.1 Checklist

 Node-RED berjalan

 Trust Engine menghasilkan trust score

 Policy Engine membaca policy.yaml

 Enforcement berhasil dijalankan

 Log tersimpan

###11. Mode Eksperimen

Gunakan mode ini untuk riset:

Simulasikan device trust score

Ubah policy threshold

Bandingkan dampak enforcement

Contoh eksperimen:

Pengaruh perubahan trust threshold terhadap false positive isolation.

##12. Troubleshooting
           Masalah                         	Solusi
Node-RED tidak bisa start	Cek journalctl -u nodered
Firewall memblokir SSH	        Reset UFW via recovery
CPU      tinggi	               Gunakan OS Lite & disable GUI

## 13. Penutup

Dengan instalasi ini, Raspberry Pi 3B telah berfungsi sebagai:

Edge Trust & Policy Gateway untuk IoT Security Research

Dokumen ini dapat direproduksi untuk:

Skripsi

Tesis

Paper IEEE

Project open-source kolaboratif
