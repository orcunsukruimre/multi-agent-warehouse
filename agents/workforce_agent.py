"""
Workforce Agent (İşgücü/İK Analiz Ajanı)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from typing import Dict, Any, List
from data.warehouse_data import get_warehouse_data
import yaml


class WorkforceAgent:
    """İşgücü ve operatör durumunu analiz eden ajan"""
    
    def __init__(self):
        self.name = "Workforce Agent"
        self.description = "Operatör durumunu analiz eder ve kaynak planlaması yapar"
        
        config_path = Path(__file__).parent.parent / "config" / "regulations.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def analyze_workforce(self) -> Dict[str, Any]:
        """İşgücü analizi yap (Basitleştirilmiş)"""
        tur_info, operators, operator_status = get_warehouse_data()
        
        # Operatör durumları
        total_operators = len(operators)
        active_count = len(operator_status[operator_status['Status'] == 'active'])
        on_leave = len(operator_status[operator_status['Status'] == 'on_leave'])
        sick_leave = len(operator_status[operator_status['Status'] == 'sick_leave'])
        
        # Kapasite hesaplama
        capacity = self._calculate_capacity(active_count)
        
        # Vardiya dağılımı
        shift_distribution = operator_status['Shift'].value_counts().to_dict()
        
        # Tecrübe dağılımı
        experience_distribution = operator_status['Experience'].value_counts().to_dict()
        
        return {
            'total_operators': total_operators,
            'active_count': active_count,
            'on_leave_count': on_leave,
            'sick_leave_count': sick_leave,
            'capacity': capacity,
            'shift_distribution': shift_distribution,
            'experience_distribution': experience_distribution
        }
    
    def _calculate_capacity(self, active_operators: int) -> Dict[str, Any]:
        """
        Operatör kapasitesini hesapla (Basitleştirilmiş)
        
        Args:
            active_operators: Aktif operatör sayısı
        
        Returns:
            Kapasite bilgileri
        """
        # Basit varsayımlar
        max_tours_per_operator = self.config['working_hours']['max_tours_per_day']  # 10 tur
        minutes_per_tour = self.config['working_hours']['minutes_per_tour']  # 40 dakika
        daily_minutes = self.config['working_hours']['daily_minutes']  # 435 dakika
        
        # Günlük kapasite
        daily_capacity = active_operators * max_tours_per_operator
        
        return {
            'active_operators': active_operators,
            'max_tours_per_operator': max_tours_per_operator,
            'minutes_per_tour': minutes_per_tour,
            'daily_minutes': daily_minutes,
            'daily_capacity_tours': daily_capacity
        }
    def _analyze_overtime_situation(self, active_operators: int) -> Dict[str, Any]:
        """
        Fazla mesai durumunu analiz et (Basitleştirilmiş)
        
        Args:
            active_operators: Aktif operatör sayısı
        
        Returns:
            Fazla mesai analizi
        """
        # Basit kural: Günlük 10 tur limit
        max_tours_per_day = self.config['working_hours']['max_tours_per_day']
        
        return {
            'max_tours_per_day': max_tours_per_day,
            'active_operators': active_operators,
            'recommendation': "Normal çalışma limitleri yeterli" if active_operators >= 6 else "Ek operatör önerilir"
        }
    
    def _assess_resource_need(self, available_operators: int, total_capacity: int, overtime_analysis: Dict) -> Dict[str, Any]:
        """Kaynak ihtiyacını değerlendirir"""
        if available_operators < 4:
            need = "CRITICAL"
            additional_needed = 4 - available_operators
        elif available_operators < 6:
            need = "HIGH"
            additional_needed = 2
        elif overtime_analysis['overtime_feasible']:
            need = "MODERATE"
            additional_needed = 0
        else:
            need = "LOW"
            additional_needed = 0
        
        return {
            "need_level": need,
            "additional_operators_needed": additional_needed,
            "overtime_as_alternative": overtime_analysis['overtime_feasible']
        }
    
    def _generate_recommendation(self, resource_need: Dict, overtime_analysis: Dict) -> str:
        """Kaynak planlaması önerisi üretir"""
        need = resource_need['need_level']
        additional = resource_need['additional_operators_needed']
        
        if need == "CRITICAL":
            return f"KRİTİK: Acil {additional} operatör eklenmelidir. Fazla mesai ile kapatılamaz."
        elif need == "HIGH":
            return f"YÜKSEK: {additional} ek operatör veya fazla mesai planlanmalıdır."
        elif need == "MODERATE":
            return f"ORTA: Mevcut kapasite yeterli ancak fazla mesai gerekebilir ({overtime_analysis['total_available_overtime_hours']} saat mevcut)."
        else:
            return "DÜŞÜK: Mevcut kapasite yeterlidir."
    
    def get_summary_text(self) -> str:
        """Özet metin döndür"""
        result = self.analyze_workforce()
        
        return f"""
    İŞGÜCÜ ANALİZİ RAPORU (Basitleştirilmiş):

    📊 Operatör Durumu:
    • Toplam Operatör: {result['total_operators']}
    • Aktif: {result['active_count']}
    • İzinli: {result['on_leave_count']}
    • Hastalık İzni: {result['sick_leave_count']}

    ⏱️  Günlük Kapasite:
    • Aktif Operatör: {result['capacity']['active_operators']} kişi
    • Maksimum Tur/Operatör: {result['capacity']['max_tours_per_operator']} tur
    • Tur Süresi: {result['capacity']['minutes_per_tour']} dakika
    • Günlük Çalışma: {result['capacity']['daily_minutes']} dakika
    • Toplam Kapasite: {result['capacity']['daily_capacity_tours']} tur/gün

    📅 Vardiya Dağılımı:
    {chr(10).join([f"   • {k}: {v} operatör" for k, v in result['shift_distribution'].items()])}

    🎓 Tecrübe Seviyesi:
    {chr(10).join([f"   • {k}: {v} operatör" for k, v in result['experience_distribution'].items()])}
    """
    
    def _format_dict(self, d: Dict) -> str:
        """Dictionary'yi güzel formatlar"""
        return '\n   '.join([f"• {k}: {v}" for k, v in d.items()])