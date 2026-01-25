"""
Depo İş Emirleri ve Operatör Verileri
Şükrü İmre'nin çalışmasından adapte edilmiştir.
"""
import pandas as pd
from typing import Tuple


def get_warehouse_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Depo iş emirleri, operatör bilgileri ve operatör durumlarını döndürür.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
            - tur_info: İş emirleri (IsEmri, UrunDesi, UrunAdedi)
            - df_operator: Operatör listesi
            - operator_status: Operatör durumları (izin, mesai saatleri vb.)
    """
    
    # İş Emirleri
    tur_list = list(range(1, 75))
    tur_desi = [
        188, 199, 164, 199, 199, 188, 188, 188, 210, 188, 188, 155, 144, 199, 210, 210, 188,
        199, 199, 199, 210, 177, 188, 199, 199, 199, 210, 210, 210, 199, 199, 188, 210, 210,
        199, 199, 188, 199, 199, 210, 188, 166, 210, 210, 210, 210, 210, 210, 199, 199, 210,
        210, 210, 199, 210, 210, 166, 188, 199, 177, 199, 177, 210, 199, 188, 188, 188, 188,
        210, 199, 199, 210, 177, 164
    ]
    miktar = [
        18, 23, 17, 33, 52, 39, 37, 29, 38, 48, 15, 6, 6, 7, 6, 13, 28, 17, 91, 128, 99, 79,
        63, 31, 40, 29, 41, 52, 57, 28, 74, 134, 156, 160, 132, 142, 154, 161, 133, 152, 77,
        71, 59, 62, 63, 81, 76, 68, 60, 96, 68, 24, 56, 89, 51, 104, 57, 118, 67, 82, 91, 72,
        109, 66, 82, 120, 45, 120, 39, 63, 81, 120, 69, 103
    ]
    
    tur_info = pd.DataFrame({
        'IsEmri': tur_list,
        'UrunDesi': tur_desi,
        'UrunAdedi': miktar
    })
    
    # Operatör Listesi (8 operatör)
    operator_list = list(range(1, 9))
    df_operator = pd.DataFrame({
        'Operator': operator_list,
        'Name': [f'Operatör_{i}' for i in operator_list]
    })
    
    # Operatör Durumları (İzin, haftalık mesai saatleri, vb.)
    operator_status = pd.DataFrame({
        'Operator': operator_list,
        'Status': ['active', 'active', 'on_leave', 'active', 'active', 'sick_leave', 'active', 'active'],
        'WeeklyHours': [42, 38, 0, 40, 43, 0, 35, 41],
        'Shift': ['morning', 'morning', 'morning', 'morning', 'afternoon', 'afternoon', 'afternoon', 'afternoon'],
        'Experience': ['senior', 'junior', 'mid', 'senior', 'mid', 'junior', 'senior', 'mid']
    })
    
    return tur_info, df_operator, operator_status


if __name__ == "__main__":
    # Test
    tur_info, operators, status = get_warehouse_data()
    print("📦 İş Emirleri:")
    print(tur_info.head())
    print(f"\nToplam: {len(tur_info)} iş emri")
    print(f"Toplam Ürün: {tur_info['UrunAdedi'].sum()}")
    print(f"Toplam Hacim: {tur_info['UrunDesi'].sum()}")