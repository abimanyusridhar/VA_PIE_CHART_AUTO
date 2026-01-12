import streamlit as st
import matplotlib.pyplot as plt

# --- 1. VISUAL CONFIGURATION ---
COLORS = {
    'Critical': '#C00000',  # Deep Dark Red
    'High':     '#FF0000',  # Bright Red
    'Medium':   '#FFC000',  # Amber/Yellow
    'Low':      '#92D050'   # Light Green
}
TABLE_COLORS = [COLORS['Critical'], COLORS['High'], COLORS['Medium'], COLORS['Low']]
TEXT_COLORS = ['white', 'white', 'black', 'black']

# --- 2. DATA PROCESSING FUNCTION ---
def process_pasted_data(raw_text):
    """
    Parses the pasted text to calculate totals.
    Expected format: IP Address | Crit | High | Med | Low | Info | Total
    """
    crit_sum = 0
    high_sum = 0
    med_sum = 0
    low_sum = 0
    
    if not raw_text:
        return [0, 0, 0, 0]

    lines = raw_text.strip().split('\n')
    
    for line in lines:
        parts = line.split()
        
        # We need at least 5 columns (IP + 4 Severities)
        if len(parts) < 5:
            continue
            
        try:
            # Check if index 1 is a number (Skipping headers)
            if not parts[1].isdigit():
                continue
                
            crit_sum += int(parts[1])
            high_sum += int(parts[2])
            med_sum  += int(parts[3])
            low_sum  += int(parts[4])
            
        except ValueError:
            continue 

    return [crit_sum, high_sum, med_sum, low_sum]

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="VAPT Calculator", layout="wide")

st.markdown("## 📊 VAPT Auto-Calculator & Generator")

# Create two columns for inputs
col1, col2 = st.columns([1, 2])

with col1:
    vessel_name = st.text_input("1. Vessel Name", placeholder="e.g., CORAL PEARL")

with col2:
    raw_data = st.text_area(
        "2. Paste Report Data", 
        height=150, 
        placeholder="Paste your rows here (e.g., 192.168.1.101  35  143  29  3 ...)"
    )

# --- 4. GENERATION LOGIC ---
if st.button("Calculate & Generate Dashboard", type="primary"):
    if not vessel_name:
        st.error("⚠️ Error: Please enter a Vessel Name.")
    elif not raw_data:
        st.error("⚠️ Error: Please paste the report data.")
    else:
        # Process Data
        counts = process_pasted_data(raw_data)
        labels = ['Critical', 'High', 'Medium', 'Low']

        if sum(counts) == 0:
            st.warning("⚠️ Error: No valid data found. Check your copy-paste format.")
        else:
            # --- PLOTTING ---
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            fig.suptitle(vessel_name.upper(), fontsize=20, fontweight='bold', x=0.15, y=0.95)

            # 1. PIE CHART
            wedges, texts = ax1.pie(
                counts, labels=counts, colors=TABLE_COLORS,
                startangle=90, counterclock=False,
                textprops={'fontsize': 12, 'weight': 'bold'}
            )
            ax1.set_aspect('equal')
            ax1.legend(wedges, labels, title="Severity", loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1))

            # 2. TABLE
            ax2.axis('off')
            col_labels = ['Severity', 'Count']
            cell_text = [[labels[i], counts[i]] for i in range(4)]

            the_table = ax2.table(
                cellText=cell_text, colLabels=col_labels,
                loc='center', cellLoc='center', colColours=['black', 'black']
            )

            # Table Styling
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(12)
            the_table.scale(0.8, 2.5)

            for (row, col), cell in the_table.get_celld().items():
                cell.set_edgecolor('white')
                cell.set_linewidth(2)
                if row == 0:
                    cell.set_facecolor('black')
                    cell.set_text_props(color='white', weight='bold', fontsize=14)
                else:
                    idx = row - 1
                    cell.set_facecolor(TABLE_COLORS[idx])
                    cell.set_text_props(color=TEXT_COLORS[idx], weight='bold', fontsize=13)

            # Display the plot in Streamlit
            st.pyplot(fig)
            
            # Optional: Allow user to download the image
            filename = f"{vessel_name.replace(' ', '_')}_PI_CHART.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            with open(filename, "rb") as file:
                btn = st.download_button(
                    label="📥 Download Chart Image",
                    data=file,
                    file_name=filename,
                    mime="image/png"
                )
            st.success(f"✅ Generated for {vessel_name}")