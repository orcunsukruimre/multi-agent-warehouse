"""
Multi-Agent Warehouse Decision Support System
Streamlit Web Interface - English Version
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Set Matplotlib backend first (required for Streamlit Cloud)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Set path
sys.path.append(str(Path(__file__).parent))

from agents.assignment_agent import AssignmentAgent
from data.warehouse_data import get_warehouse_data

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Warehouse Decision Support System",
    page_icon="🏭",
    layout="wide"
)

# CSS - Minimal design
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
st.markdown('<div class="main-title">🤖 Intelligent Task Assignment with Agentic AI</div>', unsafe_allow_html=True)
st.markdown("---")

# Load data
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
# STEP 1: AUTOMATIC SUMMARY
# ============================================
st.markdown('<div class="step-header">📊 STEP 1: CURRENT STATUS SUMMARY</div>', unsafe_allow_html=True)

if st.session_state.intro_summary is None:
    with st.spinner("🤖 GPT-4 generating summary..."):
        agent = AssignmentAgent()
        intro_summary = agent._generate_intro_summary(
            total_orders, total_items, total_volume,
            total_operators, active_operators_count,
            on_leave, sick_leave
        )
        st.session_state.intro_summary = intro_summary

# Metrics - DYNAMIC
col1, col2, col3, col4 = st.columns(4)

# If assignments have been made, show assigned values
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
    st.metric("📦 Work Orders", f"{assigned_count}/{total_orders}", "tours")
    st.progress(tour_progress / 100)
    st.caption(f"Assigned: {tour_progress:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📦 Total Products", f"{assigned_items:,}/{total_items:,}", "items")
    st.progress(item_progress / 100)
    st.caption(f"Assigned: {item_progress:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📊 Total Volume", f"{assigned_volume:,}/{total_volume:,}", "desi")
    st.progress(volume_progress / 100)
    st.caption(f"Assigned: {volume_progress:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("👷 Active Operators", f"{assigned_operators}/{total_operators}", "people")
    st.progress(operator_progress / 100)
    st.caption(f"Active: {operator_progress:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
# LLM Summary
st.markdown("### 💬 LLM Analysis")
st.info(st.session_state.intro_summary)

# ============================================
# STEP 2: START ASSIGNMENT
# ============================================
st.markdown('<div class="step-header">🔧 STEP 2: ASSIGNMENT PROCESS</div>', unsafe_allow_html=True)

if st.session_state.step == 1:
    if st.button("▶️ START ASSIGNMENT", type="primary", use_container_width=True):
        with st.spinner("⚙️ Assigning work orders..."):
            agent = AssignmentAgent()
            optimizer = agent.optimizer
            
            # Initial assignment
            assignments, method = optimizer.assign(tur_info, operators, operator_status)
            assigned_count = len(assignments['IsEmri'].unique())
            
            # Compliance check
            compliance_result = agent._check_compliance(assignments)
            
            # Save to session
            st.session_state.assignments = assignments
            st.session_state.compliance_result = compliance_result
            st.session_state.method = method
            st.session_state.assigned_count = assigned_count
            st.session_state.initial_active_count = active_operators_count
            st.session_state.step = 2
            
            st.rerun()

# ============================================
# STEP 3: COMPLIANCE + DECISION
# ============================================
if st.session_state.step >= 2:
    compliance_result = st.session_state.compliance_result
    assignments = st.session_state.assignments
    assigned_count = st.session_state.assigned_count
    
    st.success(f"✅ Initial assignment completed: {assigned_count}/{total_orders} work orders")
    
    st.markdown('<div class="step-header">⚖️ STEP 3: COMPLIANCE ASSESSMENT</div>', unsafe_allow_html=True)
    
    if compliance_result['overall_compliant']:
        # COMPLIANT - Go directly to results
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success("✅ **COMPLIANT** - All assignments are within legal limits!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.step = 3
    
    else:
        # NON-COMPLIANT - Request decision
        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.error("❌ **NON-COMPLIANT** - Legal limit violations detected!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚠️ Risk Level", compliance_result['risk_level'])
        
        with col2:
            st.metric("🚨 Total Violations", compliance_result['total_violations'])
        
        # Warnings
        if compliance_result['warnings']:
            st.markdown("**⚠️ Details:**")
            for warning in compliance_result['warnings'][:3]:
                st.warning(warning)
        
        st.markdown("---")
        
        # Human-in-the-Loop
        st.markdown('<div class="step-header">👤 STEP 4: YOUR DECISION</div>', unsafe_allow_html=True)
        
        # System analysis
        required_ops = (total_orders / 10) + 0.5
        avg_tours = total_orders / active_operators_count
        
        st.info(f"""
        **💡 System Analysis:**
        - Total Work Orders: **{total_orders} tours**
        - Current Operators: **{active_operators_count} people**
        - Average Tours/Operator: **{avg_tours:.1f} tours** ⚠️ (Limit: 10 tours)
        - Recommended Operators: **~{int(required_ops)} people**
        """)
        
        st.markdown("### 🎯 Your Options:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **A) Hire +1 Operator**
            - ✅ All work completed
            - ✅ Legal compliance achieved
            - 💰 Cost: ~$20-25
            """)
            if st.button("A) HIRE ADDITIONAL OPERATOR", use_container_width=True, key="choice_a", type="primary"):
                st.session_state.choice = "A"
                st.rerun()
        
        with col2:
            st.markdown("""
            **B) Reduce Workload**
            - ⚠️ Some work postponed
            - ✅ Cost savings
            - 💰 Cost: $0
            """)
            if st.button("B) REDUCE WORKLOAD", use_container_width=True, key="choice_b"):
                st.session_state.choice = "B"
                st.rerun()
        
        # Process decision
        if 'choice' in st.session_state and st.session_state.choice:
            with st.spinner("⚙️ Processing..."):
                agent = AssignmentAgent()
                optimizer = agent.optimizer
                
                if st.session_state.choice == "A":
                    # ADD OPERATOR
                    inactive_ops = operator_status[operator_status['Status'] != 'active']
                    
                    if len(inactive_ops) > 0:
                        idx = inactive_ops.index[0]
                        operator_status.loc[idx, 'Status'] = 'active'
                        operator_status.loc[idx, 'WeeklyHours'] = 40
                        
                        st.session_state.operator_status = operator_status
                        
                        initial_active = st.session_state.initial_active_count
                        new_active = len(operator_status[operator_status['Status'] == 'active'])
                        
                        # Reassign
                        assignments, method = optimizer.assign(tur_info, operators, operator_status)
                        assigned_count = len(assignments['IsEmri'].unique())
                        compliance_result = agent._check_compliance(assignments)
                        
                        st.session_state.assignments = assignments
                        st.session_state.compliance_result = compliance_result
                        st.session_state.assigned_count = assigned_count
                        st.session_state.decision_text = f"1 additional operator hired ({initial_active} → {new_active} operators)"
                        st.session_state.step = 3
                        
                        del st.session_state.choice
                        st.rerun()
                
                else:  # Option B
                    # REDUCE WORKLOAD
                    max_orders = active_operators_count * 10
                    tur_info_reduced = tur_info.head(max_orders)
                    
                    assignments, method = optimizer.assign(tur_info_reduced, operators, operator_status)
                    assigned_count = len(assignments['IsEmri'].unique())
                    compliance_result = agent._check_compliance(assignments)
                    
                    st.session_state.assignments = assignments
                    st.session_state.compliance_result = compliance_result
                    st.session_state.assigned_count = assigned_count
                    st.session_state.decision_text = f"{total_orders - assigned_count} work orders postponed"
                    st.session_state.step = 3
                    
                    del st.session_state.choice
                    st.rerun()

# ============================================
# STEP 5: RESULTS
# ============================================
if st.session_state.step == 3:
    st.markdown('<div class="step-header">✅ STEP 5: RESULTS</div>', unsafe_allow_html=True)
    
    assignments = st.session_state.assignments
    compliance_result = st.session_state.compliance_result
    assigned_count = st.session_state.assigned_count
    
    # Decision text
    if 'decision_text' in st.session_state:
        st.success(f"✅ {st.session_state.decision_text}")
    
    # LLM Final Summary
    if st.session_state.final_summary is None:
        with st.spinner("🤖 GPT-4 generating final summary..."):
            agent = AssignmentAgent()
            
            operator_summary = assignments.groupby('Operator').agg({
                'IsEmri': 'count',
                'UrunAdedi': 'sum',
                'UrunDesi': 'sum'
            }).rename(columns={'IsEmri': 'TurSayisi'})
            
            final_total_items = assignments['UrunAdedi'].sum()
            final_total_volume = assignments['UrunDesi'].sum()
            final_active = len(operator_status[operator_status['Status'] == 'active'])
            
            decision_explanation = st.session_state.get('decision_text', 'Assignments completed.')
            
            final_summary = agent._generate_result_summary(
                total_orders, total_items, st.session_state.initial_active_count,
                decision_explanation, assigned_count, final_active,
                final_total_items, final_total_volume, compliance_result
            )
            
            st.session_state.final_summary = final_summary
    
    st.markdown("### 💬 LLM Final Summary")
    st.info(st.session_state.final_summary)
    
    st.markdown("---")
    
    # Operator Table
    st.markdown("### 📋 Per-Operator Assignments")
    
    operator_summary = assignments.groupby('Operator').agg({
        'IsEmri': 'count',
        'UrunAdedi': 'sum',
        'UrunDesi': 'sum'
    }).rename(columns={
        'IsEmri': 'Tour Count',
        'UrunAdedi': 'Total Products',
        'UrunDesi': 'Total Volume (desi)'
    })
    
    st.dataframe(operator_summary, use_container_width=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown("### 📈 Visualization")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('white')
    
    operators_list = operator_summary.index.tolist()
    tours = operator_summary['Tour Count'].tolist()
    items = operator_summary['Total Products'].tolist()
    volumes = operator_summary['Total Volume (desi)'].tolist()
    
    # Chart 1: Tour Count
    ax1.bar(operators_list, tours, color='#1f77b4', alpha=0.8)
    ax1.axhline(y=10, color='red', linestyle='--', label='Limit: 10 tours')
    ax1.set_xlabel('Operator', fontsize=11)
    ax1.set_ylabel('Tour Count', fontsize=11)
    ax1.set_title('Tours per Operator', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Chart 2: Product Count
    ax2.bar(operators_list, items, color='#2ca02c', alpha=0.8)
    ax2.set_xlabel('Operator', fontsize=11)
    ax2.set_ylabel('Product Count', fontsize=11)
    ax2.set_title('Products per Operator', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Chart 3: Volume (Desi)
    ax3.bar(operators_list, volumes, color='#ff7f0e', alpha=0.8)
    ax3.set_xlabel('Operator', fontsize=11)
    ax3.set_ylabel('Volume (desi)', fontsize=11)
    ax3.set_title('Volume per Operator', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Chart 4: Balance (Normalized)
    max_tour = max(tours)
    normalized = [(t / max_tour) * 100 for t in tours]
    colors = ['#28a745' if n >= 80 else '#ffc107' if n >= 60 else '#dc3545' for n in normalized]
    ax4.barh(operators_list, normalized, color=colors, alpha=0.8)
    ax4.set_xlabel('Workload Balance (%)', fontsize=11)
    ax4.set_ylabel('Operator', fontsize=11)
    ax4.set_title('Workload Balance Chart', fontsize=13, fontweight='bold')
    ax4.axvline(x=80, color='green', linestyle='--', alpha=0.5, label='Balanced')
    ax4.legend()
    ax4.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    st.markdown("---")
    
    # Download Excel
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📥 Download Assignment List")
    
    with col2:
        st.download_button(
            label="📥 Download Excel",
            data=assignments.to_csv(index=False).encode('utf-8'),
            file_name=f"assignment_list_{assigned_count}tours.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Restart
    st.markdown("---")
    if st.button("🔄 Start New Assignment", use_container_width=True):
        # Clear session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()