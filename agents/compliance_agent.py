"""
Compliance Agent - Basitleştirilmiş Yasal Uyumluluk Kontrolü

KURAL:
- Bir tur = 40 dakika
- Günlük çalışma = 435 dakika (7.25 saat)
- Maksimum tur = 10 tur/gün
- 11+ tur = İHLAL (KRİTİK)
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List


class ComplianceAgent:
    """Basitleştirilmiş Uyumluluk Kontrolü"""
    
    def __init__(self):
        """Regülasyonları yükle"""
        config_path = Path(__file__).parent.parent / "config" / "regulations.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.regulations = yaml.safe_load(f)
        
        self.max_tours = self.regulations['working_hours']['max_tours_per_day']
        self.violation_threshold = self.regulations['violations']['tour_limit_exceeded']['threshold']
    
    def analyze_compliance(self, proposed_workload: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        """
        Atamaların yasal uyumluluğunu kontrol et
        
        Args:
            proposed_workload: {operator_id: {'orders': int, 'volume': int, 'items': int}}
        
        Returns:
            {
                'overall_compliant': bool,
                'risk_level': str,
                'total_violations': int,
                'operator_checks': List[dict],
                'warnings': List[str]
            }
        """
        operator_checks = []
        total_violations = 0
        warnings = []
        
        for operator_id, workload in proposed_workload.items():
            tour_count = workload['orders']
            
            # Tur limiti kontrolü
            if tour_count >= self.violation_threshold:
                # İHLAL!
                compliant = False
                violation_count = 1
                total_violations += 1
                
                warnings.append(
                    f"Operatör {operator_id}: {tour_count} tur atandı "
                    f"(limit: {self.max_tours} tur). "
                    f"Günlük çalışma süresi aşılıyor!"
                )
            else:
                # UYUMLU
                compliant = True
                violation_count = 0
            
            operator_checks.append({
                'operator_id': operator_id,
                'tour_count': tour_count,
                'compliant': compliant,
                'violation_count': violation_count
            })
        
        # Genel uyumluluk
        overall_compliant = total_violations == 0
        
        # Risk seviyesi
        if total_violations == 0:
            risk_level = "DÜŞÜK"
        else:
            risk_level = "KRİTİK"
        
        return {
            'overall_compliant': overall_compliant,
            'risk_level': risk_level,
            'total_violations': total_violations,
            'workload_compliance': {
                'operator_checks': operator_checks
            },
            'warnings': warnings
        }
    
    def get_summary_text(self) -> str:
        """Uyumluluk kurallarını özetle"""
        return f"""
YASAL UYUMLULUK KURALLARI (Basitleştirilmiş):

📋 Günlük Çalışma Kuralı:
   • Bir tur süresi: 40 dakika
   • Günlük verimli çalışma: 435 dakika (7.25 saat)
   • Maksimum tur/gün: {self.max_tours} tur
   
⚠️  İhlal Tanımı:
   • {self.violation_threshold}+ tur atanması = KRİTİK İHLAL
   • Günlük çalışma süresi aşılmış demektir
   
✅ Uyumlu Atama:
   • Operatör başına 0-{self.max_tours} tur
"""


if __name__ == "__main__":
    # Test
    agent = ComplianceAgent()
    print(agent.get_summary_text())
    
    # Test senaryosu
    test_workload = {
        1: {'orders': 12, 'volume': 2500, 'items': 800},  # İHLAL (12 tur)
        2: {'orders': 10, 'volume': 2000, 'items': 700},  # UYUMLU (10 tur)
        3: {'orders': 8, 'volume': 1800, 'items': 600},   # UYUMLU (8 tur)
    }
    
    result = agent.analyze_compliance(test_workload)
    
    print("\n" + "="*70)
    print("TEST SONUÇLARI:")
    print("="*70)
    print(f"Genel Uyumluluk: {'✅ UYUMLU' if result['overall_compliant'] else '❌ UYUMSUZ'}")
    print(f"Risk Seviyesi: {result['risk_level']}")
    print(f"Toplam İhlal: {result['total_violations']}")
    
    if result['warnings']:
        print("\n⚠️  Uyarılar:")
        for warning in result['warnings']:
            print(f"   • {warning}")