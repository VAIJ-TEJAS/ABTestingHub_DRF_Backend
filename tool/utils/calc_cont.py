import scipy.stats as stats
import numpy as np
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.io as pi


def sample_size_cont(confidence_level, power, baseline_retention, mde, vari, variations, two_tailed, absolute):
    alpha = 1 - (confidence_level/100)
    beta = 1 - (power/100)

    if two_tailed:
        alpha /= 2

    if variations > 2:
        alpha /= (variations - 1)

    if absolute:
        effect_size = (mde/2)**2
    else:
        Expected_retention = baseline_retention + ((mde / 100) * baseline_retention)
        effect_size = np.abs((Expected_retention - baseline_retention)/2) ** 2
    
    z_a = stats.norm.ppf(1 - alpha)
    z_power = stats.norm.ppf(beta)
    sample_size = ((z_a + z_power) ** 2 * vari**2) / effect_size
    return int(np.ceil(sample_size))


def duration(sample_size, arms, daily_visitors, is_equal, allocations):
    total = sample_size*arms
    if is_equal:
        days = np.ceil(total/daily_visitors)
        weeks = np.ceil(days/7)
    else:
        minimum = min(allocations)/100
        days = np.ceil(sample_size/(minimum*daily_visitors))
        weeks = np.ceil(days/7)
    return days, weeks


def calculate_revenue(revenue_per_KPI, baseline, expected_uplift, abs, sample_size_per_arm):
    
    if revenue_per_KPI == None or expected_uplift == None:
        return None, None, None
    else:
        
        expected_uplift = expected_uplift/100
    
        cntrl_revenue = revenue_per_KPI * baseline * sample_size_per_arm
        if abs:
            test_kpi_value = baseline + expected_uplift
        else:
            test_kpi_value = (1+expected_uplift) * baseline
        expt_revenue = revenue_per_KPI * test_kpi_value * sample_size_per_arm

        perct_increase = round(100*(expt_revenue - cntrl_revenue)/cntrl_revenue, 2)

        return round(cntrl_revenue, 2), round(expt_revenue, 2), perct_increase


def plot_c(df_alpha_adv, arms, factor, traffic):

    """
    Figure1
    """
    trace1 = go.Scatter(x=df_alpha_adv['Confidence Level']/100, 
                        y=df_alpha_adv['Sample Size_a'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        yaxis='y1')
    trace2 = go.Scatter(x=df_alpha_adv['Confidence Level']/100, 
                        y=(1/(factor*traffic*arms))*df_alpha_adv['Sample Size_a'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        yaxis='y2')
    data = [trace1, trace2]

    layout = go.Layout(title="Confidence Level vs. Sample Size",
                       xaxis_title='Confidence Level: (1-\u03B1)%',
                       yaxis_title='Sample Size',
                       xaxis=dict(tickformat='.1%', showgrid=True),
                       yaxis=dict(showgrid=True),
                       yaxis2=dict(showgrid=False, title="Days", overlaying = 'y', side='right'),
                       showlegend=False)
    
    fig1 = go.Figure(data = data, layout = layout)


    """
    Figure 2
    """
    trace1 = go.Scatter(x=df_alpha_adv['Power']/100, 
                        y=df_alpha_adv['Sample Size_b'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        yaxis='y1')
    
    trace2 = go.Scatter(x=df_alpha_adv['Power']/100, 
                        y=(1/(factor*traffic*arms))*df_alpha_adv['Sample Size_b'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        yaxis='y2')
    data = [trace1, trace2]

    layout = go.Layout(title="Power vs. Sample Size",
                       xaxis_title='Power',
                       yaxis_title='Sample Size',
                       xaxis=dict(tickformat='.1%', showgrid=True),
                       yaxis=dict(showgrid=True),
                       yaxis2=dict(showgrid=False, title="Days", overlaying = 'y', side='right'),
                       showlegend=False)
    
    fig2 = go.Figure(data = data, layout = layout)


    """
    Figure 3
    """
    trace1 = go.Scatter(x=df_alpha_adv['MDE'], 
                        y=df_alpha_adv['Sample Size_c'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        name='MDE vs. Sample Size',
                        yaxis='y1')
    trace2 = go.Scatter(x=df_alpha_adv['MDE'], 
                        y=(1/(factor*traffic*arms))*df_alpha_adv['Sample Size_c'], 
                        mode='lines', line=dict(color='rgba(150, 150, 230, 0.85)', width=3.5), 
                        name='MDE vs. Sample Size',
                        yaxis='y2')
    data = [trace1, trace2]

    layout = go.Layout(title="MDE vs. Sample Size",
                       xaxis_title='MDE',
                       yaxis_title='Sample Size',
                       xaxis=dict(tickformat='.1%', showgrid=True),
                       yaxis=dict(showgrid=True),
                       yaxis2=dict(showgrid=False, title="Days", overlaying = 'y', side='right'),
                       showlegend=False)
    
    fig3 = go.Figure(data = data, layout = layout)

    return fig1, fig2, fig3


def cont_calculations(confidence_level, power, baseline_kpi, standard_deviation, mde, absolute, arms, daily_interactions, two_tailed, equal_allocation, revenue_per_conversion, expected_uplift, allocations:dict = {}):
    print(confidence_level, power, baseline_kpi, standard_deviation, mde, absolute, arms, daily_interactions, two_tailed, equal_allocation, revenue_per_conversion, expected_uplift, allocations)

    # Lists created for the graph
    alpha_list = np.linspace(0.1, 0.01, 40)
    confidence_list = np.linspace(90, 99, 40)
    beta_list = np.linspace(0.2, 0.01, 40)
    mde_list = np.linspace(0.1, 0.01, 40)
    
    # Computations for graphs
    alpha_adv = [arms*sample_size_cont(100*(1-x), power,baseline_kpi, mde,standard_deviation,arms,two_tailed,absolute) for x in alpha_list]
    power_adv = [arms*sample_size_cont(confidence_level, 100*(1-x),baseline_kpi, mde,standard_deviation,arms,two_tailed, absolute) for x in beta_list]
    MDE_adv = [arms*sample_size_cont(confidence_level, power,baseline_kpi, 100*x,standard_deviation,arms,two_tailed,absolute) for x in mde_list]

    # Allocation percentages in case of unequal traffic allocations (if equal, then create an array with equal percentage values)
    alloc_percentages = []
    if equal_allocation == True:
        alloc_percentages = [100/arms]*arms
    else:
        for i in range(allocations["arms"]):
            alloc_percentages.append(allocations["data"][i]["value"])
    
    # Creating a dataframe to use as an input for the plot function
    df_alpha_adv = pd.DataFrame({'Sample Size_a': alpha_adv,
                                 'Sample Size_b': power_adv,
                                 'Sample Size_c': MDE_adv,
                                 'Confidence Level': confidence_list,
                                 'Power': [(1-x)*100 for x in beta_list],
                                 'MDE': mde_list
                                })
    
    # Getting the outputs that need to be displayed
    sample_size_per_arm = sample_size_cont(confidence_level, power,baseline_kpi, mde,standard_deviation,arms,two_tailed,absolute)
        
    total_sample_size = sample_size_per_arm*arms
    
    days_required, weeks_required = duration(sample_size_per_arm, arms, daily_interactions, equal_allocation, alloc_percentages)
    
    revenue_impact_cntrl, revenue_impact_expt, perct_impac_a = calculate_revenue(revenue_per_conversion, baseline_kpi, expected_uplift, absolute, sample_size_per_arm)
    
    fig1, fig2, fig3 = plot_c(df_alpha_adv, arms,  min(alloc_percentages)/100, daily_interactions)

    ########################################################################
    ########################################################################
    ########################################################################
    # DEVELOPERS CODE ! DO NO CHANGE THIS AT ANY COST ! ELSE THINGS GO WRONG 
    # Convert Plotly figures to JSON strings
    fig1_json = pi.to_json(fig1)
    fig2_json = pi.to_json(fig2)
    fig3_json = pi.to_json(fig3)
    
    # Parse JSON strings back into Python dictionaries
    fig1_dict = json.loads(fig1_json)
    fig2_dict = json.loads(fig2_json)
    fig3_dict = json.loads(fig3_json)
    ########################################################################
    ########################################################################
    ########################################################################

    # Updating the values in the final dictionary to be returned as the output for this function
    final_dictionary = {}
    final_dictionary["Total Sample Size"] = total_sample_size
    final_dictionary["Sample Size Per Arm"] = sample_size_per_arm
    final_dictionary["Days Required"] = days_required
    final_dictionary["Weeks Required"] = weeks_required
    final_dictionary["Control Revenue"] = revenue_impact_cntrl
    final_dictionary["Test Revenue"] = revenue_impact_expt
    ########################################################################
    ########################################################################
    ########################################################################
    # DEVELOPERS CODE ! DO NO CHANGE THIS AT ANY COST ! ELSE THINGS GO WRONG
    final_dictionary["Fig Confidence Level"] = fig1_dict
    final_dictionary["Fig Power"] = fig2_dict
    final_dictionary["Fig MDE"] = fig3_dict
    ########################################################################
    ########################################################################
    ########################################################################

    return final_dictionary

    

"""
1. Input Ranges:
    confidence level - float, 90 to 100
    power - float, 90 to 100
    baseline_kpi - float - > 0 infinity (no bound)
    standard_deviation - float - > 0 infinity (no bound)
    mde - float - > 0 to 20
    absolute - bool - True/False
    arms - int - 2 to 20
    daily interactions - int - >= 1
    two_tailed - bool - True/False
    equal_allocation - bool - True/False
    revenue_per_conversion - float - 0.01 to infinity (no bound)
    expected_uplift - float 0 to 20
    allocations - dictionary with length equaling number of arms


2. Expecting allocations dictionary to be in this format:
    allocations =  {"arms":5,
                    "data":[
                        {
                        "id":1,
                        "value":23
                        },
                        {
                        "id":2,
                        "value":23
                        },
                        {
                        "id":3,
                        "value":23
                        },
                        {
                        "id":4,
                        "value":23
                        },
                        {
                        "id":5,
                        "value":23
                        }
                    ]
                    }

3. Outputs are in the following format

final_dictionary = {
                    "Total Sample Size"]    : total_sample_size,
                    "Sample Size Per Arm"   : sample_size_per_arm, 
                    "Days Required"         : days_required, 
                    "Weeks Required"        : weeks_required, 
                    "Control Revenue"       : revenue_impact_cntrl,
                    "Test Revenue"          : revenue_impact_expt,
                    "Fig Confidence Level"  : fig1,
                    "Fig Power"             : fig2, 
                    "Fig MDE"               : fig3
                    }

"""