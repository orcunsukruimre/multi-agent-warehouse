# 🤖 Multi-Agent Warehouse Decision Support System

**Ajantik AI** ile çalışan, GPT-4 destekli akıllı depo yönetim sistemi. İş emirlerini operatörlere otomatik atar, yasal uyumluluğu kontrol eder ve **Human-in-the-Loop** ile kritik kararlar alır.

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red)](https://streamlit.io/)
[![GPT-4](https://img.shields.io/badge/GPT--4-OpenAI-green)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📖 Medium Yazısı

Bu proje hakkında detaylı yazı:

**📝 [Ajan Temelli Yapay Zekâ ile Depo Yönetimi: İnsanı Döngüde Tutan Gerçek Bir Uygulama](https://sukruimre.medium.com/ajan-temelli-yapay-zekâ-ile-depo-yönetimi-i̇nsanı-döngüde-tutan-gerçek-bir-uygulama-cc1f677e2445?postPublishedType=initial)**

*Sistem tasarımı, 4 uzman ajanın nasıl çalıştığı, human-in-the-loop yaklaşımı ve gerçek dünya uygulamaları hakkında detaylı açıklama.*

---

## 🎯 Özellikler

### 🤖 Agentic AI
- **4 Uzman Ajan** - Her biri kendi alanında otonom çalışır
- **GPT-4 Entegrasyonu** - Akıllı giriş ve sonuç özetleri
- **Otomatik Atama** - Optimizasyon → Sezgisel fallback
- **Human-in-the-Loop** - Kritik kararlarda insan onayı

### ⚖️ Yasal Uyumluluk
- **Günlük Limit** - Maksimum 10 tur/operatör (435 dakika / 7.25 saat)
- **Otomatik Kontrol** - İş Kanunu uyumluluğu (basitleştirilmiş)
- **Risk Analizi** - KRİTİK/YÜKSEK/ORTA/DÜŞÜK seviyeleri

### 📊 Görselleştirme
- **Dinamik Dashboard** - Gerçek zamanlı progress bar'lar
- **4 Grafik** - Tur, ürün, hacim, denge analizi
- **Excel Export** - Atama listelerini indir

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Gereksinimler
```bash
pip install -r requirements.txt
```

### 2️⃣ OpenAI API Key Ayarla

**Yöntem 1: Environment Variable (Önerilen)**
```bash
export OPENAI_API_KEY="sk-proj-YOUR-API-KEY-HERE"
```

**Yöntem 2: .env Dosyası**

`.env` dosyası oluşturun:
```
OPENAI_API_KEY=sk-proj-YOUR-API-KEY-HERE
```

⚠️ **Önemli:** API key'inizi asla GitHub'a yüklemeyin! `.gitignore` dosyası `.env`'yi otomatik dışlar.

### 3️⃣ Uygulamayı Çalıştır

**Streamlit Web Arayüzü (Önerilen):**
```bash
streamlit run app.py
```

Tarayıcıda otomatik açılır: `http://localhost:8501`

**Terminal Arayüzü:**
```bash
python3 main.py
```

---

## 📋 Kullanım Akışı

### 1️⃣ Otomatik Özet
Sistem açıldığında GPT-4 mevcut durumu analiz eder:
- İş emri sayısı (74 tur)
- Toplam ürün ve hacim (5,177 adet, 14,491 desi)
- Operatör durumu (6 aktif, 2 izinli/hasta)

### 2️⃣ Atama Başlat
Tek tıkla otomatik atama:
- Optimizasyon algoritması (PuLP)
- Başarısız olursa sezgisel yöntem
- Dinamik progress bar'lar

### 3️⃣ Uyumluluk Kontrolü
Otomatik yasal uyumluluk denetimi:
- 11+ tur = KRİTİK İHLAL
- 0-10 tur = UYUMLU

### 4️⃣ Karar Noktası (Human-in-the-Loop)
Uyumsuzluk varsa sistem 2 seçenek sunar:
- **A) +1 Ek Operatör Al** - Tüm işler tamamlanır (~500-700 TL)
- **B) İş Emri Azalt** - Maliyet tasarrufu (0 TL)

### 5️⃣ Sonuçlar
- LLM final özeti (GPT-4)
- Operatör başına tablo
- 4 detaylı grafik
- Excel indirme

---

## 🏗️ Proje Yapısı
```
multi_agent_warehouse/
├── app.py                      # Streamlit web arayüzü
├── main.py                     # Terminal arayüzü
├── agents/
│   ├── assignment_agent.py     # Ana orchestrator
│   ├── inventory_agent.py      # İş yükü analizi
│   ├── workforce_agent.py      # İşgücü analizi
│   └── compliance_agent.py     # Yasal uyumluluk
├── tools/
│   ├── optimizer.py            # Atama algoritmaları
│   ├── llm_summarizer.py       # GPT-4 entegrasyonu
│   └── visualizer.py           # Grafik oluşturma
├── data/
│   └── warehouse_data.py       # Veri kaynağı
├── config/
│   └── regulations.yaml        # Uyumluluk kuralları
├── outputs/                    # Excel ve grafikler
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler
- **Python 3.9+**
- **Streamlit** - Web arayüzü
- **GPT-4** - OpenAI API
- **PuLP** - Matematiksel optimizasyon
- **Pandas** - Veri işleme
- **Matplotlib** - Görselleştirme

### Atama Algoritması

**Optimizasyon (PuLP):**
```python
# Amaç: İş yükü dengesini maksimize et
maximize: M1*y + M2*z + Σ(ürün_adedi)

# Kısıtlar:
1. Her iş bir kişiye: Σ(x[i,j]) = 1
2. Tur dengesi: tur[i] ≥ ortalama * z
3. Desi dengesi: desi[i] ≥ ortalama * y
4. Denge oranı: z ≤ 0.53 * y
```

**Sezgisel (Fallback):**
```python
# Round-robin dengeli dağıtım
1. İş emirlerini hacim/adet oranına göre sırala
2. Operatörlere sırayla dağıt
```

### Uyumluluk Kuralları
```yaml
working_hours:
  daily_minutes: 435        # 7.25 saat
  minutes_per_tour: 40      # Tur süresi
  max_tours_per_day: 10     # Limit

violations:
  tour_limit_exceeded:
    threshold: 11           # İhlal
    risk_level: "KRİTİK"
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Normal Kapasite (6 Aktif Operatör)
```
✅ 74 iş emri → 74 atandı
✅ Uyumluluk: UYUMLU
✅ Risk: DÜŞÜK
```

### Senaryo 2: Kısıtlı Kapasite (4 Aktif Operatör)
```
⚠️  74 iş emri → İlk atama uyumsuz
👤 Karar: A) +1 Operatör
✅ 74 iş emri → 74 atandı
✅ Uyumluluk: UYUMLU
```

### Senaryo 3: İş Emri Azaltma
```
⚠️  74 iş emri → İlk atama uyumsuz
👤 Karar: B) İş Emri Azalt
✅ 60 iş emri → 60 atandı
⚠️  14 iş emri ertelendi
```

---

## 📐 Sistem Varsayımları

### Operasyonel Parametreler
- **Bir tur süresi:** 40 dakika
- **Günlük çalışma:** 435 dakika (7.25 saat)
- **Maksimum tur/operatör:** 10 tur/gün

### Test Verisi
- **Toplam iş emri:** 74 tur
- **Toplam ürün:** 5,177 adet
- **Toplam hacim:** 14,491 desi
- **Operatör:** 8 toplam (6 aktif, 2 izinli/hasta)

---

## ⚠️ Bilinen Sorunlar

### Mac M1/M2/M3/M4 Optimizasyon
PuLP optimizasyonu bazı Apple Silicon sistemlerde çalışmayabilir. Sistem otomatik olarak sezgisel algoritmaya geçer (garantili çözüm).

**Çözüm:** GLPK solver kurabilirsiniz:
```bash
brew install glpk
```

---

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📝 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👤 Yazar

**Dr. Şükrü İmre**

- 📧 Email: orcunimre@hotmail.com
- 💼 LinkedIn: https://tr.linkedin.com/in/şükrü-imre-phd-8b779141
- 📝 Medium: https://medium.com/@sukruimre

---

## 🙏 Teşekkürler

- OpenAI GPT-4
- Streamlit Community
- PuLP Optimization Library
- Python Community


---

**⭐ Beğendiyseniz yıldız vermeyi unutmayın!**

---

*Bu proje bir araştırma çalışmasıdır. Gerçek bir depo uygulaması değil, ajantik AI'nın nasıl kullanılabileceğini gösteren bir prototiptir.*