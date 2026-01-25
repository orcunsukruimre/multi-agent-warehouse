# Multi-Agent Warehouse Decision Support System

## 🎯 Proje Hakkında

**Agentic AI** destekli akıllı depo yönetim sistemi. GPT-4 ile çalışan multi-agent yapısı sayesinde iş emirlerini operatörlere otomatik atar, yasal uyumluluğu kontrol eder ve gerektiğinde insan kararı alır.

### Temel Özellikler

- 🤖 **GPT-4 Entegrasyonu** - Akıllı özet ve analiz
- 📊 **Otomatik Atama** - Optimizasyon veya sezgisel algoritma
- ⚖️ **Yasal Uyumluluk** - İş Kanunu 4857 ve İSG kontrolü
- 👤 **Human-in-the-Loop** - Kritik kararlarda insan onayı
- 📈 **Görselleştirme** - Operatör başına metrik grafikleri
- 💾 **Excel Raporlama** - Detaylı atama listeleri

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
pip install -r requirements.txt
```

### 2. API Key Ayarla

`tools/llm_summarizer.py` dosyasında:
```python
API_KEY = "sk-proj-your-openai-api-key-here"
```

### 3. Çalıştır
```bash
python3 main.py
```

**[1]** seçin → Agentic AI

---

## 📊 Sistem Akışı
```
1. Giriş Özeti (LLM)
   ↓
2. İş Emri Ataması (Optimizer)
   ↓
3. Uyumluluk Kontrolü
   ↓
4. Uyumsuz mu? → Human-in-the-Loop
   ├─ Ek Kaynak Al
   └─ İş Emri Azalt
   ↓
5. Final Atama
   ↓
6. Sonuç Özeti (LLM)
   ↓
7. Excel + Grafikler
```

---

## 🤖 Agent'lar (Backend)

### Inventory Agent
- İş yükü analizi
- Toplam iş emri, ürün, hacim

### Workforce Agent
- İşgücü durumu
- Aktif operatör, kapasite

### Compliance Agent
- Yasal uyumluluk
- İş Kanunu 4857
- İSG Yönetmeliği

### Assignment Agent (Orchestrator)
- Tüm agentları koordine eder
- LLM ile özetler
- Human-in-the-Loop yönetir

---

## 📋 Çıktılar

### Excel Raporu
- **Atama Listesi**: Operatör - İş Emri eşleştirmeleri
- **Operatör Özeti**: Tur, ürün, hacim metrikleri
- **Genel Özet**: Toplam istatistikler
- **LLM Özetleri**: Giriş ve sonuç metinleri

### Grafikler
- Operatör başına tur sayısı
- Operatör başına ürün adedi
- Operatör başına hacim
- İş yükü dengesi

---

## ⚖️ Yasal Uyumluluk

- ✅ İş Kanunu 4857 (Max 45 saat/hafta)
- ✅ Fazla mesai limitleri (Günlük 3, haftalık 11 saat)
- ✅ İSG Yönetmeliği
- ✅ KVKK (Veri saklama)

---

## 📂 Proje Yapısı
```
multi_agent_warehouse/
├── agents/
│   ├── inventory_agent.py      # İş yükü analizi
│   ├── workforce_agent.py      # İşgücü analizi
│   ├── compliance_agent.py     # Yasal uyumluluk
│   └── assignment_agent.py     # Ana orchestrator
├── data/
│   └── warehouse_data.py       # Depo verileri
├── tools/
│   ├── optimizer.py            # Atama algoritmaları
│   ├── llm_summarizer.py       # GPT-4 entegrasyonu
│   └── visualizer.py           # Grafik oluşturma
├── config/
│   └── regulations.yaml        # İş Kanunu kuralları
├── outputs/                    # Excel + Grafikler
├── main.py                     # Ana uygulama
└── README.md
```

---

## 🔑 Önemli Notlar

### API Key Güvenliği
- `.env` dosyasını **asla** GitHub'a yüklemeyin
- `.gitignore` içinde tanımlıdır

### Human-in-the-Loop
- Uyumsuzluk tespit edilince devreye girer
- 2 seçenek: Ek kaynak al / İş emri azalt
- Kararlar audit trail'e kaydedilir

---

## 📚 Referanslar

- Dr. Şükrü İmre, "LLM Agentlar Depoda Nasıl Kullanılabilir?", Medium, 2024
- İş Kanunu 4857
- İSG Yönetmeliği, 2012
- KVKK, Kanun No. 6698

---

## 🛠️ Geliştirme
```bash
# Test
python3 -m pytest

# Linting
flake8 agents/ tools/
```

---

**Lisans:** MIT  
**Yazar:** [İsminiz]  
**Tarih:** Ocak 2026