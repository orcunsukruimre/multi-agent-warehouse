"""
Assignment Agent (Atama Ajanı) - Temiz Versiyon

Görevleri:
- İş emirlerini operatörlere atamak
- LLM ile özet üretmek
- Uyumluluk kontrolü yapmak
- Human-in-the-Loop karar mekanizması
- Excel rapor ve görselleştirme
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from typing import Dict, Any
from datetime import datetime

from data.warehouse_data import get_warehouse_data
from tools.optimizer import AssignmentOptimizer
from tools.llm_summarizer import LLMSummarizer
from tools.visualizer import AssignmentVisualizer
from agents.compliance_agent import ComplianceAgent
from openai import OpenAI


class AssignmentAgent:
    """İş emri atama ve raporlama ajanı"""
    
    def __init__(self):
        self.name = "Assignment Agent"
        self.description = "İş emirlerini operatörlere atar ve LLM ile raporlar"
        
        self.optimizer = AssignmentOptimizer()
        self.llm = LLMSummarizer()
        self.visualizer = AssignmentVisualizer()
        self.compliance = ComplianceAgent()
        self.client = OpenAI(api_key=self.llm.client.api_key)
    
    def run_full_assignment(self) -> Dict[str, Any]:
        """
        TAM AGENTIC AI WORKFLOW
        
        1. Giriş Özeti (LLM)
        2. İlk Atama
        3. Uyumluluk Kontrolü
        4. Human-in-the-Loop (gerekirse)
        5. Final Atama
        6. Sonuç Özeti (LLM)
        7. Excel + Grafikler
        """
        
        print("\n" + "="*80)
        print(" " * 20 + "🤖 AGENTIC AI - DEPO YÖNETİM SİSTEMİ")
        print("="*80 + "\n")
        
        # ========================================
        # VERİ YÜKLEME
        # ========================================
        tur_info, operators, operator_status = get_warehouse_data()
        
        total_orders = len(tur_info)
        total_items = tur_info['UrunAdedi'].sum()
        total_volume = tur_info['UrunDesi'].sum()
        total_operators = len(operators)
        active_operators_count = len(operator_status[operator_status['Status'] == 'active'])
        on_leave = len(operator_status[operator_status['Status'] == 'on_leave'])
        sick_leave = len(operator_status[operator_status['Status'] == 'sick_leave'])
        
        # Başlangıç değerlerini sakla
        initial_active_count = active_operators_count
        
        # ========================================
        # 1. GİRİŞ ÖZETİ (LLM)
        # ========================================
        print("="*80)
        print("📊 ADIM 1: GİRİŞ DURUMU - DEPO YÖNETİMİNE ÖZET")
        print("="*80 + "\n")
        print("📸 [EKRAN GÖRÜNTÜSÜ 1: Giriş Özeti]\n")
        
        intro_summary = self._generate_intro_summary(
            total_orders, total_items, total_volume,
            total_operators, active_operators_count, on_leave, sick_leave
        )
        
        print("💬 DEPO YÖNETİMİNE GİRİŞ ÖZETİ:")
        print("─" * 80)
        print(intro_summary)
        print("─" * 80)
        
        print(f"\n📋 Detaylı Veriler:")
        print(f"   İş Emirleri: {total_orders} tur")
        print(f"   Toplam Ürün: {total_items} adet")
        print(f"   Toplam Hacim: {total_volume} desi")
        print(f"   Aktif Operatör: {active_operators_count}/{total_operators}")
        
        # ========================================
        # 2. İLK ATAMA
        # ========================================
        print("\n" + "="*80)
        print("🔧 ADIM 2: İŞ EMRİ ATAMALARI YAPILIYOR")
        print("="*80 + "\n")
        
        if active_operators_count == 0:
            print("❌ HATA: Aktif operatör yok!")
            return {"success": False, "error": "NO_ACTIVE_OPERATORS"}
        
        assignments, method = self.optimizer.assign(tur_info, operators, operator_status)
        assigned_count = len(assignments['IsEmri'].unique())
        
        print(f"✅ İlk Atama Tamamlandı:")
        print(f"   • Yöntem: {'Optimizasyon' if method == 'OPTIMIZATION' else 'Sezgisel Algoritma'}")
        print(f"   • Atanan İş Emri: {assigned_count}/{total_orders}")
        
        # ========================================
        # 3. UYUMLULUK DEĞERLENDİRMESİ
        # ========================================
        print("\n" + "="*80)
        print("⚖️  ADIM 3: UYUMLULUK DEĞERLENDİRMESİ")
        print("="*80 + "\n")
        
        compliance_result = self._check_compliance(assignments)
        
        print(f"📊 Uyumluluk Sonucu:")
        print(f"   • Durum: {'✅ UYUMLU' if compliance_result['overall_compliant'] else '❌ UYUMSUZ'}")
        print(f"   • Risk Seviyesi: {compliance_result['risk_level']}")
        print(f"   • İhlal Sayısı: {compliance_result['total_violations']}")
        
        # Uyumsuz operatörleri tespit et
        non_compliant_operators = [
            check['operator_id'] 
            for check in compliance_result['workload_compliance']['operator_checks']
            if not check['compliant']
        ]
        
        if non_compliant_operators:
            print(f"\n⚠️  Uyumsuz Operatörler: {len(non_compliant_operators)} kişi")
            print(f"   • Operatör ID'leri: {non_compliant_operators}")
            print(f"   • Neden: 11+ tur atandı (günlük limit aşımı)")
        
        # ========================================
        # 4. HUMAN-IN-THE-LOOP (Gerekirse)
        # ========================================
        human_decision = None
        decision_explanation = ""
        
        if not compliance_result['overall_compliant']:
            print("\n" + "="*80)
            print("👤 ADIM 4: KARAR GEREKİYOR - HUMAN-IN-THE-LOOP")
            print("="*80)
            print("\n📸 [EKRAN GÖRÜNTÜSÜ 2: Karar Noktası]\n")
            
            # Karar al
            choice = self._ask_human_decision(
                total_orders, active_operators_count, 
                len(non_compliant_operators), compliance_result
            )
            
            if choice == 'A':
                # Ek operatör ekle
                add_count = 1
                
                assignments, method, assigned_count, compliance_result, active_operators_count, decision_explanation = \
                    self._add_operators(
                        add_count, tur_info, operators, operator_status,
                        initial_active_count, len(non_compliant_operators)
                    )
                
                human_decision = f"EK_KAYNAK_{add_count}_OPERATOR"
            
            elif choice == 'B':
                # İş emri azalt
                assignments, method, assigned_count, compliance_result, decision_explanation = \
                    self._reduce_orders(
                        tur_info, operators, operator_status,
                        active_operators_count, total_orders
                    )
                
                human_decision = "EK_KAYNAK_YOK_IS_EMRI_AZALTILDI"
        
        else:
            print("\n✅ Atamalar yasal olarak uyumlu, ek aksiyona gerek yok!")
            human_decision = "UYUMLU_AKSIYON_GEREKMEDI"
            decision_explanation = (
                f"Tüm atamalar yasal limitlere uygun. "
                f"{assigned_count} iş emri {active_operators_count} operatöre başarıyla atandı."
            )
        
        # ========================================
        # 5. SONUÇ ÖZETİ (LLM)
        # ========================================
        print("\n" + "="*80)
        print("📝 ADIM 5: SONUÇ ÖZETİ (LLM)")
        print("="*80 + "\n")
        print("📸 [EKRAN GÖRÜNTÜSÜ 3: Sonuç Özeti]\n")
        
        operator_summary = assignments.groupby('Operator').agg({
            'IsEmri': 'count',
            'UrunAdedi': 'sum',
            'UrunDesi': 'sum'
        }).rename(columns={'IsEmri': 'TurSayisi'})
        
        final_total_items = assignments['UrunAdedi'].sum()
        final_total_volume = assignments['UrunDesi'].sum()
        
        result_summary = self._generate_result_summary(
            total_orders, total_items, initial_active_count,
            decision_explanation, assigned_count, active_operators_count,
            final_total_items, final_total_volume, compliance_result
        )
        
        print("💬 SONUÇ ÖZETİ:")
        print("─" * 80)
        print(result_summary)
        print("─" * 80)
        
        # ========================================
        # 6. EXCEL + GÖRSELLEŞTİRME
        # ========================================
        print("\n" + "="*80)
        print("💾 ADIM 6: EXCEL VE GÖRSELLEŞTİRME")
        print("="*80 + "\n")
        print("📸 [EKRAN GÖRÜNTÜSÜ 4: Grafikler ve Excel]\n")
        
        output_excel = self._create_excel_report(
            assignments, operator_summary, total_orders, assigned_count,
            len(operator_summary), final_total_items, final_total_volume,
            method, compliance_result, human_decision,
            intro_summary, result_summary
        )
        
        charts = self.visualizer.create_all_charts(assignments, total_orders)
        
        print(f"✅ Excel raporu oluşturuldu: {output_excel.name}")
        print(f"\n✅ Grafikler oluşturuldu:")
        for name, path in charts.items():
            print(f"   • {name}: {Path(path).name}")
        
        # ========================================
        # FİNAL EKRAN
        # ========================================
        self._print_final_summary(
            operator_summary, total_orders, assigned_count,
            final_total_items, compliance_result,
            output_excel, charts
        )
        
        return {
            "success": True,
            "intro_summary": intro_summary,
            "result_summary": result_summary,
            "human_decision": human_decision,
            "decision_explanation": decision_explanation,
            "assignments": assignments,
            "operator_summary": operator_summary,
            "compliance_result": compliance_result,
            "charts": charts,
            "output_files": {"excel": str(output_excel)},
            "stats": {
                "total_orders": total_orders,
                "assigned_orders": assigned_count,
                "total_items": final_total_items,
                "total_volume": final_total_volume,
                "active_operators": len(operator_summary),
                "risk_level": compliance_result['risk_level']
            }
        }
    
    # ========================================
    # YARDIMCI METODLAR
    # ========================================
    
    def _generate_intro_summary(self, total_orders, total_items, total_volume,
                                total_operators, active_operators_count, 
                                on_leave, sick_leave) -> str:
        """Giriş özeti üret (LLM)"""
        prompt = f"""
Sen bir depo yönetimi asistanısın. Depo müdürüne bugünkü durumu 3-4 cümlelik 
profesyonel bir özet olarak sun.

**Bugünkü Durum:**

İŞ EMİRLERİ:
- Toplam İş Emri: {total_orders} tur
- Toplanacak Ürün: {total_items} adet
- Toplam Hacim: {total_volume} desi

OPERATÖR DURUMU:
- Toplam Operatör: {total_operators} kişi
- Aktif Operatör: {active_operators_count} kişi
- İzinli: {on_leave} kişi
- Hastalık İzni: {sick_leave} kişi

Özet profesyonel ve yöneticiye bilgi verici olsun. Sadece özet metni döndür.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir depo yönetimi asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    
    def _check_compliance(self, assignments: pd.DataFrame) -> Dict[str, Any]:
        """Uyumluluk kontrolü yap"""
        workload_per_operator = assignments.groupby('Operator').agg({
            'IsEmri': 'count',
            'UrunDesi': 'sum',
            'UrunAdedi': 'sum'
        }).to_dict('index')
        
        proposed_workload = {
            int(op): {
                'orders': int(data['IsEmri']),
                'volume': int(data['UrunDesi']),
                'items': int(data['UrunAdedi'])
            }
            for op, data in workload_per_operator.items()
        }
        
        return self.compliance.analyze_compliance(proposed_workload=proposed_workload)
    
    def _ask_human_decision(self, total_orders, active_operators_count,
                       non_compliant_count, compliance_result) -> str:
        """Human-in-the-Loop karar iste"""
        print(f"\n⚠️  DURUM RAPORU:")
        print(f"   • Toplam İş Emri: {total_orders} tur")
        print(f"   • Mevcut Operatör: {active_operators_count} kişi")
        print(f"   • Uyumsuz Operatör: {non_compliant_count} kişi (11+ tur aldı)")
        print(f"   • Risk Seviyesi: {compliance_result['risk_level']}")
        
        if compliance_result['warnings']:
            print(f"\n   ⚠️  Uyarılar:")
            for warning in compliance_result['warnings'][:3]:
                print(f"      • {warning}")
        
        # Sistem analizi
        required_ops = (total_orders / self.compliance.max_tours) + 0.5
        additional_needed = max(1, int(required_ops - active_operators_count))
        
        print(f"\n💡 SİSTEM ANALİZİ:")
        print(f"   • Toplam İş Emri: {total_orders} tur")
        print(f"   • Mevcut Operatör: {active_operators_count}")
        print(f"   • Gerekli Operatör: ~{int(required_ops)}")
        print(f"   • Eksik: ~{additional_needed} operatör")
        
        print(f"\n💡 SİSTEM ÖNERİSİ:")
        print(f"   ⚠️  Not: Sadece 1 inaktif operatör eklenebilir (diğerleri izinli/hasta)")
        print(f"\n   [A] +1 Ek Operatör Al")
        print(f"       → Toplam {active_operators_count + 1} operatör")
        print(f"       → Operatör başına ~{total_orders/(active_operators_count+1):.1f} tur")
        print(f"       → Risk: {'DÜŞÜK' if total_orders/(active_operators_count+1) <= 10 else 'ORTA'}")
        
        print(f"\n   [B] Ek Operatör Alma (İş emri azalt)")
        print(f"       → Mevcut {active_operators_count} operatörle devam")
        print(f"       → Maksimum {active_operators_count * 10} iş emri atanır")
        print(f"       → {total_orders - (active_operators_count * 10)} iş emri ertelenir")
        
        print("\n" + "─"*80)
        return input("\n👤 Kararınız (A/B): ").strip().upper()
    
    def _add_operators(self, add_count, tur_info, operators, operator_status,
                  initial_active_count, non_compliant_count):
        """Ek operatör ekle ve yeniden ata"""
        print(f"\n✅ Karar: +{add_count} ek operatör alınacak\n")
        
        inactive_ops = operator_status[operator_status['Status'] != 'active']
        available_count = len(inactive_ops)
        
        # Kontrol: Hiç inaktif operatör yok mu?
        if available_count == 0:
            print(f"❌ HATA: Hiç inaktif operatör yok!")
            print(f"   Tüm operatörler zaten aktif.\n")
            
            # Mevcut durumu döndür
            assignments, method = self.optimizer.assign(tur_info, operators, operator_status)
            assigned_count = len(assignments['IsEmri'].unique())
            compliance_result = self._check_compliance(assignments)
            active_operators_count = len(operator_status[operator_status['Status'] == 'active'])
            
            decision_explanation = "Ek operatör alınamadı (tüm operatörler zaten aktif)."
            
            return assignments, method, assigned_count, compliance_result, active_operators_count, decision_explanation
        
        # Uyarı: İstenen kadar yok
        if available_count < add_count:
            print(f"⚠️  UYARI: Sadece {available_count} inaktif operatör mevcut!")
            print(f"   → Mevcut {available_count} operatör eklenecek\n")
        
        max_additional = min(available_count, add_count)
        added_operators = 0
        
        print(f"🔄 {max_additional} operatör ekleniyor...\n")
        
        # Operatörleri ekle
        for i in range(max_additional):
            idx = inactive_ops.index[added_operators]
            operator_status.loc[idx, 'Status'] = 'active'
            operator_status.loc[idx, 'WeeklyHours'] = 40
            added_operators += 1
            
            new_active_count = len(operator_status[operator_status['Status'] == 'active'])
            print(f"   • +{added_operators}. operatör eklendi (Toplam aktif: {new_active_count})")
        
        # Yeniden ata
        print(f"\n🔄 Yeniden atama yapılıyor...")
        assignments, method = self.optimizer.assign(tur_info, operators, operator_status)
        assigned_count = len(assignments['IsEmri'].unique())
        
        # Uyumluluk kontrol
        compliance_result = self._check_compliance(assignments)
        active_operators_count = len(operator_status[operator_status['Status'] == 'active'])
        
        print(f"\n✅ Atama Tamamlandı:")
        print(f"   • Atanan İş Emri: {assigned_count}/{len(tur_info)}")
        print(f"   • Uyumluluk: {'✅ UYUMLU' if compliance_result['overall_compliant'] else '❌ UYUMSUZ'}")
        print(f"   • Risk: {compliance_result['risk_level']}")
        print(f"   • Aktif Operatör: {initial_active_count} → {active_operators_count} (+{added_operators})")
        
        # Decision explanation
        decision_explanation = (
            f"{initial_active_count} aktif operatör vardı. "
            f"Atamalarda {non_compliant_count} operatörün tur sayısı 11+ oldu (günlük limit aşımı). "
            f"Yönetici onayı ile {added_operators} ek operatör alındı (toplam {active_operators_count} operatör). "
            f"{'Yasal uyumluluk sağlandı.' if compliance_result['overall_compliant'] else 'Risk seviyesi: ' + compliance_result['risk_level']}"
        )
        
        return assignments, method, assigned_count, compliance_result, active_operators_count, decision_explanation
        
    def _reduce_orders(self, tur_info, operators, operator_status,
                      active_operators_count, total_orders):
        """İş emri azalt ve uyumlu hale getir"""
        print("\n⚠️  Karar: Ek operatör alınmayacak, uyumlu kadar ata\n")
        print("🔄 Yasal limitlere uygun olacak şekilde iş emirleri azaltılıyor...\n")
        
        compliant = False
        current_orders = total_orders
        attempts = 0
        max_attempts = 15
        
        while not compliant and current_orders > active_operators_count and attempts < max_attempts:
            attempts += 1
            
            # %10 azalt
            reduce_count = max(1, int(current_orders * 0.1))
            current_orders = max(current_orders - reduce_count, active_operators_count)
            
            print(f"   Deneme {attempts}: {current_orders} iş emri deneniyor...")
            
            tur_info_reduced = tur_info.head(current_orders)
            assignments_temp, method_temp = self.optimizer.assign(tur_info_reduced, operators, operator_status)
            
            comp_temp = self._check_compliance(assignments_temp)
            
            print(f"      → {current_orders} iş: Uyumluluk {'✅' if comp_temp['overall_compliant'] else '❌'}, "
                  f"Risk: {comp_temp['risk_level']}, İhlal: {comp_temp['total_violations']}")
            
            if comp_temp['overall_compliant']:
                compliant = True
                assignments = assignments_temp
                method = method_temp
                assigned_count = current_orders
                compliance_result = comp_temp
                
                print(f"\n✅ Uyumlu atama bulundu: {current_orders}/{total_orders} iş emri")
                break
            
            # Küçük adımlarla dene
            if current_orders - active_operators_count < 5:
                current_orders -= 1
        
        if not compliant:
            # Son çare: Minimum atama
            print(f"\n⚠️  Standart azaltma başarısız, minimum atama deneniyor...")
            current_orders = active_operators_count
            
            tur_info_reduced = tur_info.head(current_orders)
            assignments, method = self.optimizer.assign(tur_info_reduced, operators, operator_status)
            compliance_result = self._check_compliance(assignments)
            assigned_count = current_orders
            
            print(f"✅ Minimum atama kabul edildi: {current_orders}/{total_orders} iş emri")
            print(f"   Risk: {compliance_result['risk_level']} (Yönetici onayı gerekli)")
        
        decision_explanation = (
            f"Ek kaynak alınmadı. {active_operators_count} operatörle çalışıldı. "
            f"Yasal limitler nedeniyle sadece {assigned_count}/{total_orders} iş emri atanabildi. "
            f"{total_orders - assigned_count} iş emri ertelendi. "
            f"Risk: {compliance_result['risk_level']}"
        )
        
        return assignments, method, assigned_count, compliance_result, decision_explanation
    
    def _generate_result_summary(self, total_orders, total_items, initial_active_count,
                                decision_explanation, assigned_count, active_operators_count,
                                final_total_items, final_total_volume, compliance_result) -> str:
        """Sonuç özeti üret (LLM)"""
        prompt = f"""
Sen bir depo yönetimi asistanısın. Atama sürecinin sonucunu depo müdürüne 
4-5 cümlelik profesyonel bir özet olarak sun.

**ATAMA SONUÇLARI:**

BAŞLANGIÇ:
- Toplam İş Emri: {total_orders} tur
- Toplam Ürün: {total_items} adet
- Başlangıç Operatör: {initial_active_count} kişi

SÜREÇTEKİ GELİŞMELER:
{decision_explanation}

FİNAL DURUM:
- Atanan İş Emri: {assigned_count}/{total_orders} ({(assigned_count/total_orders*100):.0f}%)
- Çalışan Operatör: {active_operators_count} kişi
- Toplanacak Ürün: {final_total_items} adet
- Toplam Hacim: {final_total_volume} desi
- Risk Seviyesi: {compliance_result['risk_level']}
- Yasal Uyumluluk: {'UYUMLU ✅' if compliance_result['overall_compliant'] else 'UYUMSUZ ❌'}

Özet profesyonel, doğru ve net olsun. Sadece özet metni döndür.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir depo yönetimi asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_excel_report(self, assignments, operator_summary, total_orders,
                            assigned_count, operator_count, final_total_items,
                            final_total_volume, method, compliance_result,
                            human_decision, intro_summary, result_summary):
        """Excel raporu oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_excel = Path(__file__).parent.parent / "outputs" / f"atama_raporu_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            # Sayfa 1: Atama Listesi
            assignments_display = assignments.copy()
            assignments_display.columns = ['Operatör ID', 'İş Emri', 'Hacim (desi)', 'Ürün Adedi']
            assignments_display.to_excel(writer, sheet_name='Atama Listesi', index=False)
            
            # Sayfa 2: Operatör Özeti
            operator_summary_display = operator_summary.copy()
            operator_summary_display.columns = ['Tur Sayısı', 'Toplam Ürün', 'Toplam Hacim']
            operator_summary_display.to_excel(writer, sheet_name='Operatör Özeti')
            
            # Sayfa 3: Genel Özet
            summary_data = pd.DataFrame({
                'Metrik': [
                    'Toplam İş Emri',
                    'Atanan İş Emri',
                    'Atanmayan İş Emri',
                    'Çalışan Operatör',
                    'Toplam Ürün',
                    'Toplam Hacim (desi)',
                    'Atama Yöntemi',
                    'Risk Seviyesi',
                    'Yasal Uyumluluk',
                    'Yönetici Kararı'
                ],
                'Değer': [
                    total_orders,
                    assigned_count,
                    total_orders - assigned_count,
                    operator_count,
                    final_total_items,
                    final_total_volume,
                    'Optimizasyon' if method == 'OPTIMIZATION' else 'Sezgisel',
                    compliance_result['risk_level'],
                    'Uyumlu' if compliance_result['overall_compliant'] else 'Uyumsuz',
                    human_decision if human_decision else 'Gerekli değil'
                ]
            })
            summary_data.to_excel(writer, sheet_name='Genel Özet', index=False)
            
            # Sayfa 4: LLM Özetleri
            llm_summaries = pd.DataFrame({
                'Bölüm': ['Giriş Özeti', 'Sonuç Özeti'],
                'LLM Metni': [intro_summary, result_summary]
            })
            llm_summaries.to_excel(writer, sheet_name='LLM Özetleri', index=False)
        
        return output_excel
    
    def _print_final_summary(self, operator_summary, total_orders, assigned_count,
                            final_total_items, compliance_result, output_excel, charts):
        """Final özet ekrana yazdır"""
        print("\n" + "="*80)
        print("✅ AGENTIC AI SÜRECİ TAMAMLANDI")
        print("="*80 + "\n")
        
        print("📊 Operatör Başına Metrikler:")
        print("─" * 80)
        print(operator_summary.to_string())
        print("─" * 80)
        
        print(f"\n📈 GENEL İSTATİSTİKLER:")
        print(f"   • Toplam İş Emri: {total_orders}")
        print(f"   • Atanan: {assigned_count} ({(assigned_count/total_orders*100):.1f}%)")
        print(f"   • Çalışan Operatör: {len(operator_summary)}")
        print(f"   • Toplanan Ürün: {final_total_items:,}")
        print(f"   • Risk: {compliance_result['risk_level']}")
        
        print(f"\n💾 ÇIKTI DOSYALARI:")
        print(f"   • Excel: {output_excel.name}")
        print(f"   • Grafikler: {len(charts)} adet PNG")


if __name__ == "__main__":
    # Test
    agent = AssignmentAgent()
    result = agent.run_full_assignment()
    
    if result['success']:
        print("\n🎉 Test başarılı!")
    else:
        print(f"\n❌ Hata: {result.get('error')}")