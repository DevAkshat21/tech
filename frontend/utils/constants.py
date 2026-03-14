GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Backgrounds */
  --void:          #00030a;
  --deep:          #000d1a;
  --surface:       #001428;
  --surface2:      #002040;

  /* Borders */
  --rim:           rgba(0,180,255,0.12);
  --rim-hot:       rgba(0,210,255,0.35);

  /* Primary accent */
  --ice:           #00d4ff;
  --ice-dim:       rgba(0,212,255,0.15);
  --ice-glow:      rgba(0,212,255,0.06);

  /* AI / forecast */
  --aurora:        #7c3aed;
  --aurora-dim:    rgba(124,58,237,0.15);

  /* Anomaly warm */
  --flare:         #f59e0b;
  --flare-dim:     rgba(245,158,11,0.15);

  /* Extremes */
  --heat:          #ef4444;
  --cool:          #3b82f6;
  --life:          #10b981;

  /* Typography */
  --text-primary:   #f0f9ff;
  --text-secondary: #7eb8cc;
  --text-dim:       #2d6a7a;

  /* Fonts */
  --font-display: 'Syne', sans-serif;
  --font-body:    'Inter', sans-serif;
  --font-data:    'JetBrains Mono', monospace;
}

/* Streamlit Chrome Removal */
#MainMenu, footer, header, [data-testid="stToolbar"],
.stDeployButton, .stDecoration, div[data-testid="stStatusWidget"] { display: none !important; }

.stApp, .stAppViewContainer { background: var(--void) !important; }

.block-container {
  padding: 0 0 0 0 !important;
  max-width: 100% !important;
}

/* Also remove padding from the section containers */
section[data-testid="stMain"] > div {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb {
  background: var(--rim-hot);
  border-radius: 2px;
}

[data-baseweb="select"] {
  background: var(--surface) !important;
  border: 1px solid var(--rim) !important;
  border-radius: 12px !important;
}
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label {
  visibility: hidden;
  height: 0;
  margin: 0;
  display: none;
}

[data-testid="stSlider"] .rc-slider-track { background: var(--ice) !important; }
[data-testid="stSlider"] .rc-slider-handle {
  border-color: var(--ice) !important;
  background: var(--void) !important;
}

.stButton > button {
  background: transparent !important;
  border: 1px solid var(--rim) !important;
  color: var(--text-primary) !important;
  border-radius: 12px !important;
  font-family: var(--font-body) !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  border-color: var(--rim-hot) !important;
  background: var(--ice-glow) !important;
}

/* Section Header Pattern */
.section-header { text-align: center; padding: 60px 24px 32px; }
.eyebrow {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 12px;
}
.section-title {
  font-family: var(--font-display);
  font-size: clamp(32px, 5vw, 52px);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
  margin-bottom: 12px;
}
.section-sub {
  font-family: var(--font-body);
  font-size: 16px;
  font-weight: 300;
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Glass Card Pattern */
.glass {
  background: rgba(0,20,40,0.82);
  border: 1px solid var(--rim);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}
.glass-hot { border-color: var(--rim-hot); }
.glass:hover {
  border-color: rgba(0,210,255,0.22);
  transition: border-color 0.3s ease;
}

/* Utility classes */
.text-cyan { color: var(--ice); }
.text-purple { color: var(--aurora); }
.text-amber { color: var(--flare); }
.text-red { color: var(--heat); }
.text-blue { color: var(--cool); }
.text-green { color: var(--life); }
.font-mono { font-family: var(--font-data); }
.font-display { font-family: var(--font-display); }

/* Context Bar */
.ctx-bar {
  background: rgba(0,10,22,0.97);
  border-bottom: 1px solid var(--rim);
  padding: 10px 32px;
  display: flex; justify-content: space-between; align-items: center;
  position: sticky; top: 0; z-index: 100;
}
.ctx-pill {
  font-size: 11px; font-family: var(--font-body); font-weight: 500;
  background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2);
  color: var(--ice); padding: 4px 14px; border-radius: 20px; cursor: pointer;
}

/* Stats Row */
.stat-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 16px;
}

/* Hero Animations */
@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
@keyframes border-glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(0,212,255,0); }
  50% { box-shadow: 0 0 20px 2px rgba(0,212,255,0.15); }
}
@keyframes bounce { 
  0%, 100% { transform: translateY(0); } 
  50% { transform: translateY(4px); } 
}

/* Analogue specific */
.analogue-cards-container {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;
}

/* RCP specific */
.rcp-card {
    display: grid; grid-template-columns: 220px 1fr; gap: 24px;
    background: rgba(0,20,40,0.82); border: 1px solid var(--rim);
    border-radius: 0 16px 16px 0; padding: 24px 28px;
    margin-bottom: 20px;
}

</style>
"""

OBSERVER_JS = """
<style>
.aos {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1),
              transform 0.7s cubic-bezier(0.16,1,0.3,1);
}
.aos.visible { opacity: 1; transform: translateY(0); }
.aos-d1 { transition-delay: 0.1s; }
.aos-d2 { transition-delay: 0.2s; }
.aos-d3 { transition-delay: 0.3s; }
.aos-d4 { transition-delay: 0.4s; }
</style>
<script>
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.12 });
// Add a small delay to ensure DOM is ready
setTimeout(() => {
    document.querySelectorAll('.aos').forEach(el => obs.observe(el));
}, 500);
</script>
"""
