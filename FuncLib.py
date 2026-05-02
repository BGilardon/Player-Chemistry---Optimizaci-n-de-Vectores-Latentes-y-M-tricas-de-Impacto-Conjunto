from IPython.display import display, HTML
import pandas as pd
import numpy as np

def Matches_Teams_Players(df):
    #Cantidad de equipos
    print("Teams : \t", len(df["TeamName"].unique()))
    
    #Cantidad de jugadores
    print("Players : \t", len(df["jugador"].unique()))
    
    #Cantidad de partidos
    print("Matches : \t",len(df["matchId"].unique()))
    print("Matches : \t",len((df['TeamName'].astype(str) + ' - ' + df['TeamRival'].astype(str)).unique()))


# Eventos por event_name con descripcion
descripciones = {
    'Pass': 'Pase a un compañero',
    'BallTouch': 'Toque de balón sin pase',
    'BallRecovery': 'Recuperación del balón',
    'Clearance': 'Despeje',
    'BlockedPass': 'Pase bloqueado por rival',
    'Foul': 'Falta cometida',
    'Aerial': 'Duelo aéreo',
    'Claim': 'Arquero atrapa el balón',
    'KeeperPickup': 'Arquero recoge con las manos',
    'TakeOn': 'Intento de gambeta',
    'Tackle': 'Entrada/tackle al rival',
    'OffsideGiven': 'Offside cobrado',
    'Dispossessed': 'Jugador pierde el balón',
    'OffsidePass': 'Pase en posición de offside',
    'OffsideProvoked': 'Offside provocado al rival',
    'SavedShot': 'Tiro al arco atajado',
    'Save': 'Atajada del arquero',
    'ShieldBallOpp': 'Jugador protege el balón del rival',
    'MissedShots': 'Tiro desviado o al palo',
    'Card': 'Tarjeta amarilla o roja',
    'Punch': 'Arquero rechaza de puño',
    'Goal': 'Gol',
    'ChanceMissed': 'Chance de gol desperdiciada',
    'KeeperSweeper': 'Arquero sale a cortar',
    'Interception': 'Intercepción del balón',
    'SubstitutionOff': 'Jugador sale del partido',
    'SubstitutionOn': 'Jugador entra al partido',
    'FormationSet': 'Formación inicial registrada',
    'FormationChange': 'Cambio de formación',
    'Start': 'Inicio de período',
    'End': 'Fin de período',
    'Error': 'Error del jugador que genera chance rival',
    'ShotOnPost': 'Tiro que pega en el palo',
    'PenaltyFaced': 'Penal que enfrenta el arquero',
    'Smother': 'Arquero cierra el ángulo y tapa',
    'GoodSkill': 'Habilidad técnica destacada',
    'CrossNotClaimed': 'Centro no atrapado por el arquero',
}

def eventos_por_tipo(df):
    total = df.groupby('event_name').size().reset_index(name='count')
    exitosos = df[df['outcome_type'] == 'Successful'].groupby('event_name').size().reset_index(name='exitosos')
    
    resultado = total.merge(exitosos, on='event_name', how='left')
    resultado['exitosos'] = resultado['exitosos'].fillna(0)
    resultado['pct_exitoso'] = (resultado['exitosos'] / resultado['count'] * 100).round(1)
    resultado['descripcion'] = resultado['event_name'].map(descripciones)
    
    return resultado.drop(columns='exitosos').sort_values('count', ascending=False)

from IPython.display import display, HTML


def analisis_evento(df, event_name, dplay = True):    
    subset = df[df['event_name'] == event_name]
    n = len(subset)
    serie = {}

    Col_Count = ["jugador", "position", "receiver_position", "receiver_playerName", "previous_event",
                "next_event_posesion", "period_id"]

    Col_num = ["minute", "x", "y", "endX", "endY", "time_since_previous_action", "xG_corr", 
            "xGoT_corr", "xA", "xT", "goalMouthZ", "goalMouthY", ]  
    
    def _cat_block(subset, cols):
        html = ""
        for col in cols:
            nans = subset[col].isna().sum()
            top  = subset[col].value_counts().head(5)
            top_df = top.reset_index()
            top_df.columns = [col, 'count']
            html += f"<b>{col}</b> — NaN: {nans:,}<br>" + top_df.to_html(index=False) + "<br>"
        return html


    # --- Numéricas ---
    col_num_pres = [c for c in Col_num if c in subset.columns]
    num_html = ""
    if col_num_pres:
        stats = subset[col_num_pres].agg(['mean', 'std']).T.round(3)
        stats.columns = ['Media', 'Desvio std']
        for col in col_num_pres:
            serie[f'{col}_mean'] = stats.loc[col, 'Media']
            serie[f'{col}_std']  = stats.loc[col, 'Desvio std']
        num_html = stats.to_html()

    # --- Outcome (solo outcome_type) ---
    outcome_html = ""
    if 'outcome_type' in subset.columns:
        nans = subset['outcome_type'].isna().sum()
        vc   = subset['outcome_type'].value_counts()
        out  = pd.DataFrame({'count': vc, '%': (vc / n * 100).round(1)}).head(5)
        for val, row in out.iterrows():
            serie[f'outcome_type_{val}_pct'] = row['%']
        outcome_html = f"<br><b>outcome_type</b> — NaN: {nans:,}<br>" + out.to_html()

    # --- Categóricas divididas en 2 ---
    col_count_pres = [c for c in Col_Count if c in subset.columns]
    for col in col_count_pres:
        nans = subset[col].isna().sum()
        top  = subset[col].value_counts()
        serie[f'{col}_nan'] = nans
        if len(top) > 0:
            serie[f'{col}_top1']       = top.index[0]
            serie[f'{col}_top1_count'] = top.iloc[0]

    mid = len(col_count_pres) // 2 + len(col_count_pres) % 2
    cat_html_1 = _cat_block(subset, col_count_pres[:mid])
    cat_html_2 = _cat_block(subset, col_count_pres[mid:])

    # --- Layout HTML ---
    if dplay:
        html = f"""
        <h3>{event_name} &mdash; {n:,} eventos</h3>
        <table width="100%" style="border-collapse:collapse"><tr>
            <td valign="top" width="25%" style="padding-right:20px">
                <b>Numéricas</b><br>{num_html}{outcome_html}
            </td>
            <td valign="top" width="37%" style="padding-right:20px">
                <b>Categóricas (1/2)</b><br>{cat_html_1}
            </td>
            <td valign="top" width="38%">
                <b>Categóricas (2/2)</b><br>{cat_html_2}
            </td>
        </tr></table>
        """
        display(HTML(html))

    return pd.Series(serie, name=event_name)