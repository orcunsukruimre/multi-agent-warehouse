"""
Multi-Agent Warehouse Decision Support System
Streamlit Web Arayüzü - Yalın Tasarım
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Matplotlib backend'i önce ayarla (Streamlit Cloud için gerekli)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Path ayarla
sys.path.append(str(Path(__file__).parent))

from agents.assignment_agent import AssignmentAgent
from data.warehouse_data import get_warehouse_data

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Depo Yönetim Sistemi",
    page_icon="🏭",
    layout="wide"
)

# CSS - Minimal tasarım
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-left: 5px solid #1f77b4;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'assignments' not in st.session_state:
    st.session_state.assignments = None
if 'compliance_result' not in st.session_state:
    st.session_state.compliance_result = None
if 'operator_status' not in st.session_state:
    st.session_state.operator_status = None
if 'intro_summary' not in st.session_state:
    st.session_state.intro_summary = None
if 'final_summary' not in st.session_state:
    st.session_state.final_summary = None

# Header
st.markdown('<div class="main-title">🤖 AGENTIC AI - DEPO YÖNETİM SİSTEMİ</div>', unsafe_allow_html=True)
st.markdown("---")

# Veri yükle
tur_info, operators, operator_status_original = get_warehouse_data()

if st.session_state.operator_status is None:
    st.session_state.operator_status = operator_status_original.copy()

operator_status = st.session_state.operator_status

total_orders = len(tur_info)
total_items = tur_info['UrunAdedi'].sum()
total_volume = tur_info['UrunDesi'].sum()
total_operators = len(operators)
active_operators_count = len(operator_status[operator_status['Status'] == 'active'])
on_leave = len(operator_status[operator_status['Status'] == 'on_leave'])
sick_leave = len(operator_status[operator_status['Status'] == 'sick_leave'])

# ============================================
# ADIM 1: OTOMATIK ÖZET
# ============================================
st.markdown('<div class="step-header">📊 ADIM 1: MEVCUT DURUM ÖZETİ</div>', unsafe_allow_html=True)

if st.session_state.intro_summary is None:
    with st.spinner("🤖 GPT-4 özet üretiyor..."):
        agent = AssignmentAgent()
        intro_summary = agent._generate_intro_summary(
            total_orders, total_items, total_volume,
            total_operators, active_operators_count,
            on_leave, sick_leave
        )
        st.session_state.intro_summary = intro_summary

# Metrikler# Metrikler - DİNAMİK
col1, col2, col3, col4 = st.columns(4)

# Eğer atama yapıldıysa atanan değerleri göster
if st.session_state.assignments is not None:
    assignments = st.session_state.assignments
    assigned_count = st.session_state.assigned_count
    assigned_items = assignments['UrunAdedi'].sum()
    assigned_volume = assignments['UrunDesi'].sum()
    assigned_operators = len(assignments['Operator'].unique())
    
    tour_progress = (assigned_count / total_orders) * 100
    item_progress = (assigned_items / total_items) * 100
    volume_progress = (assigned_volume / total_volume) * 100
    operator_progress = (assigned_operators / total_operators) * 100
else:
    assigned_count = 0
    assigned_items = 0
    assigned_volume = 0
    assigned_operators = 0
    
    tour_progress = 0
    item_progress = 0
    volume_progress = 0
    operator_progress = 0

with col1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📦 İş Emri", f"{assigned_count}/{total_orders}", "tur")
    st.progress(tour_progress / 100)
    st.caption(f"Atanan: %{tour_progress:.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📦 Toplam Ürün", f"{assigned_items:,}/{total_items:,}", "adet")
    st.progress(item_progress / 100)
    st.caption(f"Atanan: %{item_progress:.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📊 Toplam Hacim", f"{assigned_volume:,}/{total_volume:,}", "desi")
    st.progress(volume_progress / 100)
    st.caption(f"Atanan: %{volume_progress:.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("👷 Çalışan Operatör", f"{assigned_operators}/{total_operators}", "kişi")
    st.progress(operator_progress / 100)
    st.caption(f"Aktif: %{operator_progress:.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
# LLM Özeti
st.markdown("### 💬 LLM Analizi")
st.info(st.session_state.intro_summary)

# ============================================
# ADIM 2: ATAMA BAŞLAT
# ============================================
st.markdown('<div class="step-header">🔧 ADIM 2: ATAMA İŞLEMİ</div>', unsafe_allow_html=True)

if st.session_state.step == 1:
    if st.button("▶️ ATAMAYI BAŞLAT", type="primary", width='stretch'):
        with st.spinner("⚙️ Atama yapılıyor..."):
            agent = AssignmentAgent()
            optimizer = agent.optimizer
            
            # İlk atama
            assignments, method = optimizer.assign(tur_info, operators, operator_status)
            assigned_count = len(assignments['IsEmri'].unique())
            
            # Uyumluluk kontrolü
            compliance_result = agent._check_compliance(assignments)
            
            # Session'a kaydet
            st.session_state.assignments = assignments
            st.session_state.compliance_result = compliance_result
            st.session_state.method = method
            st.session_state.assigned_count = assigned_count
            st.session_state.initial_active_count = active_operators_count
            st.session_state.step = 2
            
            st.rerun()

# ============================================
# ADIM 3: UYUMLULUK + KARAR
# ============================================
if st.session_state.step >= 2:
    compliance_result = st.session_state.compliance_result
    assignments = st.session_state.assignments
    assigned_count = st.session_state.assigned_count
    
    st.success(f"✅ İlk atama tamamlandı: {assigned_count}/{total_orders} iş emri")
    
    st.markdown('<div class="step-header">⚖️ ADIM 3: UYUMLULUK DEĞERLENDİRMESİ</div>', unsafe_allow_html=True)
    
    if compliance_result['overall_compliant']:
        # UYUMLU - Direkt sonuçlara geç
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success("✅ **UYUMLU** - Tüm atamalar yasal limitlere uygun!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.step = 3
    
    else:
        # UYUMSUZ - Karar iste
        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.error("❌ **UYUMSUZ** - Yasal limit aşımları tespit edildi!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚠️ Risk Seviyesi", compliance_result['risk_level'])
        
        with col2:
            st.metric("🚨 Toplam İhlal", compliance_result['total_violations'])
        
        # Uyarılar
        if compliance_result['warnings']:
            st.markdown("**⚠️ Detaylar:**")
            for warning in compliance_result['warnings'][:3]:
                st.warning(warning)
        
        st.markdown("---")
        
        # Human-in-the-Loop
        st.markdown('<div class="step-header">👤 ADIM 4: KARAR VERİN</div>', unsafe_allow_html=True)
        
        # Sistem analizi
        required_ops = (total_orders / 10) + 0.5
        avg_tours = total_orders / active_operators_count
        
        st.info(f"""
        **💡 Sistem Analizi:**
        - Toplam İş Emri: **{total_orders} tur**
        - Mevcut Operatör: **{active_operators_count} kişi**
        - Ortalama Tur/Operatör: **{avg_tours:.1f} tur** ⚠️ (Limit: 10 tur)
        - Önerilen Operatör: **~{int(required_ops)} kişi**
        """)
        
        st.markdown("### 🎯 Seçenekleriniz:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **A) +1 Ek Operatör Al**
            - ✅ Tüm işler tamamlanır
            - ✅ Yasal uyumluluk sağlanır
            - 💰 Maliyet: ~500-700 TL
            """)
            if st.button("A) EK OPERATÖR AL", width='stretch', key="choice_a", type="primary"):
                st.session_state.choice = "A"
                st.rerun()
        
        with col2:
            st.markdown("""
            **B) Ek Operatör Alma**
            - ⚠️ Bazı işler ertelenir
            - ✅ Maliyet tasarrufu
            - 💰 Maliyet: 0 TL
            """)
            if st.button("B) İŞ EMRİ AZALT", width='stretch', key="choice_b"):
                st.session_state.choice = "B"
                st.rerun()
        
        # Karar işleme
        if 'choice' in st.session_state and st.session_state.choice:
            with st.spinner("⚙️ İşleniyor..."):
                agent = AssignmentAgent()
                optimizer = agent.optimizer
                
                if st.session_state.choice == "A":
                    # EK OPERATÖR EKLE
                    inactive_ops = operator_status[operator_status['Status'] != 'active']
                    
                    if len(inactive_ops) > 0:
                        idx = inactive_ops.index[0]
                        operator_status.loc[idx, 'Status'] = 'active'
                        operator_status.loc[idx, 'WeeklyHours'] = 40
                        
                        st.session_state.operator_status = operator_status
                        
                        initial_active = st.session_state.initial_active_count
                        new_active = len(operator_status[operator_status['Status'] == 'active'])
                        
                        # Yeniden ata
                        assignments, method = optimizer.assign(tur_info, operators, operator_status)
                        assigned_count = len(assignments['IsEmri'].unique())
                        compliance_result = agent._check_compliance(assignments)
                        
                        st.session_state.assignments = assignments
                        st.session_state.compliance_result = compliance_result
                        st.session_state.assigned_count = assigned_count
                        st.session_state.decision_text = f"1 ek operatör alındı ({initial_active} → {new_active} operatör)"
                        st.session_state.step = 3
                        
                        del st.session_state.choice
                        st.rerun()
                
                else:  # B seçeneği
                    # İŞ EMRİ AZALT
                    max_orders = active_operators_count * 10
                    tur_info_reduced = tur_info.head(max_orders)
                    
                    assignments, method = optimizer.assign(tur_info_reduced, operators, operator_status)
                    assigned_count = len(assignments['IsEmri'].unique())
                    compliance_result = agent._check_compliance(assignments)
                    
                    st.session_state.assignments = assignments
                    st.session_state.compliance_result = compliance_result
                    st.session_state.assigned_count = assigned_count
                    st.session_state.decision_text = f"{total_orders - assigned_count} iş emri ertelendi"
                    st.session_state.step = 3
                    
                    del st.session_state.choice
                    st.rerun()

# ============================================
# ADIM 4: SONUÇLAR
# ============================================
if st.session_state.step == 3:
    st.markdown('<div class="step-header">✅ ADIM 5: SONUÇLAR</div>', unsafe_allow_html=True)
    
    assignments = st.session_state.assignments
    compliance_result = st.session_state.compliance_result
    assigned_count = st.session_state.assigned_count
    
    # Karar metni
    if 'decision_text' in st.session_state:
        st.success(f"✅ {st.session_state.decision_text}")
    
    # LLM Final Özeti
    if st.session_state.final_summary is None:
        with st.spinner("🤖 GPT-4 final özet üretiyor..."):
            agent = AssignmentAgent()
            
            operator_summary = assignments.groupby('Operator').agg({
                'IsEmri': 'count',
                'UrunAdedi': 'sum',
                'UrunDesi': 'sum'
            }).rename(columns={'IsEmri': 'TurSayisi'})
            
            final_total_items = assignments['UrunAdedi'].sum()
            final_total_volume = assignments['UrunDesi'].sum()
            final_active = len(operator_status[operator_status['Status'] == 'active'])
            
            decision_explanation = st.session_state.get('decision_text', 'Atamalar tamamlandı.')
            
            final_summary = agent._generate_result_summary(
                total_orders, total_items, st.session_state.initial_active_count,
                decision_explanation, assigned_count, final_active,
                final_total_items, final_total_volume, compliance_result
            )
            
            st.session_state.final_summary = final_summary
    
    st.markdown("### 💬 LLM Final Özeti")
    st.info(st.session_state.final_summary)
    
    st.markdown("---")
    
    # Operatör Tablosu
    st.markdown("### 📋 Operatör Başına Atamalar")
    
    operator_summary = assignments.groupby('Operator').agg({
        'IsEmri': 'count',
        'UrunAdedi': 'sum',
        'UrunDesi': 'sum'
    }).rename(columns={
        'IsEmri': 'Tur Sayısı',
        'UrunAdedi': 'Toplam Ürün',
        'UrunDesi': 'Toplam Hacim (desi)'
    })
    
    st.dataframe(operator_summary, width='stretch')
    
    st.markdown("---")
    
    # Grafikler
    st.markdown("### 📈 Görselleştirme")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('white')
    
    operators_list = operator_summary.index.tolist()
    tours = operator_summary['Tur Sayısı'].tolist()
    items = operator_summary['Toplam Ürün'].tolist()
    volumes = operator_summary['Toplam Hacim (desi)'].tolist()
    
    # Grafik 1: Tur Sayısı
    ax1.bar(operators_list, tours, color='#1f77b4', alpha=0.8)
    ax1.axhline(y=10, color='red', linestyle='--', label='Limit: 10 tur')
    ax1.set_xlabel('Operatör', fontsize=11)
    ax1.set_ylabel('Tur Sayısı', fontsize=11)
    ax1.set_title('Operatör Başına Tur Sayısı', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Grafik 2: Ürün Adedi
    ax2.bar(operators_list, items, color='#2ca02c', alpha=0.8)
    ax2.set_xlabel('Operatör', fontsize=11)
    ax2.set_ylabel('Ürün Adedi', fontsize=11)
    ax2.set_title('Operatör Başına Ürün Adedi', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Grafik 3: Hacim (Desi)
    ax3.bar(operators_list, volumes, color='#ff7f0e', alpha=0.8)
    ax3.set_xlabel('Operatör', fontsize=11)
    ax3.set_ylabel('Hacim (desi)', fontsize=11)
    ax3.set_title('Operatör Başına Hacim', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Grafik 4: Denge (Normalleştirilmiş)
    max_tour = max(tours)
    normalized = [(t / max_tour) * 100 for t in tours]
    colors = ['#28a745' if n >= 80 else '#ffc107' if n >= 60 else '#dc3545' for n in normalized]
    ax4.barh(operators_list, normalized, color=colors, alpha=0.8)
    ax4.set_xlabel('İş Yükü Dengesi (%)', fontsize=11)
    ax4.set_ylabel('Operatör', fontsize=11)
    ax4.set_title('İş Yükü Denge Grafiği', fontsize=13, fontweight='bold')
    ax4.axvline(x=80, color='green', linestyle='--', alpha=0.5, label='Dengeli')
    ax4.legend()
    ax4.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    st.markdown("---")
    
    # Excel İndir
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📥 Atama Listesini İndir")
    
    with col2:
        st.download_button(
            label="📥 Excel İndir",
            data=assignments.to_csv(index=False).encode('utf-8'),
            file_name=f"atama_listesi_{assigned_count}tur.csv",
            mime="text/csv",
            width='stretch'
        )
    
    # Yeniden Başlat
    st.markdown("---")
    if st.button("🔄 Yeni Atama Başlat", width='stretch'):
        # Session temizle
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()