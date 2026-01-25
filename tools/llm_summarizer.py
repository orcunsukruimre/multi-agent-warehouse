"""
LLM ile Özet Üretimi (GPT-4)
"""
from openai import OpenAI
import pandas as pd
from typing import Dict, Any

# ============================================
# BURAYA API KEY'İNİZİ YAZIN
# ============================================
import os

# API key'i environment variable'dan al
API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# ============================================


class LLMSummarizer:
    """GPT-4 ile özet metin üretimi"""
    def __init__(self):
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-proj-xxx"):
            raise ValueError(
                "❌ HATA: API key tanımlanmamış!\n"
                "Lütfen tools/llm_summarizer.py dosyasının başındaki\n"
                "OPENAI_API_KEY = '...' satırına gerçek API key'inizi yazın."
            )
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4"
    
    def summarize_workforce(self, 
                           total_orders: int,
                           total_items: int, 
                           total_volume: int,
                           total_operators: int,
                           active_operators: int,
                           on_leave: int,
                           sick_leave: int) -> str:
        """İşgücü analizi özetini üretir"""
        
        prompt = f"""
Sen bir depo yönetimi uzmanısın. Aşağıdaki bilgileri analiz edip, depo yöneticisine 
2-3 cümlelik kısa ve profesyonel bir özet sun.

**Durum:**
- Toplam İş Emri: {total_orders} adet
- Toplanacak Ürün: {total_items} adet
- Toplam Hacim: {total_volume} desi
- Toplam Operatör: {total_operators} kişi
- Aktif Operatör: {active_operators} kişi
- İzinli: {on_leave} kişi
- Hastalık İzni: {sick_leave} kişi

Sadece özet metni döndür, başka bir şey ekleme.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Sen profesyonel bir depo yönetimi asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    def summarize_assignment(self,
                            assignments: pd.DataFrame,
                            method: str,
                            total_orders: int,
                            assigned_orders: int) -> str:
        """Atama sonuçlarını özetler"""
        
        # Operatör başına özet
        summary = assignments.groupby('Operator').agg({
            'IsEmri': 'count',
            'UrunDesi': 'sum',
            'UrunAdedi': 'sum'
        }).rename(columns={'IsEmri': 'TurSayisi'})
        
        summary_text = summary.to_string()
        
        method_name = "optimizasyon" if method == "OPTIMIZATION" else "sezgisel algoritma"
        
        prompt = f"""
Sen bir depo yönetimi uzmanısın. İş emri atama sonuçlarını analiz edip, 
depo yöneticisine 3-4 cümlelik profesyonel bir özet sun.

**Atama Detayları:**
- Kullanılan Yöntem: {method_name}
- Toplam İş Emri: {total_orders} adet
- Atanan İş Emri: {assigned_orders} adet
- Atanmayan: {total_orders - assigned_orders} adet

**Operatör Başına Atamalar:**
{summary_text}

Özette şunları belirt:
1. Hangi yöntem kullanıldı
2. Kaç iş emri atandı
3. Operatörler arasında denge sağlandı mı
4. Varsa özel durumlar

Sadece özet metni döndür.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Sen profesyonel bir depo yönetimi asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    
    def summarize_compliance(self,
                            assignments: pd.DataFrame,
                            compliance_result: Dict[str, Any]) -> str:
        """Uyumluluk kontrolü sonuçlarını özetler"""
        
        total_violations = compliance_result.get('total_violations', 0)
        risk_level = compliance_result.get('risk_level', 'UNKNOWN')
        warnings = compliance_result.get('warnings', [])
        
        warnings_text = "\n".join([f"- {w}" for w in warnings]) if warnings else "Uyarı yok"
        
        prompt = f"""
Sen bir depo yönetimi uzmanısın. Atamalar yapıldıktan sonra yasal uyumluluk 
kontrolü yapıldı. Sonuçları depo yöneticisine 3-4 cümlelik profesyonel bir özet sun.

**Uyumluluk Sonuçları:**
- Risk Seviyesi: {risk_level}
- Toplam İhlal: {total_violations}
- Uyarılar:
{warnings_text}

Özette şunları belirt:
1. Atamalar yasal olarak uyumlu mu
2. Risk seviyesi ne
3. Varsa öneriler

Sadece özet metni döndür.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Sen profesyonel bir depo yönetimi asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Test
    summarizer = LLMSummarizer()
    
    summary = summarizer.summarize_workforce(
        total_orders=74,
        total_items=5177,
        total_volume=14491,
        total_operators=8,
        active_operators=6,
        on_leave=1,
        sick_leave=1
    )
    
    print("📊 İşgücü Özeti:")
    print(summary)