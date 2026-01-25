"""
Atama Sonuçları Görselleştirme
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için


class AssignmentVisualizer:
    """Atama sonuçlarını görselleştirir"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Türkçe karakter desteği
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    def create_assignment_summary(self, 
                                  assignments: pd.DataFrame,
                                  total_orders: int,
                                  filename: str = "assignment_summary.png") -> str:
        """
        Atama özeti grafiği oluşturur.
        
        3 alt grafik:
        1. Operatör başına tur sayısı (bar chart)
        2. Operatör başına ürün adedi (bar chart)
        3. Operatör başına hacim (bar chart)
        """
        # Özet hesapla
        summary = assignments.groupby('Operator').agg({
            'IsEmri': 'count',
            'UrunAdedi': 'sum',
            'UrunDesi': 'sum'
        }).rename(columns={'IsEmri': 'TurSayisi'})
        
        # Figure oluştur
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Depo İş Emri Atama Özeti', fontsize=16, fontweight='bold')
        
        # 1. Operatör başına tur sayısı
        ax1 = axes[0, 0]
        operators = summary.index.astype(str)
        tur_counts = summary['TurSayisi'].values
        bars1 = ax1.bar(operators, tur_counts, color='steelblue', alpha=0.8)
        ax1.set_xlabel('Operatör', fontsize=11)
        ax1.set_ylabel('Tur Sayısı', fontsize=11)
        ax1.set_title('Operatör Başına Tur Sayısı', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Değerleri bar üzerine yaz
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        # 2. Operatör başına ürün adedi
        ax2 = axes[0, 1]
        item_counts = summary['UrunAdedi'].values
        bars2 = ax2.bar(operators, item_counts, color='coral', alpha=0.8)
        ax2.set_xlabel('Operatör', fontsize=11)
        ax2.set_ylabel('Ürün Adedi', fontsize=11)
        ax2.set_title('Operatör Başına Ürün Adedi', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        # 3. Operatör başına hacim (desi)
        ax3 = axes[1, 0]
        volumes = summary['UrunDesi'].values
        bars3 = ax3.bar(operators, volumes, color='mediumseagreen', alpha=0.8)
        ax3.set_xlabel('Operatör', fontsize=11)
        ax3.set_ylabel('Hacim (desi)', fontsize=11)
        ax3.set_title('Operatör Başına Hacim', fontsize=12, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        # 4. Atama durumu (pie chart)
        ax4 = axes[1, 1]
        assigned = len(assignments)
        unassigned = total_orders - assigned
        
        if unassigned > 0:
            sizes = [assigned, unassigned]
            labels = [f'Atanan\n({assigned})', f'Atanmayan\n({unassigned})']
            colors = ['#66b3ff', '#ff9999']
            explode = (0.05, 0.05)
        else:
            sizes = [assigned]
            labels = [f'Atanan\n({assigned})']
            colors = ['#66b3ff']
            explode = (0.05,)
        
        ax4.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 10})
        ax4.set_title('İş Emri Atama Durumu', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Kaydet
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_balance_chart(self,
                            assignments: pd.DataFrame,
                            filename: str = "workload_balance.png") -> str:
        """
        İş yükü dengesi grafiği oluşturur.
        
        Her operatör için tur, ürün ve hacim normalleştirilmiş radar chart.
        """
        summary = assignments.groupby('Operator').agg({
            'IsEmri': 'count',
            'UrunAdedi': 'sum',
            'UrunDesi': 'sum'
        }).rename(columns={'IsEmri': 'TurSayisi'})
        
        # Normalize et (0-100 arası)
        summary_norm = summary.copy()
        for col in summary_norm.columns:
            max_val = summary_norm[col].max()
            if max_val > 0:
                summary_norm[col] = (summary_norm[col] / max_val) * 100
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        operators = summary_norm.index.astype(str)
        x = range(len(operators))
        width = 0.25
        
        ax.bar([i - width for i in x], summary_norm['TurSayisi'], width, 
               label='Tur Sayısı', color='steelblue', alpha=0.8)
        ax.bar(x, summary_norm['UrunAdedi'], width,
               label='Ürün Adedi', color='coral', alpha=0.8)
        ax.bar([i + width for i in x], summary_norm['UrunDesi'], width,
               label='Hacim (desi)', color='mediumseagreen', alpha=0.8)
        
        ax.set_xlabel('Operatör', fontsize=12)
        ax.set_ylabel('Normalleştirilmiş İş Yükü (%)', fontsize=12)
        ax.set_title('Operatörler Arası İş Yükü Dengesi', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(operators)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 110)
        
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_all_charts(self, 
                         assignments: pd.DataFrame,
                         total_orders: int) -> dict:
        """Tüm grafikleri oluşturur"""
        
        charts = {
            "summary": self.create_assignment_summary(assignments, total_orders),
            "balance": self.create_balance_chart(assignments)
        }
        
        return charts


if __name__ == "__main__":
    # Test
    from data.warehouse_data import get_warehouse_data
    from tools.optimizer import AssignmentOptimizer
    
    tur_info, operators, operator_status = get_warehouse_data()
    
    optimizer = AssignmentOptimizer()
    assignments, method = optimizer.assign(tur_info, operators, operator_status)
    
    visualizer = AssignmentVisualizer()
    charts = visualizer.create_all_charts(assignments, len(tur_info))
    
    print("📊 Grafikler oluşturuldu:")
    for name, path in charts.items():
        print(f"   {name}: {path}")