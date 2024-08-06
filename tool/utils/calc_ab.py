import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
from scipy import stats
import plotly.io as pi
import json

def plot1(visitors, conversions, tail, results, confidence_level=95):
    groups = len(visitors)
    conversion_rates = np.array(conversions) / np.array(visitors)
    p_value = results['P-Value']
    alpha = 1 - (confidence_level / 100)
    test=results['Test']

    # Create an interactive plot for normal distribution curves
    fig = go.Figure()
    x = np.linspace(min(conversion_rates) - 0.1, max(conversion_rates) + 0.1, 1000)

    # Variables to hold max density value for scaling y-axis and colors
    max_density = 0
    # colors = ['red', 'orange', 'green', 'blue', 'purple', 'brown']
    # colors=['54C1E2','8A54E2','E25490','5754E2','E25454','D3F27B','F2917B','9575F0','F9D1A8','F9F9A8','FF0000','D1A8F9','F816F8','A8F9F9','BEBEBE','0400DD','C5F9A8','F9A8A8','0FC70B']
    colors = ['#54C1E2', '#8A54E2', '#E25490', '#5754E2', '#E25454', '#D3F27B', 
          '#F2917B', '#9575F0', '#F9D1A8', '#F9F9A8', '#FF0000', '#D1A8F9', 
          '#F816F8', '#A8F9F9', '#BEBEBE', '#0400DD', '#C5F9A8', '#F9A8A8', 
          '#0FC70B']
    interpretation=''
    
    for i in range(groups):
        mean = conversion_rates[i]
        std_err = np.sqrt((mean * (1 - mean)) / visitors[i])
        dof = visitors[i] - 1
        if test == 'z':
            y = stats.norm.pdf(x, mean, std_err)
        else:
            y = stats.t.pdf(x, dof, mean, std_err)
        
        if(i==0):
            if test == 'z':
                critical_value=stats.norm.ppf(1 - alpha/2) if tail=='two' else stats.norm.ppf(1 - alpha)
                ci_upper = mean + critical_value * std_err
                ci_lower = mean - critical_value * std_err 
            else:
                critical_value=stats.t.ppf(1 - alpha,dof) if tail=='two' else stats.norm.ppf(1 - alpha)
                ci_upper = mean + critical_value * std_err
                ci_lower = mean - critical_value * std_err

        max_density = max(max_density, max(y))

        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=f'Group {i + 1} (CR: {mean:.2%})',
            line=dict(color=colors[i % len(colors)])
        ))

        # Add vertical lines for mean conversion rates
        fig.add_trace(go.Scatter(
            x=[mean, mean],
            y=[0, max_density],
            mode='lines',
            name=f'CR Group {i + 1}: {mean:.2%}',
            line=dict(color=colors[i % len(colors)], dash='dash')
        ))
        if i==0:
            # Add ci_upper line
            fig.add_trace(go.Scatter(
                x=[ci_upper, ci_upper, None, None],
                y=[0, max_density, max_density, 0],
                name='CI Upper',
                fill='tozeroy',
                fillcolor='green',
                line=dict(color='#FFFFFF'),
                opacity=0.2,
                showlegend=False,
                cliponaxis=False
            ))
            
            #add ci_lower line
            fig.add_trace(go.Scatter(
            x=[ci_lower, ci_lower, None, None],
            y=[0, max_density, max_density, 0],
            name='CI Lower',
            fill='tozeroy',
            fillcolor='red',
            line=dict(color='#FFFFFF'),
            opacity=0.2,
            showlegend=False,
            cliponaxis=False
            ))
            
             # Add annotations for CI lines
            fig.add_annotation(
                x=ci_upper,
                y=max_density,
                text="CI Upper",
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=-30,
                font=dict(color='#FFFFFF')
            )
            fig.add_annotation(
                x=ci_lower,
                y=max_density,
                text="CI Lower",
                showarrow=True,
                arrowhead=2,
                ax=-20,
                ay=-30,
                font=dict(color='#FFFFFF')
            )
        
        if tail=="two-tailed" and i!=0:
        # Add shaded area above ci_upper
            x_fill = x[x > ci_upper]
            y_fill = y[x > ci_upper]

            fig.add_trace(go.Scatter(
                x=np.concatenate(([ci_upper], x_fill, [x_fill[-1], ci_upper])),
                y=np.concatenate(([0], y_fill, [0, 0])),
                fill='toself',
                fillcolor='rgba(0,255,0,0.2)' if p_value[i-1]<alpha else 'rgba(128,128,128,0.2)',  # Green color with transparency
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))
            
            # Add shaded area below ci_lower (if two-tailed)
            x_fill = x[x < ci_lower]
            y_fill = y[x < ci_lower]

            fig.add_trace(go.Scatter(
                x=np.concatenate(([ci_lower], x_fill, [x_fill[-1], ci_lower])),
                y=np.concatenate(([0], y_fill, [0, 0])),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)' if p_value[i-1]<alpha else 'rgba(128,128,128,0.2)',  # Red color with transparency
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))
        elif (i!=0):
            # Right one-tailed
            # Add shaded area above ci_upper
            x_fill = x[x > ci_upper]
            y_fill = y[x > ci_upper]
            fig.add_trace(go.Scatter(
                x=np.concatenate(([ci_upper], x_fill, [x_fill[-1], ci_upper])),
                y=np.concatenate(([0], y_fill, [0, 0])),
                fill='toself',
                fillcolor='rgba(0,255,0,0.2)' if p_value[i-1]<alpha else 'rgba(128,128,128,0.2)',  # Green color with transparency if significant else grey
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))

        
        if(i!=0):
            if(p_value[i-1]<alpha):
                if conversion_rates[i]>ci_upper:
                    interpretation+= f"The Conversion rate of Group {i+1} falls to the right of the {confidence_level}% confidence interval of the control group.\nThe uplift region is shaded green in the visualization to showcase the significant positive uplift.\n\n"
                elif conversion_rates[i]<ci_lower and tail=='two':
                    interpretation += f"The Conversion rate of Group {i+1} falls to the left of the {confidence_level}% confidence interval of the control group.\nThe uplift region is shaded red in the visualization to showcase the significant negative uplift.\n\n"   
            else:
                if conversion_rates[i]>ci_upper and tail=='two':
                    interpretation += f"The Conversion rate of Group {i+1} falls to the right of the {confidence_level}% confidence interval of the control group.\n"
                    interpretation += f"The uplift is insignificant because unequal sample sizes of groups 0 and {i} result in different standard deviations for the probability distributions.\n"
                    interpretation+="The uplift region is shaded grey to showcase the same.\n\n"
                elif conversion_rates[i]<ci_lower and tail=='two':
                    interpretation += f"The Conversion rate of Group {i+1} falls to the left of the {confidence_level}% confidence interval of the control group.\n"
                    interpretation += f"The uplift is insignificant because unequal sample sizes of groups 0 and {i} result in different standard deviations for the probability distributions.\n"
                    interpretation+="The uplift region is shaded grey to showcase negative uplift.\n\n"

                elif tail=='two':
                    interpretation += f"The Conversion rate of Group {i+1} falls within the {confidence_level}% confidence interval of the control group.\n"
                    interpretation += f"The uplift is insignificant because unequal sample sizes of groups 0 and {i} result in different standard deviations for the probability distributions.\n\n"


    # Add layout details
    fig.update_layout(
        title='Conversion Rate Distribution of Different Groups',
        xaxis_title='Conversion Rate (%)',
        yaxis_title='Probability Density Function',
        legend=dict(x=0.8, y=1),
        plot_bgcolor='#2E383F',
        paper_bgcolor='#2E383F',
        font=dict(color='#FFFFFF')
    )

    # fig.show()
    # print(interpretation)
    return {"Figure": fig, "Interpretation": interpretation}

def generate_conclusion(results, alpha):
    conclusions = []
    conversion_rates=results['Conversion Rate']
    absolute = conversion_rates[1]*100 - conversion_rates[0]*100
    abs_value = round(absolute, 2)
    confidence_level = (1 - alpha) * 100
    
    # Determine the significance and direction of the result
    if results['P-Value'][0] < alpha:
        status = "significant"
        if conversion_rates[0] < conversion_rates[1]:
            conclusions.append({"text": f"The treatment group (B) showed a {abs_value}% absolute uplift over control group (A). {confidence_level:.2f}% of the time, the outcome is due to the changes and not due to random chance. This suggests that group B is the more effective strategy for increasing conversions.", "className": ''})
        elif conversion_rates[0] > conversion_rates[1]:
            conclusions.append({"text": f"The treatment group (B) showed a {abs_value}% absolute decrease over control group (A). {confidence_level:.2f}% of the time, the outcome is due to the changes and not due to random chance. This suggests that group B is not an effective strategy for increasing conversions.", "className": ''})

    else:
        status = "insignificant"
        if conversion_rates[0] < conversion_rates[1]:
            conclusions.append({"text": f"Despite treatment group (B) showing a {abs_value}% absolute uplift over control group (A), it is not conclusive enough to make a decision. Further investigation or a larger data set may be needed for reliable insights.", "className": ''})
        elif conversion_rates[0] > conversion_rates[1]:
            conclusions.append({"text": f"Though the treatment group (B) showed a {abs_value}% absolute decrease over control group (A), it is not conclusive enough to make a decision. Further investigation or a larger data set may be needed for reliable insights.", "className": ''})

    # Add test type and significance to conclusions
    conclusions.insert(0, {"text": f"The test results are statistically", "className": ''})
    conclusions.append({"text": "", "className": "text-white"})
    conclusions.append({"text": results['Test'], "className": "font-bold"})

    return conclusions, status


def generate_conclusion_mvt(results: dict, diff_in_cr: list, alpha_level: float):
    disclaimer = (
        "DISCLAIMER: This tool currently conducts a pairwise test for each pair of control and treatment groups "
        "without correcting for familywise error rate, and is therefore not entirely theoretically correct. "
        "The appropriate way to go about a multivariate test would be to either conduct an ANOVA or Chi-squared Test "
        "(using a contingency table). If the null hypothesis (of equality) is rejected, pairwise comparisons can be "
        "performed using the Tukey-Kramer test or the Fisher's Exact Test respectively to find out which of the "
        "treatment groups differ significantly from the control. This will be updated in future versions of the tool."
    )
    conclusions = []
    significance = []

    for i, pvalue in enumerate(results['P-Value']):
        if pvalue < alpha_level:
            significance.append("Significant")
        else:
            significance.append("Insignificant")

    significant_groups = {
        index + 2: diff_in_cr[index] for index, value in enumerate(significance) if value == "Significant"
    }

    if not significant_groups:
        conclusions.append({"text": "None of the treatment groups showed a significant absolute increase or decrease over the control group(A), i.e, have a big enough change for it to be conclusive enough to make a decision.", "className": "text-warning"})
        conclusions.append({"text": "Further investigation or a larger data may be needed for reliable insights.", "className": "text-info"})
    else:
        max_uplift_group = max(significant_groups, key=significant_groups.get)
        max_uplift = significant_groups[max_uplift_group]

        conclusions.append({"text": f"Treatment group {max_uplift_group} showed the greatest absolute uplift of {max_uplift * 100:.2f}% over control group (A).", "className": "text-success"})
        conclusions.append({"text": f"{(1 - alpha_level) * 100:.2f}% of the time, the outcome is due to the changes and not due to random chance.", "className": "text-success"})
        conclusions.append({"text": f"This suggests that group {max_uplift_group} is the more effective strategy for increasing conversions.", "className": "text-success"})

    test_status_color = "green" if significant_groups else "red"
    conclusions.insert(0, {"text": f"The test results are statistically", "className": ""})
    conclusions.append({"text": "", "className": ""})
    conclusions.append({"text": results["Test"], "className": "font-bold"})
    conclusions.append({"text": "", "className": ""})
    conclusions.append({"text": disclaimer, "className": ""})

    return conclusions,significance


def analysis_function(visitors_input, conversions_input, confidence_level: float, two_tail):
    visitor_counts = []
    for i in range(visitors_input["arms"]):
        visitor_counts.append(visitors_input["data"][i]["value"])
    conversion_counts = []
    for i in range(conversions_input["arms"]):
        conversion_counts.append(conversions_input["data"][i]["value"])
    alpha_level = round(1 - confidence_level/100, 2)

    N = sum(value for value in visitor_counts)
    test = ""
    warnings = [
        "ATTENTION! Different sample sizes (visitors) in each group could introduce bias, potentially influencing test results.\n\n For a more accurate comparison, consider equalizing sample sizes between the groups."
        for i in range(1, len(visitor_counts))
        if visitor_counts[i] != visitor_counts[0]
    ]

    conversion_rates = [
        conversion_counts[i] / visitor_counts[i] for i in range(len(visitor_counts))
    ]
    diff_in_cr = [
        round(conversion_rates[i] - conversion_rates[0], 2)
        for i in range(1, len(conversion_rates))
    ]

    uplifts = [
        round(diff_in_cr[i] / (conversion_rates[0] + 10**-27), 2) for i in range(len(diff_in_cr))
    ]

    standard_errors = [
        (
            np.sqrt(
                (conversion_rates[0] * (1 - conversion_rates[0]) / visitor_counts[0])
                + (conversion_rates[i] * (1 - conversion_rates[i]) / visitor_counts[i])
            )
        )
        for i in range(1, len(conversion_rates))
    ]
    dfs = [
        (visitor_counts[0] + visitor_counts[i] - 2)
        for i in range(1, len(visitor_counts))
    ]
    pooled_props = [
        (
            (conversion_counts[0] + conversion_counts[i])
            / (visitor_counts[0] + visitor_counts[i])
        )
        for i in range(1, len(conversion_counts))
    ]
    statistic_scores = [
        (diff_in_cr[i] / standard_errors[i]) for i in range(len(diff_in_cr))
    ]

    pvalues = []

    for i in range(len(statistic_scores)):
        if ((N * pooled_props[i]) > 5) and ((N * (1 - pooled_props[i])) > 5):
            test = "NOTE: Z-test is being performed as the total count of conversions is sufficiently large.\n"
            if two_tail == "two-tailed":
                pvalues.append(2 * (1 - stats.norm.cdf(np.abs(statistic_scores[i]))))
            else:
                if statistic_scores[i] > 0:
                    pvalues.append(1 - stats.norm.cdf(statistic_scores[i]))  # Greater than direction
                else:
                    pvalues.append(stats.norm.cdf(statistic_scores[i]))  # Less than direction
        else:
            test = "NOTE: t-test is being performed as the total count of conversions is pretty small.\n"
            if two_tail == "two-tailed":
                pvalues.append(2 * (1 - stats.t.cdf(np.abs(statistic_scores[i]), dfs[i])))
            else:
                if statistic_scores[i] > 0:
                    pvalues.append(1 - stats.t.cdf(statistic_scores[i], dfs[i]))  # Greater than direction
                else:
                    pvalues.append(stats.t.cdf(statistic_scores[i], dfs[i]))  # Less than direction

    results = {
        "P-Value": pvalues,
        "Conversion Rate": conversion_rates,
        "Test": test,
    }

    fig_dict = {}
    status = ""

    if len(visitor_counts) == 2:
        fig=plot1(
            visitor_counts,
            conversion_counts,
            two_tail,
            results,
            confidence_level
        )

        fig_json = pi.to_json(fig["Figure"])
        fig_dict = json.loads(fig_json)

        conclusion, status = generate_conclusion(results, alpha_level)
        significance=[status]

    else:
        fig = plot1(
            visitor_counts,
            conversion_counts,
            two_tail,
            results,
            confidence_level
        )

        fig_json = pi.to_json(fig["Figure"])
        fig_dict = json.loads(fig_json)

        conclusion,significance = generate_conclusion_mvt(results, diff_in_cr, alpha_level)

    print(conclusion)

    data_as_response = {
        "arms": len(visitor_counts),
        "conversion-rates": [
            {"arm": i + 1, "value": conversion_rates[i] * 100}
            for i in range(len(conversion_rates))
        ],
        "difference-conversion-rates": [
            {"arm": i + 2, "value": diff_in_cr[i] * 100} for i in range(len(diff_in_cr))
        ],
        "max_uplift": max(uplifts) * 100,
        # "statistically_significant": True if "significant" == status else False,
        "relative-uplift-values": [
            {"arm": i + 2, "value": uplifts[i] * 100} for i in range(len(uplifts))
        ],
        "standard-errors": [
            {"arm": i + 2, "value": standard_errors[i]}
            for i in range(len(standard_errors))
        ],
        "p-values": [{"arm": i + 2, "value": pvalues[i]} for i in range(len(pvalues))],
        "significance": [{"arm": i + 2, "value": significance[i]} for i in range(len(significance))],
        "warnings": warnings,
        "conclusion": conclusion,
        "figure": fig_dict,
    }
    fig["Figure"].show()

    return data_as_response

# visitor_input = {
#     "arms": 3,
#     "data": [
#         {"id": 1, "value": 1000},
#         {"id": 2, "value": 1000},
#         {"id": 3, "value": 1000},
#     ],
# }

# conversion_input = {
#     "arms": 3,
#     "data": [{"id": 1, "value": 200}, {"id": 2, "value": 202}, {"id": 3, "value": 260}],
# }

# visitor_input = {
#     "arms": 2,
#     "data": [
#         {"id": 1, "value": 1000},
#         {"id": 2, "value": 1000},
#     ],
# }

# conversion_input = {
#     "arms": 2,
#     "data": [{"id": 1, "value": 70}, {"id": 2, "value": 50}],
# }


# answer=analysis_function(visitor_input, conversion_input, 95, "two-tailed")
# print(answer)