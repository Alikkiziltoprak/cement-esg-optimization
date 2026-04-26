import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Limak Cement ESG Dashboard', page_icon='🏭', layout='wide')

df = pd.DataFrame({'Year': [2021, 2022, 2023, 2024], 'Total_Emissions_tCO2': [8841640, 8627337, 8255695, 8203005], 'Coal_ton': [1195450, 1188875, 973952, 866871], 'Alt_Fuel_ton': [17375, 29900, 86809, 148515]})

def compute_emissions(clinker_ratio, alt_fuel_share):
    return clinker_ratio * 0.85 + (1 - alt_fuel_share) * 0.30

def compute_energy_cost(alt_fuel_share, energy_price=120):
    return (1 - alt_fuel_share) * energy_price + alt_fuel_share * (energy_price * 0.70)

def compute_total_cost(clinker_ratio, alt_fuel_share, carbon_price=65):
    energy_cost = compute_energy_cost(alt_fuel_share)
    emissions = compute_emissions(clinker_ratio, alt_fuel_share)
    carbon_cost = emissions * carbon_price
    additive_cost = (1 - clinker_ratio) * 35
    return energy_cost + carbon_cost + additive_cost

st.sidebar.title('Limak Cement')
st.sidebar.markdown('**ESG Optimization Dashboard**')
page = st.sidebar.radio('Navigation', ['Company Overview', 'Optimization Tool', 'Carbon Sensitivity'])

if page == 'Company Overview':
    st.title('Limak Cement — ESG Performance Overview')
    st.markdown('*Source: Limak Cement Sustainability Reports 2023 & 2024*')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('2021 Baseline', '8.84M ton CO2')
    col2.metric('2024 Actual', '8.20M ton CO2', delta='-7.2%', delta_color='inverse')
    col3.metric('2030 Target', '~4.3M ton CO2', delta='-51% vs 2021', delta_color='inverse')
    col4.metric('Alt Fuel Share', '12.81%', delta='+12% vs 2021')
    st.markdown('---')
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader('Total Emissions Trend (2021-2024)')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Year'], y=df['Total_Emissions_tCO2']/1e6, mode='lines+markers', name='Total Emissions', line=dict(color='red', width=3)))
        fig.add_hline(y=8.84164, line_dash='dot', line_color='gray', annotation_text='2021 Baseline')
        fig.add_hline(y=4.3, line_dash='dot', line_color='green', annotation_text='2030 Target')
        fig.update_layout(yaxis_title='Million ton CO2', height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        st.subheader('Coal vs Alternative Fuel (2021-2024)')
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df['Year'], y=df['Coal_ton']/1000, name='Coal (000 ton)', marker_color='gray'))
        fig2.add_trace(go.Bar(x=df['Year'], y=df['Alt_Fuel_ton']/1000, name='Alt Fuel (000 ton)', marker_color='green'))
        fig2.update_layout(barmode='group', yaxis_title='000 ton', height=350)
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('---')
    st.subheader('Gap Analysis — 2021 Baseline vs 2030 Target')
    col_a, col_b, col_c = st.columns(3)
    col_a.metric('Emission Gap to Close', '3.90M ton CO2')
    col_b.metric('Alt Fuel Gap', '+48.2%')
    col_c.metric('Years Remaining', '6 years')

elif page == 'Optimization Tool':
    st.title('Optimization Tool — What-If Analysis')
    st.markdown('Adjust the sliders to explore cost and emission trade-offs.')
    col_slider, col_results = st.columns([1, 2])
    with col_slider:
        st.subheader('Parameters')
        alt_fuel = st.slider('Alternative Fuel Share (%)', 5, 70, 13) / 100
        clinker  = st.slider('Clinker Ratio', 0.60, 0.85, 0.83)
        carbon_p = st.slider('Carbon Price (USD/ton CO2)', 20, 200, 65)
        st.markdown('---')
        st.subheader('Status Check')
        if clinker < 0.65:
            st.error('Clinker ratio critically low — quality risk!')
        elif clinker < 0.70:
            st.warning('Approaching quality constraint (min 0.70)')
        else:
            st.success('Clinker ratio within safe range')
        if carbon_p > 119:
            st.error('Carbon cost exceeds fuel cost — green strategy mandatory!')
        elif carbon_p > 65:
            st.warning('Carbon penalty in transitional zone')
        else:
            st.info('Carbon cost below tipping point — business as usual')
        if alt_fuel > 0.50:
            st.success('Strong decarbonization trajectory')
        elif alt_fuel > 0.25:
            st.info('Moderate transition underway')
        else:
            st.warning('Early stage — significant upside available')
    with col_results:
        baseline_cost = compute_total_cost(0.8313, 0.1281, carbon_p)
        current_cost  = compute_total_cost(clinker, alt_fuel, carbon_p)
        current_emis  = compute_emissions(clinker, alt_fuel)
        saving        = baseline_cost - current_cost
        emis_red      = (1 - current_emis / compute_emissions(0.8313, 0.1281)) * 100
        st.subheader('Results')
        m1, m2, m3, m4 = st.columns(4)
        m1.metric('Total Cost', f'${current_cost:.1f}/ton')
        m2.metric('vs Baseline', f'${saving:+.1f}/ton', delta_color='inverse')
        m3.metric('CO2/ton clinker', f'{current_emis:.3f}')
        m4.metric('Emission Reduction', f'{emis_red:.1f}%')
        st.markdown('---')
        st.subheader('Cost Breakdown')
        energy   = compute_energy_cost(alt_fuel)
        carbon   = current_emis * carbon_p
        additive = (1 - clinker) * 35
        fig3 = go.Figure(go.Waterfall(orientation='v', measure=['relative', 'relative', 'relative', 'total'], x=['Energy Cost', 'Carbon Cost', 'Additive Cost', 'Total'], y=[energy, carbon, additive, 0], increasing={'marker': {'color': 'red'}}, totals={'marker': {'color': 'steelblue'}}))
        fig3.update_layout(height=350, yaxis_title='USD/ton clinker')
        st.plotly_chart(fig3, use_container_width=True)

elif page == 'Carbon Sensitivity':
    st.title('Carbon Price Sensitivity & Strategic Zones')
    carbon_range = np.linspace(10, 200, 200)
    scenarios = {'Current (13%)': 0.1281, 'Conservative (25%)': 0.25, 'Moderate (40%)': 0.40, '2030 Target (61%)': 0.61}
    fig4 = go.Figure()
    colors = ['red', 'orange', 'gold', 'green']
    for (label, af), color in zip(scenarios.items(), colors):
        costs = [compute_total_cost(0.8313, af, cp) for cp in carbon_range]
        fig4.add_trace(go.Scatter(x=carbon_range, y=costs, mode='lines', name=label, line=dict(color=color, width=2)))
    fig4.add_vrect(x0=10,  x1=65,  fillcolor='blue',   opacity=0.05, annotation_text='Business as Usual',        annotation_position='top left')
    fig4.add_vrect(x0=65,  x1=119, fillcolor='orange',  opacity=0.05, annotation_text='Transitional',             annotation_position='top left')
    fig4.add_vrect(x0=119, x1=200, fillcolor='red',     opacity=0.05, annotation_text='Green Strategy Mandatory', annotation_position='top left')
    fig4.add_vline(x=65,  line_dash='dash', line_color='black',   annotation_text='$65 Tipping Point')
    fig4.add_vline(x=119, line_dash='dash', line_color='darkred', annotation_text='$119 Dominance')
    fig4.update_layout(height=450, xaxis_title='Carbon Price (USD/ton CO2)', yaxis_title='Total Cost (USD/ton clinker)')
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('---')
    st.subheader('Decision Matrix')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('### $0 - $65 — Business as Usual\n- Cost optimization dominates\n- Alt fuel expansion beneficial but not urgent\n- Clinker ratio flexible')
    with col2:
        st.markdown('### $65 - $119 — Transitional\n- Carbon penalty significant\n- Optimal clinker ratio drops to minimum\n- Alt fuel expansion accelerates savings')
    with col3:
        st.markdown('### $119+ — Green Strategy Mandatory\n- Carbon cost exceeds fuel cost\n- Maximum alt fuel adoption required\n- Low clinker ratio non-negotiable')