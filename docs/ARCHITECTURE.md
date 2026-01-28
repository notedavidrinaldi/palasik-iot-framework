# PALASIK Architecture

Dokumen ini menjelaskan arsitektur PALASIK sebagai framework IoT Gateway
berbasis Zero Trust.

---

## Komponen Utama

1. **Agent**
   Runtime utama yang mengatur lifecycle sistem.

2. **Adapter**
   Jembatan antara dunia luar (MQTT, HTTP) dan event internal PALASIK.

3. **Trust Engine**
   Menghitung skor kepercayaan event.

4. **Policy Engine**
   Menentukan keputusan keamanan (ALLOW / DENY).

5. **Plugin**
   Menangani event berdasarkan keputusan policy.

---

## Alur Event

```mermaid
sequenceDiagram
    participant Device
    participant Broker
    participant Adapter
    participant Agent
    participant Trust
    participant Policy
    participant Plugin

    Device->>Broker: publish data
    Broker->>Adapter: message
    Adapter->>Agent: emit_event
    Agent->>Trust: evaluate
    Trust->>Agent: trust_score
    Agent->>Policy: decide
    Policy->>Agent: ALLOW / DENY
    Agent->>Plugin: on_event
```
Prinsip Desain

-Zero Trust by Default

-Separation of Concern

-Extensible via Plugin

-Single Direction Data Flow



