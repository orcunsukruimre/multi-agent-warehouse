"""
Inventory Agent (Stok/İş Yükü Analiz Ajanı)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from typing import Dict, Any, List
from data.warehouse_data import get_warehouse_data


class InventoryAgent:
    """İş emirlerini analiz eden ajan"""
    
    def __init__(self):
        self.name = "Inventory Agent"
        self.description = "İş emirlerini analiz eder ve iş yükü hesaplar"
    
    def analyze_orders(self) -> Dict[str, Any]:
        """Tüm iş emirlerini analiz eder ve özet rapor üretir."""
        tur_info, _, _ = get_warehouse_data()
        
        total_orders = len(tur_info)
        total_items = tur_info['UrunAdedi'].sum()
        total_volume = tur_info['UrunDesi'].sum()
        
        avg_items_per_order = total_items / total_orders
        avg_volume_per_order = total_volume / total_orders
        
        critical_threshold_volume = tur_info['UrunDesi'].quantile(0.75)
        critical_threshold_items = tur_info['UrunAdedi'].quantile(0.75)
        
        critical_orders = tur_info[
            (tur_info['UrunDesi'] >= critical_threshold_volume) | 
            (tur_info['UrunAdedi'] >= critical_threshold_items)
        ]
        
        priority_high = critical_orders['IsEmri'].tolist()[:15]
        
        estimated_time_minutes = (total_items * 2) + (total_volume / 100 * 5)
        estimated_time_hours = estimated_time_minutes / 60
        
        return {
            "agent_name": self.name,
            "total_orders": int(total_orders),
            "total_items": int(total_items),
            "total_volume": int(total_volume),
            "avg_items_per_order": round(avg_items_per_order, 2),
            "avg_volume_per_order": round(avg_volume_per_order, 2),
            "critical_orders_count": len(critical_orders),
            "priority_high_orders": priority_high,
            "estimated_time_hours": round(estimated_time_hours, 2),
            "recommendation": self._generate_recommendation(total_orders, total_items, estimated_time_hours)
        }
    
    def _generate_recommendation(self, total_orders: int, total_items: int, estimated_hours: float) -> str:
        """İş yükü analiz sonucuna göre öneri üretir"""
        if estimated_hours > 60:
            priority = "ÇOK YÜKSEK"
            action = "Acil ek kaynak gerekli. Fazla mesai veya geçici işçi alımı önerilir."
        elif estimated_hours > 40:
            priority = "YÜKSEK"
            action = "Mevcut operatörlere ek olarak 2-3 operatör daha gerekli."
        elif estimated_hours > 25:
            priority = "ORTA"
            action = "Mevcut kapasite ile yönetilebilir, ancak optimizasyon gerekebilir."
        else:
            priority = "DÜŞÜK"
            action = "Normal operasyonel kapasite yeterli."
        
        return f"Öncelik: {priority} - {action}"
    
    def get_summary_text(self) -> str:
        """İnsan okunabilir özet metin üretir"""
        result = self.analyze_orders()
        
        summary = f"""
    ╔══════════════════════════════════════════════════════════╗
    ║          INVENTORY AGENT - İŞ YÜKÜ ANALİZİ              ║
    ╚══════════════════════════════════════════════════════════╝

    📦 Genel Durum:
    • Toplam İş Emri: {result['total_orders']} adet
    • Toplanacak Ürün: {result['total_items']} adet
    • Toplam Hacim: {result['total_volume']} desi
    • Tahmini Süre: {result['estimated_time_hours']} saat

    📊 Ortalama Değerler:
    • İş Emri Başına Ürün: {result['avg_items_per_order']} adet
    • İş Emri Başına Hacim: {result['avg_volume_per_order']} desi

    ⚠️  Kritik İş Emirleri:
    • Yüksek Öncelikli: {result['critical_orders_count']} iş emri
    • İlk 5 Öncelikli İş: {', '.join(map(str, result['priority_high_orders'][:5]))}

    💡 ÖNERİ:
    {result['recommendation']}
    """
        return summary