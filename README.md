# PALASIK  
**Pengaman Layer Edge Sistem IoT Kritis**  
*A Zero Trust IoT Gateway Framework based on Raspberry Pi*

---

## 📌 Abstrak
PALASIK adalah sebuah framework penelitian berbasis **Raspberry Pi**
yang dirancang untuk menerapkan konsep **Zero Trust Security Architecture**
pada sistem **Internet of Things (IoT)** di level **edge gateway**.

Framework ini berfokus pada evaluasi kepercayaan perangkat (device trust),
pengendalian akses berbasis kebijakan, serta pengamanan komunikasi IoT
yang bersifat ringan, modular, dan mudah direproduksi untuk kebutuhan
penelitian akademik maupun pengembangan lanjutan.

---

## 🎯 Latar Belakang
Pertumbuhan pesat sistem IoT menghadirkan tantangan keamanan yang signifikan,
khususnya pada perangkat dengan sumber daya terbatas.
Pendekatan keamanan tradisional yang bersifat perimeter-based
tidak lagi memadai untuk menghadapi ancaman seperti:
- Rogue device
- Spoofing identitas perangkat
- Unauthorized access di edge gateway

PALASIK mengadopsi prinsip **“Never Trust, Always Verify”**
dengan menempatkan mekanisme trust evaluation langsung di gateway IoT.

---

## 🧠 Kontribusi Utama
Kontribusi utama dari PALASIK meliputi:

1. **Trust Engine berbasis Edge**
   - Evaluasi kepercayaan perangkat secara dinamis
   - Skoring berdasarkan identitas, perilaku, dan konteks

2. **Policy Engine modular**
   - Pengambilan keputusan berbasis aturan (policy-driven)
   - Mendukung skema allow / deny / quarantine

3. **Framework eksperimental terbuka**
   - Mudah direplikasi untuk penelitian kampus
   - Mendukung kolaborasi lintas disiplin

4. **Dokumentasi terstruktur**
   - Arsitektur
   - Metodologi
   - Roadmap penelitian

---

## 🏗️ Arsitektur Sistem (Ringkas)

[ IoT Device ]
│
▼
[ Trust Engine ] ──► [ Policy Engine ] ──► [ IoT Service ]
▲
│
[ Context & Behavior ]


PALASIK berperan sebagai **security layer** di antara perangkat IoT
dan layanan backend.

---

## 🧪 Platform & Teknologi
- **Hardware**
  - Raspberry Pi 3B / 3B+
  - RFID Reader (contoh: Invengo XC-RF850)
- **Software**
  - Node-RED
  - Python
  - MQTT / REST API
- **Security Concept**
  - Zero Trust Architecture
  - Edge Computing
  - Policy-based Access Control

---

## 📚 Dokumentasi Lengkap
Dokumentasi teknis dan pengembangan tersedia di:

👉 https://notedavidrinaldi.github.io/palasik/

Struktur dokumentasi:
- Overview
- Architecture
- Trust Engine
- Policy Engine
- Installation
- Roadmap
- Contributors
- Citation

---

## 🧑‍🔬 Konteks Penelitian
Framework ini ditujukan untuk:
- Penelitian IoT Security
- Edge Computing
- Smart Infrastructure
- Sistem Tertanam & Jaringan

PALASIK **tidak terbatas pada satu use-case** dan dapat dikembangkan
untuk:
- Smart Campus
- Smart Port
- Smart Healthcare
- Industrial IoT

---

## 🤝 Kontribusi & Kolaborasi
Kontribusi sangat terbuka untuk:
- Peneliti
- Mahasiswa
- Praktisi IoT & Security

Silakan baca panduan kontribusi di:
📄 `CONTRIBUTING.md`

---

## 📄 Sitasi
Jika menggunakan PALASIK dalam publikasi ilmiah, silakan rujuk:
📑 `docs/palasik/citation.md`

---

## 📜 Lisensi
Proyek ini dirilis di bawah **MIT License**,
memungkinkan penggunaan untuk riset dan pengembangan lanjutan.

---

## 👤 Peneliti Utama
**David Rinaldi**  
IoT Security & Edge Computing Researcher  
📧 GitHub: https://github.com/notedavidrinaldi/palasik-iot-framework

