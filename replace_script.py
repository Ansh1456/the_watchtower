import os
import glob
import re

template_dir = r"d:\1 Coding\intern\the_watchtower\templates"
files = glob.glob(os.path.join(template_dir, "*.html"))

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Base name changes
    content = content.replace("The Watchtower", "Watchtower")
    content = content.replace("Watchtower", "The Watchtower")
    
    # Capitalize branding in titles 
    # (Since some blocks say `Watchtower — The Watchtower`, they become `The Watchtower — The Watchtower`)

    # Apply glassmorphism classes to common containers
    # From: bg-wt-card border border-wt-border
    # To: glass-panel hover-card
    content = re.sub(r'bg-wt-card\s+border\s+border-wt-border(?!\s*px-3)', 'glass-panel hover-card', content)
    content = content.replace('bg-wt-surface/60', 'bg-wt-glass')
    content = content.replace('bg-wt-surface', 'glass-panel')
    content = content.replace('bg-wt-card', 'glass-panel')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Replacement complete.")
