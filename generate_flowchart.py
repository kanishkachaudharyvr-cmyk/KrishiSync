import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_flowchart():
    # Set up figure
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Draw Title block
    ax.text(50, 95, "KrishiSync — System Architecture Block Diagram", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#065f46')
    ax.text(50, 91, "Unified AI & Multilingual Agricultural ERP Platform", 
            ha='center', va='center', fontsize=10, style='italic', color='#374151')

    # Utility box drawing helper
    def draw_box(x, y, w, h, text, title, bg_color, border_color):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.5", 
                                      linewidth=1.5, edgecolor=border_color, facecolor=bg_color, mutation_scale=1)
        ax.add_patch(rect)
        # Title text
        ax.text(x + w/2, y + h - 1.5, title, ha='center', va='top', fontsize=9, fontweight='bold', color='#1f2937')
        # Body text
        ax.text(x + w/2, y + h/2 - 0.8, text, ha='center', va='center', fontsize=8, color='#4b5563', linespacing=1.3)

    # 1. Farmer Input Layer
    draw_box(10, 68, 22, 14, 
             "• Spoken Indic Audio\n• Web Dashboard Forms\n• Theme/Aesthetic Controls", 
             "1. Farmer Input Layer", 
             "#ecfdf5", "#059669")

    # 2. Sarvam AI Translation Gateway
    draw_box(42, 68, 22, 14, 
             "• WAV Audio Ingestion\n• saaras:v3 Translation\n• Direct English Mapping", 
             "2. Sarvam AI Layer", 
             "#f0f9ff", "#0284c7")

    # 3. Cognitive Core Agent Engine
    draw_box(42, 40, 22, 14, 
             "• Google Antigravity SDK\n• Multi-Turn Reasoning\n• Schema-Scoped Parsing", 
             "3. Cognitive Core", 
             "#faf5ff", "#7c3aed")

    # 4. Scoped Database / ERP Tools
    draw_box(10, 12, 22, 16, 
             "• calculate_price_estimate()\n• book_mandi_order()\n• get_order_tracking_details()", 
             "4. Scoped ERP Tools", 
             "#fffbeb", "#d97706")

    # 5. Local Database SQLite Storage
    draw_box(42, 12, 22, 16, 
             "• Farmer Accounts Table\n• MandiReference Seeding\n• MandiOrders Queue\n• InventoryItem Levels", 
             "5. Database Storage", 
             "#fbfbfe", "#4f46e5")

    # 6. Responsive Frontend UI Dashboard
    draw_box(74, 12, 20, 70, 
             "• Single-Page Layout\n• Dark/Light Themes\n• Dynamic Cursor Spotlight\n• Transit Progress Bars\n• Chart.js Price Plot\n• Web Audio Canvas Waveform", 
             "6. Dashboard UI", 
             "#fff1f2", "#e11d48")

    # Arrows connection helper
    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#4b5563", lw=1.2, shrinkA=5, shrinkB=5))
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.5, label, ha='center', va='center', fontsize=7, color='#6b7280', fontweight='semibold')

    # Connections
    draw_arrow(32, 75, 42, 75, "Audio Stream")
    draw_arrow(53, 68, 53, 54, "Translated Prompt")
    draw_arrow(42, 47, 21, 47, "Call SQLite Tool")
    draw_arrow(21, 47, 21, 28)
    draw_arrow(21, 20, 42, 20, "Read/Write SQL")
    draw_arrow(64, 20, 74, 20, "Query Data")
    draw_arrow(74, 47, 64, 47, "User Text Query")
    draw_arrow(21, 68, 74, 82, "Manual Input")

    plt.tight_layout()
    plt.savefig("krishisyncblockdiagram.pdf", bbox_inches='tight')
    plt.close()
    print("Flowchart PDF successfully generated as 'krishisyncblockdiagram.pdf'")

if __name__ == "__main__":
    draw_flowchart()
