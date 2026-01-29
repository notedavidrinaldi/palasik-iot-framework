# PALASIK Architecture

Dokumen ini menjelaskan arsitektur internal PALASIK
sebagai **Zero Trust Event Enforcement Framework**.

---

## 🧱 High-Level Architecture

PALASIK berada di **edge / gateway layer**
di antara perangkat IoT dan backend service.

```text
IoT Device
   │
   ▼
[ Adapter ]
   │
   ▼
[ Agent ]
   │
   ├── Trust Engine
   │
   ├── Policy Engine
   │
   └── Plugin System
   │
   ▼
Backend / Service

```
---
## 🧱 High-Level Architecture

PALASIK berada di **edge / gateway layer**
di antara perangkat IoT dan backend service.

```text
IoT Device
   │
   ▼
[ Adapter ]
   │
   ▼
[ Agent ]
   │
   ├── Trust Engine
   │
   ├── Policy Engine
   │
   └── Plugin System
   │
   ▼
Backend / Service
```

## 🔁 Event Processing Flow
```text
Event
 └─► Adapter
     └─► Agent
         ├─► TrustEngine.evaluate()
         ├─► PolicyEngine.decide()
         └─► Plugin.on_event()
```
## 🧩 Core Components

Agent

- Runtime utama PALASIK

- Mengelola lifecycle sistem

- Mengorkestrasi trust, policy, dan plugin

Adapter

- Menjembatani dunia luar (MQTT, HTTP, dll)

- Mengubah input menjadi event PALASIK

Trust Engine

- Menghitung skor kepercayaan (0.0 – 1.0)

- Tidak membuat keputusan akhir

Policy Engine

- Mengubah trust score menjadi keputusan eksplisit

- Contoh: ALLOW, DENY

Plugin System

- Menjalankan aksi berdasarkan keputusan
- Logging, forwarding, alert, dsb

## 🔐 Design Principles

- Zero Trust by Default

- Explicit Decision Making

- Single Direction Flow

- Separation of Concern
