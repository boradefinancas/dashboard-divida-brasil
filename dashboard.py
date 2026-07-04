import os
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ===== 1. BUSCAR DADOS NO BANCO CENTRAL =====
def buscar_serie(codigo, data_ini='01/01/2006'):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={data_ini}'
    resp = requests.get(url)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    return df.set_index('data').sort_index()

# DLSP (% PIB) - série 4513
dlsp = buscar_serie(4513)

# DBGG (% PIB) - séries 4537 (até 2007) e 13762 (de 2008 em diante)
dbgg_antiga = buscar_serie(4537, data_ini='01/01/2006')
dbgg_antiga = dbgg_antiga[dbgg_antiga.index <= '2007-12-31']
dbgg_nova = buscar_serie(13762, data_ini='01/01/2008')
dbgg = pd.concat([dbgg_antiga, dbgg_nova]).sort_index()

# ===== 2. MONTAR O GRÁFICO =====
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dlsp.index, y=dlsp['valor'],
    name='DLSP (% PIB)', mode='lines',
    line=dict(color='#c0392b', width=2.5)
))

fig.add_trace(go.Scatter(
    x=dbgg.index, y=dbgg['valor'],
    name='DBGG (% PIB)', mode='lines',
    line=dict(color='#2980b9', width=2.5)
))

fig.update_layout(
    title=f'Dívida Pública Brasileira (% do PIB) — Atualizado em {datetime.now().strftime("%d/%m/%Y")}',
    xaxis_title='Ano', yaxis_title='% do PIB',
    template='plotly_white',
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    height=550
)

grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

# ===== 3. MONTAR O HTML FINAL =====
html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Dívida Pública Brasileira</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; }}
  .container {{ max-width: 1100px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
  h1 {{ color: #2c3e50; text-align: center; margin-bottom: 5px; }}
  .sub {{ text-align: center; color: #7f8c8d; margin-bottom: 30px; font-size: 14px; }}
  .fonte {{ text-align: center; color: #95a5a6; font-size: 12px; margin-top: 20px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Dívida Pública Brasileira</h1>
  <p class="sub">Evolução da Dívida Líquida e Bruta em relação ao PIB</p>
  {grafico_html}
  <p class="fonte">Fonte: Banco Central do Brasil — SGS | Gerado automaticamente via GitHub Actions</p>
</div>
</body>
</html>'''

# ===== 4. SALVAR O ARQUIVO =====
os.makedirs('public', exist_ok=True)
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Dashboard gerado com sucesso!')
