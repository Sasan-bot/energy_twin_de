import matplotlib.pyplot as plt
import numpy as np

def show_professional_dashboard(analysis):
    """
    UI/UX Layer: Strategic Decision Support System v2.0
    Combines technical precision with financial transparency.
    """
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 12)) # Slightly taller to fit the Roadmap
    
    fig.suptitle(f"SOLAR STRATEGY REPORT: ENERGY-TWIN 2026\nSystem Capacity: {analysis['capacity_kwp']:.1f} kWp", 
                 fontsize=22, fontweight='bold', color='#00FFCC', y=0.98)

    # --- 1. Energy Flow (Donut Chart) ---
    ax1 = plt.subplot2grid((3, 3), (0, 0))
    sc_rate = analysis['no_battery']['sc_rate']
    ax1.pie([sc_rate, 100 - sc_rate], labels=['Used', 'Export'], colors=['#00FFCC', '#333333'], 
            autopct='%1.0f%%', startangle=90, pctdistance=0.75, textprops={'color':"w", 'weight':'bold'})
    ax1.add_artist(plt.Circle((0,0), 0.70, fc='#000000'))
    ax1.set_title(f"Self-Consumption: {sc_rate:.1f}%", pad=15)

    # --- 2. Financial Strategy (Bar Chart) ---
    ax2 = plt.subplot2grid((3, 3), (0, 1), colspan=2)
    scenarios = ['Standard', 'With Battery']
    paybacks = [analysis['no_battery']['payback'], analysis['with_battery']['payback']]
    invests = [analysis['no_battery']['invest'], analysis['with_battery']['invest']]
    bars = ax2.bar(scenarios, paybacks, color=['#555555', '#00FFCC'], alpha=0.8, width=0.4)
    ax2.set_ylabel("Years to ROI")
    ax2.set_ylim(0, max(paybacks) * 1.4) 
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.6, 
                 f"{yval:.1f} Yrs\n({invests[i]:,.0f} €)", ha='center', color='w', fontweight='bold')

    # --- 3. Eco & Hardware Box ---
    ax3 = plt.subplot2grid((3, 3), (1, 0))
    ax3.axis('off')
    trees = int(analysis['co2_saved'] * 80) 
    info_text = (f"🌿 ECO IMPACT\n\nCO2 Saved: {analysis['co2_saved']:.2f} T/Y\n"
                 f"Trees: {trees} 🌳\n-------------------\n"
                 f"Panels: {analysis['num_panels']}\nYield: {analysis['yield']:,.0f} kWh/Y")
    ax3.text(0.5, 0.5, info_text, transform=ax3.transAxes, fontsize=12, ha='center', va='center',
             bbox=dict(boxstyle='round,pad=1.5', facecolor='#0A2A12', edgecolor='#00FFCC', lw=2))

    # --- 4. Mobility Sector (Free EV Range) ---
    ax4 = plt.subplot2grid((3, 3), (1, 1))
    ax4.axis('off')
    ev_km = (analysis['yield'] * (sc_rate/100)) / 0.15 
    mobility_text = (f"🚗 SOLAR MOBILITY\n\nFree EV Range:\n{ev_km:,.0f} KM / Year\n"
                     f"Fuel Saved: ~{(ev_km/100)*1.8:.0f} €")
    ax4.text(0.5, 0.5, mobility_text, transform=ax4.transAxes, fontsize=12, ha='center', va='center',
             bbox=dict(boxstyle='round,pad=1.5', facecolor='#111111', edgecolor='#FFCC00', lw=2))

    # --- 5. Project Scorecard (Radar) ---
    ax5 = fig.add_subplot(3, 3, 6, polar=True)
    labels = ['Yield', 'ROI', 'Eco']
    values = [85, 70, 92] # Example scores
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]; angles += angles[:1]
    ax5.plot(angles, values, color='#00FFCC'); ax5.fill(angles, values, alpha=0.3)
    ax5.set_xticks(angles[:-1]); ax5.set_xticklabels(labels, size=8)

    # --- 6. ACQUISITION ROADMAP (The "Closer") ---
    ax6 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
    ax6.axis('off')
    invest = analysis['no_battery']['invest']
    monthly_gain = analysis['no_battery']['savings'] / 12
    loan_pmt = (invest * 1.25) / 120 
    roadmap = (f"--- STRATEGIC PURCHASE OPTIONS ---\n"
               f"CASH BUY: {invest:,.0f} € upfront | Gain: +{monthly_gain:.0f} €/mo\n"
               f"SMART LOAN: 0 € upfront | Payment: ~{loan_pmt:.0f} €/mo | Solar Income: ~{monthly_gain:.0f} €/mo\n"
               f">> AI VERDICT: Solar income covers { (monthly_gain/loan_pmt)*100 :.0f}% of your loan!")
    ax6.text(0.5, 0.5, roadmap, transform=ax6.transAxes, fontsize=13, ha='center', va='center',
             color='#00FFCC', fontweight='bold', bbox=dict(boxstyle='round,pad=1', facecolor='#111111'))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()