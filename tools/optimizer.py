"""
Optimizasyon ve Sezgisel Atama Araçları
"""
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from pulp import *


class AssignmentOptimizer:
    """İş emri atama optimizasyonu"""
    
    def __init__(self):
        self.name = "Assignment Optimizer"
    
    def optimize(self, 
             tur_info: pd.DataFrame, 
             operators: pd.DataFrame,
             operator_status: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], str]:
        """
        PuLP ile matematiksel optimizasyon - GLPK Solver (Mac uyumlu)
        """
        try:
            from pulp import (LpProblem, LpMinimize, LpVariable, lpSum, 
                            LpBinary, LpStatus, GLPK)
            
            # Sadece aktif operatörleri al
            active_ops = operator_status[operator_status['Status'] == 'active']['Operator'].tolist()
            
            if len(active_ops) == 0:
                return None, "NO_ACTIVE_OPERATORS"
            
            # Model oluştur
            model = LpProblem("Is_Emri_Atama", LpMinimize)
            
            # Karar değişkenleri
            job_ids = tur_info['IsEmri'].tolist()
            x = {}
            for i in active_ops:
                for j in job_ids:
                    x[(i, j)] = LpVariable(f"x_{i}_{j}", cat=LpBinary)
            
            y = LpVariable("y", lowBound=0)
            z = LpVariable("z", lowBound=0)
            
            # Amaç fonksiyonu
            M1, M2 = 10000, 10000
            model += M1 * y + M2 * z + lpSum([
                x[(i, j)] * tur_info[tur_info['IsEmri'] == j]['UrunAdedi'].values[0]
                for i in active_ops
                for j in job_ids
            ])
            
            # Kısıtlar
            for j in job_ids:
                model += lpSum([x[(i, j)] for i in active_ops]) == 1
            
            total_tours = len(job_ids)
            total_desi = tur_info['UrunDesi'].sum()
            num_ops = len(active_ops)
            
            avg_tours = total_tours / num_ops
            avg_desi = total_desi / num_ops
            
            for i in active_ops:
                model += lpSum([x[(i, j)] for j in job_ids]) >= avg_tours - z
                model += lpSum([x[(i, j)] for j in job_ids]) <= avg_tours + z
                
                model += lpSum([
                    x[(i, j)] * tur_info[tur_info['IsEmri'] == j]['UrunDesi'].values[0]
                    for j in job_ids
                ]) >= avg_desi - y
                model += lpSum([
                    x[(i, j)] * tur_info[tur_info['IsEmri'] == j]['UrunDesi'].values[0]
                    for j in job_ids
                ]) <= avg_desi + y
            
            model += z <= 0.53 * y
            
            # ✅ GLPK solver kullan (Mac uyumlu)
            try:
                solver = GLPK(msg=0)
                model.solve(solver)
            except:
                # GLPK yoksa default solver
                model.solve()
            
            # Sonuç kontrolü
            if LpStatus[model.status] == 'Optimal':
                assignments = []
                for i in active_ops:
                    for j in job_ids:
                        if x[(i, j)].varValue == 1:
                            job_data = tur_info[tur_info['IsEmri'] == j].iloc[0]
                            assignments.append({
                                'Operator': i,
                                'IsEmri': j,
                                'UrunDesi': job_data['UrunDesi'],
                                'UrunAdedi': job_data['UrunAdedi']
                            })
                
                return pd.DataFrame(assignments), "OPTIMIZATION"
            else:
                return None, "OPTIMIZATION_NO_SOLUTION"
        
        except Exception as e:
            print(f"Optimizasyon hatası: {e}")
            return None, "OPTIMIZATION_ERROR"
        
    def heuristic(self,
                  tur_info: pd.DataFrame,
                  operators: pd.DataFrame,
                  operator_status: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Sezgisel (greedy) algoritma ile atama yapar.
        
        Strateji: İş emirlerini hacim/adet oranına göre sırala,
                 operatörlere round-robin şekilde dağıt.
        """
        try:
            # Sadece aktif operatörler
            active_ops = operator_status[operator_status['Status'] == 'active']
            operator_list = active_ops['Operator'].tolist()
            
            if len(operator_list) == 0:
                return None, "NO_OPERATORS"
            
            # İş emirlerini hacim/adet oranına göre sırala (büyükten küçüğe)
            tur_info_sorted = tur_info.copy()
            tur_info_sorted['ratio'] = tur_info_sorted['UrunDesi'] / tur_info_sorted['UrunAdedi']
            tur_info_sorted = tur_info_sorted.sort_values('ratio', ascending=False)
            
            # Round-robin atama
            assignments = []
            for idx, row in tur_info_sorted.iterrows():
                operator_idx = idx % len(operator_list)
                selected_operator = operator_list[operator_idx]
                
                assignments.append({
                    'Operator': selected_operator,
                    'IsEmri': row['IsEmri'],
                    'UrunDesi': row['UrunDesi'],
                    'UrunAdedi': row['UrunAdedi']
                })
            
            return pd.DataFrame(assignments), "HEURISTIC"
            
        except Exception as e:
            print(f"Sezgisel algoritma hatası: {e}")
            return None, "HEURISTIC_ERROR"
    
    def assign(self,
               tur_info: pd.DataFrame,
               operators: pd.DataFrame,
               operator_status: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        """
        Önce optimizasyon, başarısız olursa sezgisel yöntem ile atama yapar.
        
        Returns:
            (atamalar, method): Atama sonuçları ve kullanılan method
        """
        # Önce optimizasyon dene
        result, method = self.optimize(tur_info, operators, operator_status)
        
        if result is not None:
            print(f"✅ Optimizasyon başarılı!")
            return result, method
        
        # Optimizasyon başarısız, sezgisel yönteme geç
        print(f"⚠️  Optimizasyon başarısız ({method}), sezgisel yönteme geçiliyor...")
        result, method = self.heuristic(tur_info, operators, operator_status)
        
        if result is not None:
            print(f"✅ Sezgisel atama başarılı!")
            return result, method
        
        raise Exception("Hem optimizasyon hem sezgisel yöntem başarısız!")


if __name__ == "__main__":
    # Test
    from data.warehouse_data import get_warehouse_data
    
    tur_info, operators, operator_status = get_warehouse_data()
    
    optimizer = AssignmentOptimizer()
    assignments, method = optimizer.assign(tur_info, operators, operator_status)
    
    print(f"\nKullanılan Yöntem: {method}")
    print(f"\nİlk 10 Atama:")
    print(assignments.head(10))
    
    # Özet
    summary = assignments.groupby('Operator').agg({
        'IsEmri': 'count',
        'UrunDesi': 'sum',
        'UrunAdedi': 'sum'
    }).rename(columns={'IsEmri': 'TurSayisi'})
    
    print(f"\nOperatör Başına Özet:")
    print(summary)