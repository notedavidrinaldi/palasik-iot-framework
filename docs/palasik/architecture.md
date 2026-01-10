---
title: "System Architecture"
weight: 2
---

# Arsitektur Sistem PALASIK

## 1. Gambaran Umum
PALASIK menggunakan pendekatan **Edge-based Zero Trust Architecture**, di mana keputusan keamanan dilakukan sedekat mungkin dengan sumber data.

## 2. Layer Arsitektur

```mermaid
flowchart TB
    subgraph FIELD["Field Layer"]
        TAG[RFID / Sensor]
        DEV[IoT Device]
    end

    subgraph EDGE["Edge Layer (PALASIK)"]
        RPI[Raspberry Pi]
        TRUST[Trust Engine]
        POLICY[Policy Engine]
    end

    subgraph CLOUD["Cloud / Platform"]
        DB[(Database)]
        DASH[Dashboard]
    end

    TAG --> DEV
    DEV --> TRUST
    TRUST --> POLICY
    POLICY --> DB
    POLICY --> DASH
```

