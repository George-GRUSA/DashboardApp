import streamlit as st
import datetime

st.set_page_config(layout="wide")


# Responsive Tableau Embed Script
responsive_embed_code = """
<script type="module" src="https://us-east-1.online.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js"></script>

<div id="viz-container"></div>

<script>
  function renderViz() {
    const container = document.getElementById('viz-container');
    container.innerHTML = '';  // Clear existing viz

    const width = window.innerWidth;
    const height = window.innerHeight - 100; // leave space for title and footer

    const viz = document.createElement('tableau-viz');
    viz.setAttribute('id', 'tableau-viz');
    viz.setAttribute('src', 'https://us-east-1.online.tableau.com/t/bluejeansgolf/views/RanchPassScoreboard/RichardsonDB');
    viz.setAttribute('width', width);
    viz.setAttribute('height', height);
    viz.setAttribute('hide-tabs', '');
    viz.setAttribute('toolbar', 'bottom');

    
    container.appendChild(viz);
  }

  window.addEventListener('DOMContentLoaded', renderViz);
  window.addEventListener('resize', () => {
    renderViz();
  });
</script>
"""

# Inject HTML and JavaScript
st.components.v1.html(responsive_embed_code, height=1000, scrolling=False)

# Timestamp
st.caption(f"Last refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

