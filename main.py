"""
Multi-Agent Warehouse Decision Support System
Ana Çalıştırma Dosyası
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from agents.assignment_agent import AssignmentAgent
from agents.inventory_agent import InventoryAgent
from agents.workforce_agent import WorkforceAgent
from agents.compliance_agent import ComplianceAgent


def print_banner():
    """Başlangıç banner'ı"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         MULTI-AGENT WAREHOUSE DECISION SUPPORT SYSTEM               ║
║                                                                      ║
║              🤖 Agentic AI - GPT-4 Powered                          ║
║              📊 Intelligent Assignment & Compliance                 ║
║              👤 Human-in-the-Loop Decision Making                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def show_menu():
    """Ana menü - Sadeleştirilmiş"""
    menu = """
═══════════════════════════════════════════════════════════════════════
                            ANA MENÜ
═══════════════════════════════════════════════════════════════════════

[1] 🤖 Agentic AI - Akıllı Atama Sistemi
    └─ LLM destekli otomatik atama, uyumluluk ve karar destek
    
[2] 📊 Detaylı Analiz Raporları
    └─ İş yükü, işgücü, uyumluluk analizleri (salt okunur)
    
[3] 📝 Geçmiş Atamaları Görüntüle
    └─ Önceki atama kayıtlarını incele
    
[0] ❌ Çıkış

═══════════════════════════════════════════════════════════════════════
"""
    print(menu)
    return input("Seçiminiz (1/2/3/0): ").strip()


def run_agentic_ai():
    """🤖 AGENTIC AI - Akıllı Atama Sistemi"""
    print("\n" + "=" * 70)
    print("🤖 AGENTIC AI MODU")
    print("=" * 70)
    print("\nBu sistem:")
    print("  ✅ İş yükü ve işgücü durumunu LLM ile analiz eder")
    print("  ✅ Otomatik atama yapar (Optimizasyon → Sezgisel)")
    print("  ✅ Yasal uyumluluğu kontrol eder")
    print("  ✅ Gerektiğinde size karar sorgusu yapar")
    print("  ✅ Sonuçları LLM ile özetler")
    print("  ✅ Excel raporu ve grafikler oluşturur\n")
    
    confirm = input("Başlatılsın mı? (E/H): ").strip().upper()
    
    if confirm != 'E':
        print("\n❌ İşlem iptal edildi.")
        return
    
    try:
        agent = AssignmentAgent()
        result = agent.run_full_assignment()
        
        if result['success']:
            print("\n" + "=" * 70)
            print("📊 İŞLEM ÖZETİ")
            print("=" * 70)
            print(f"\n✅ Toplam İş Emri: {result['stats']['total_orders']}")
            print(f"✅ Atanan: {result['stats']['assigned_orders']}")
            print(f"✅ Çalışan Operatör: {result['stats']['active_operators']}")
            print(f"✅ Toplam Ürün: {result['stats']['total_items']:,}")
            print(f"✅ Risk: {result['stats']['risk_level']}")
            
            if result.get('human_decision'):
                print(f"\n👤 Yönetici Kararı: {result['human_decision']}")
            
            print(f"\n💾 Çıktılar:")
            print(f"   • Excel: {Path(result['output_files']['excel']).name}")
            print(f"   • Grafikler: {len(result['charts'])} adet")
            
            # Grafikleri aç
            open_charts = input("\n📊 Grafikleri açmak ister misiniz? (E/H): ").strip().upper()
            if open_charts == 'E':
                import subprocess
                import platform
                
                for chart_path in result['charts'].values():
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', chart_path])
                    elif platform.system() == 'Windows':
                        subprocess.run(['start', chart_path], shell=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', chart_path])
                
                print("✅ Grafikler açıldı!")
            
            print("\n" + "=" * 70)
            print("✅ SÜREÇ BAŞARIYLA TAMAMLANDI!")
            print("=" * 70)
        else:
            print(f"\n❌ Hata: {result.get('error')}")
    
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n[Enter] tuşuna basarak devam edin...")


def run_analysis_mode():
    """📊 Detaylı Analiz Raporları"""
    print("\n📊 ANALİZ MODU - Detaylı Raporlar\n")
    print("=" * 70)
    
    print("\n📦 1. İŞ YÜKÜ ANALİZİ")
    print("=" * 70)
    agent1 = InventoryAgent()
    print(agent1.get_summary_text())
    
    print("\n👷 2. İŞGÜCÜ ANALİZİ")
    print("=" * 70)
    agent2 = WorkforceAgent()
    print(agent2.get_summary_text())
    
    print("\n⚖️  3. YASAL UYUMLULUK")
    print("=" * 70)
    agent3 = ComplianceAgent()
    print(agent3.get_summary_text())
    
    input("\n[Enter] tuşuna basarak devam edin...")


def view_past_assignments():
    """📝 Geçmiş Atamaları Görüntüle"""
    import pandas as pd
    
    outputs_dir = Path(__file__).parent / "outputs"
    excel_files = sorted(outputs_dir.glob("atama_raporu_*.xlsx"), 
                        key=lambda x: x.stat().st_mtime, 
                        reverse=True)
    
    if not excel_files:
        print("\n⚠️  Henüz kayıtlı atama yok.\n")
        input("[Enter] tuşuna basarak devam edin...")
        return
    
    print("\n📝 GEÇMİŞ ATAMALAR")
    print("=" * 70)
    print(f"\nToplam {len(excel_files)} atama kaydı bulundu.\n")
    
    for i, file in enumerate(excel_files[:5], 1):  # Son 5 kayıt
        print(f"{i}. {file.name}")
        
        # Genel Özet'i oku
        try:
            df = pd.read_excel(file, sheet_name='Genel Özet')
            print("   Özet:")
            for _, row in df.iterrows():
                print(f"      • {row['Metrik']}: {row['Değer']}")
            print()
        except:
            print("   (Özet okunamadı)\n")
    
    if len(excel_files) > 5:
        print(f"... ve {len(excel_files) - 5} kayıt daha\n")
    
    # En son raporu aç
    open_latest = input("En son raporu açmak ister misiniz? (E/H): ").strip().upper()
    if open_latest == 'E':
        import subprocess
        import platform
        
        latest_file = excel_files[0]
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', str(latest_file)])
        elif platform.system() == 'Windows':
            subprocess.run(['start', str(latest_file)], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', str(latest_file)])
        
        print(f"✅ {latest_file.name} açıldı!")
    
    input("\n[Enter] tuşuna basarak devam edin...")


def main():
    """Ana program döngüsü"""
    print_banner()
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            run_agentic_ai()
        elif choice == "2":
            run_analysis_mode()
        elif choice == "3":
            view_past_assignments()
        elif choice == "0":
            print("\n👋 Sistemden çıkılıyor. İyi çalışmalar!\n")
            break
        else:
            print("\n❌ Geçersiz seçim. Lütfen 1, 2, 3 veya 0 girin.\n")
            input("[Enter] tuşuna basarak devam edin...")


if __name__ == "__main__":
    main()
    """
    
  

**Kaydedin!**

---

### 3️⃣ `.gitignore` Oluştur (Güvenlik)

Ana klasöre → New File → `.gitignore`
```
# API Keys
.env
tools/llm_summarizer.py

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Outputs
outputs/*.xlsx
outputs/*.csv
outputs/*.png
logs/*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db 

  """