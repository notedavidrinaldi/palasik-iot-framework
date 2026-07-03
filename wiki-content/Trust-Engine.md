# Trust Engine

Trust Engine PALASIK menilai apakah event layak dipercaya menggunakan pendekatan kontekstual:

- reputasi/tipe device
- pola pengiriman event
- metadata event
- faktor keandalan waktu/behavior
- indikator anomali

### Output

Trust Engine memberi **trust score** numerik (mis. 0.0–1.0) dan/atau sinyal tambahan yang dipakai Policy Engine.

### Peran di pipeline

Trust Engine **bukan** keputusan final. Ia hanya menilai risiko/kepercayaan untuk diputuskan lebih lanjut oleh Policy Engine.

### Praktik operasional

- Untuk perubahan perilaku trust, lakukan pengujian lewat `simulate` terlebih dulu.
- Pantau metrik runtime (`status`) setelah update supaya tidak terjadi anomali deny rate.
