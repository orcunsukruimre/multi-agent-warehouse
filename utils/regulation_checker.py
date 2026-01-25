"""
Regülasyon kontrolü için utility fonksiyonları
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


class RegulationChecker:
    """İş Kanunu ve İSG regülasyonlarını kontrol eden sınıf"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "regulations.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def check_weekly_hours(self, current_hours: float, additional_hours: float = 0) -> Dict[str, Any]:
        """
        Haftalık çalışma saati limitini kontrol eder.
        """
        max_hours = self.config['labor_law']['max_weekly_hours']
        total_hours = current_hours + additional_hours
        
        is_compliant = total_hours <= max_hours
        remaining = max_hours - current_hours
        
        # Uyarı seviyeleri
        usage_percent = (total_hours / max_hours) * 100
        warning_threshold = self.config['compliance']['warning_threshold']
        critical_threshold = self.config['compliance']['critical_threshold']
        
        status = "OK"
        if usage_percent >= critical_threshold:
            status = "CRITICAL"
        elif usage_percent >= warning_threshold:
            status = "WARNING"
        
        return {
            "compliant": is_compliant,
            "current_hours": current_hours,
            "additional_hours": additional_hours,
            "total_hours": total_hours,
            "max_hours": max_hours,
            "remaining_hours": remaining,
            "usage_percent": usage_percent,
            "status": status
        }
    
    def check_overtime_limit(self, current_weekly_overtime: float, requested_overtime: float) -> Dict[str, Any]:
        """Fazla mesai limitlerini kontrol eder"""
        max_weekly_overtime = self.config['labor_law']['overtime']['max_weekly_hours']
        max_daily_overtime = self.config['labor_law']['overtime']['max_daily_hours']
        
        total_overtime = current_weekly_overtime + requested_overtime
        daily_compliant = requested_overtime <= max_daily_overtime
        weekly_compliant = total_overtime <= max_weekly_overtime
        
        return {
            "daily_compliant": daily_compliant,
            "weekly_compliant": weekly_compliant,
            "compliant": daily_compliant and weekly_compliant,
            "requested_overtime": requested_overtime,
            "max_daily_overtime": max_daily_overtime,
            "current_weekly_overtime": current_weekly_overtime,
            "max_weekly_overtime": max_weekly_overtime,
            "remaining_overtime": max_weekly_overtime - current_weekly_overtime
        }
    
    def check_workload_limits(self, 
                             num_orders: int, 
                             total_volume: float, 
                             total_items: int,
                             experience: str = "mid") -> Dict[str, Any]:
        """Operatör iş yükü limitlerini kontrol eder"""
        warehouse = self.config['warehouse_rules']
        
        # Tecrübe çarpanı uygula
        multiplier = warehouse['experience_multipliers'].get(experience, 1.0)
        
        max_orders = int(warehouse['max_orders_per_operator'] * multiplier)
        max_volume = warehouse['max_volume_per_operator'] * multiplier
        max_items = warehouse['max_items_per_operator'] * multiplier
        
        orders_compliant = num_orders <= max_orders
        volume_compliant = total_volume <= max_volume
        items_compliant = total_items <= max_items
        
        violations = []
        if not orders_compliant:
            violations.append(f"İş emri sayısı limitini aşıyor: {num_orders} > {max_orders}")
        if not volume_compliant:
            violations.append(f"Hacim limitini aşıyor: {total_volume} > {max_volume}")
        if not items_compliant:
            violations.append(f"Ürün adedi limitini aşıyor: {total_items} > {max_items}")
        
        return {
            "compliant": orders_compliant and volume_compliant and items_compliant,
            "orders_compliant": orders_compliant,
            "volume_compliant": volume_compliant,
            "items_compliant": items_compliant,
            "violations": violations,
            "limits": {
                "max_orders": max_orders,
                "max_volume": max_volume,
                "max_items": max_items
            },
            "actual": {
                "num_orders": num_orders,
                "total_volume": total_volume,
                "total_items": total_items
            }
        }
    
    def calculate_risk_score(self, workload_check: Dict, weekly_hours_check: Dict) -> Tuple[int, str]:
        """
        Genel risk skorunu hesaplar (1-4 arası)
        """
        risk_score = 1
        
        if not workload_check['compliant']:
            risk_score += len(workload_check['violations'])
        
        if weekly_hours_check['status'] == "WARNING":
            risk_score += 1
        elif weekly_hours_check['status'] == "CRITICAL":
            risk_score += 2
        
        risk_levels = self.config['occupational_safety']['risk_levels']
        if risk_score <= risk_levels['low']:
            risk_level = "DÜŞÜK"
        elif risk_score <= risk_levels['medium']:
            risk_level = "ORTA"
        elif risk_score <= risk_levels['high']:
            risk_level = "YÜKSEK"
        else:
            risk_level = "KRİTİK"
        
        return min(risk_score, 4), risk_level