import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.io as pi
import json

# Helper Functions
def plot1(results, visitors_a, visitors_b, conv_a, conv_b, confidence_level, tail):
    # Obtaining values from inputs
    df_a = visitors_a - 1
    df_b = visitors_b - 1
    alpha = 1 - (confidence_level / 100)
    p_value = results["P-Value"]
    interpretation = ""
    interpretation += "The above graph illustrates probability density functions for assumed conversion rate distributions of control(A) and experiment(B) groups centered around observed conversion rates.\n\n"
    # Choosing the test to perform
    n = visitors_a + visitors_b
    df = n - 2
    p = (conv_a + conv_b) / n

    if n * p > 5 and n * (1 - p) > 5:
        test = "z"
    else:
        test = "t"

    # Obtaining relevant details from results
    conv_rate_a = results["Conversion Rate A"]
    conv_rate_b = results["Conversion Rate B"]
    test_statistic = results["Statistic"]
    # Calculate standard deviations based on percentages
    sd_a = np.sqrt((conv_rate_a * (1 - conv_rate_a)) / visitors_a)
    sd_b = np.sqrt((conv_rate_b * (1 - conv_rate_b)) / visitors_b)
    # Define lower and upper limits for the graph
    l_a = conv_rate_a - 4 * sd_a
    l_b = conv_rate_b - 4 * sd_b
    u_a = conv_rate_a + 4 * sd_a
    u_b = conv_rate_b + 4 * sd_b
    # Calculate PDFs for Group A and Group B
    x_a = np.linspace(l_a, u_a, 500)
    x_b = np.linspace(l_b, u_b, 500)
    if test == "z":
        y_a = stats.norm.pdf(x_a, conv_rate_a, sd_a)
        y_b = stats.norm.pdf(x_b, conv_rate_b, sd_b)
    else:
        y_a = stats.t.pdf(x_a, df_a, conv_rate_a, sd_a)
        y_b = stats.t.pdf(x_b, df_b, conv_rate_b, sd_b)
    ymax_line = max(max(y_a), max(y_b)) * 1.1
    y_mid = max(max(y_a), max(y_b)) * 0.5
    fig = go.Figure()
    # Add traces with transparency and individual x-values
    fig.add_trace(
        go.Scatter(
            x=x_a,
            y=y_a,
            mode="lines",
            name="Group A (Control)",
            line=dict(color="rgba(255, 99, 71, 0.5)", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_b,
            y=y_b,
            mode="lines",
            name="Group B (Experiment)",
            line=dict(color="rgba(255, 165, 0, 0.5)", width=3),
        )
    )
    # Add the conversion rate lines
    fig.add_shape(
        type="line",
        x0=conv_rate_a,
        y0=0,
        x1=conv_rate_a,
        y1=ymax_line,
        line=dict(color="rgba(255, 99, 71, 0.6)", width=2),
        name="Conversion Rate A",
    )
    fig.add_shape(
        type="line",
        x0=conv_rate_b,
        y0=0,
        x1=conv_rate_b,
        y1=ymax_line,
        line=dict(color="rgba(255, 165, 0, 0.6)", width=2),
        name="Conversion Rate B",
    )

    # Add annotations for the conversion rate lines
    fig.add_annotation(
        x=conv_rate_a,
        y=y_mid,
        text=f"<b>CR A: {round(100*conv_rate_a, 2)}%</b>",
        showarrow=False,
        textangle=-90,
        xanchor="right",
    )
    fig.add_annotation(
        x=conv_rate_b,
        y=y_mid,
        text=f"<b>CR B: {round(100*conv_rate_b, 2)}%</b>",
        showarrow=False,
        textangle=-90,
        xanchor="right",
    )
    # Getting confidence interval based on the significance level chosen by the user
    if tail == "two-tailed":
        interpretation += f"Dotted lines around conversion rate (A) represent {confidence_level}% confidence interval of the control group."
        if test == "z":
            critical_value = stats.norm.ppf(1 - alpha / 2)
        else:
            critical_value = stats.t.ppf(1 - alpha / 2, df)

        ciA = (
            conv_rate_a - (critical_value * sd_a),
            conv_rate_a + (critical_value * sd_a),
        )
        ciB = (
            conv_rate_b - (critical_value * sd_b),
            conv_rate_b + (critical_value * sd_b),
        )

        if test == "z":
            x_fill = np.linspace(ciA[1], x_b[-1], 500)
            yb_fill = stats.norm.pdf(x_fill, conv_rate_b, sd_b)
        else:
            x_fill = np.linspace(ciA[1], x_b[-1], 500)
            yb_fill = stats.t.pdf(x_fill, df_b, conv_rate_b, sd_b)

        if p_value < alpha:
            if conv_rate_b > ciA[1]:
                # Adding confidence interval lines for B when the result is significant
                fig.add_shape(
                    type="line",
                    x0=ciA[0],
                    y0=0,
                    x1=ciA[0],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                    name="Confidence Interval A (Two-Tailed)",
                )
                fig.add_shape(
                    type="line",
                    x0=ciA[1],
                    y0=0,
                    x1=ciA[1],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                )
                fig.add_annotation(
                    x=ciA[0],
                    y=ymax_line,
                    text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[0], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="right",
                )
                fig.add_annotation(
                    x=ciA[1],
                    y=ymax_line,
                    text=f" <b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[1], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )

                # Filling the uplift region green to show that the result was significant
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=yb_fill,
                        fill="tozeroy",
                        fillcolor="rgba(0, 128, 0, 0.3)",
                        line=dict(color="rgba(0, 128, 0, 0.5)", width=2),
                        name="Significant Positive Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the right of the {confidence_level}% confidence interval of the control group. \n\nThe uplift region is shaded green in the visualization to showcase the significant positive uplift. "

            elif conv_rate_b < ciA[0]:

                # Adding confidence interval lines for B when the result is significant
                fig.add_shape(
                    type="line",
                    x0=ciA[0],
                    y0=0,
                    x1=ciA[0],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                    name="Confidence Interval A (Two-Tailed)",
                )
                fig.add_shape(
                    type="line",
                    x0=ciA[1],
                    y0=0,
                    x1=ciA[1],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                )
                fig.add_annotation(
                    x=ciA[0],
                    y=ymax_line,
                    text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[0], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )
                fig.add_annotation(
                    x=ciA[1],
                    y=ymax_line,
                    text=f" <b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[1], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )

                # Filling the entire B region red to show that the we had negative conversions in test
                if test == "z":
                    xfill_b = np.linspace(x_b[0], ciA[0], 500)
                    yfill_b = stats.norm.pdf(xfill_b, conv_rate_b, sd_b)
                else:
                    xfill_b = np.linspace(x_b[0], ciA[0], 500)
                    yfill_b = stats.t.pdf(xfill_b, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=xfill_b,
                        y=yfill_b,
                        fill="tozeroy",
                        fillcolor="rgba(128, 0, 0, 0.3)",
                        line=dict(color="rgba(128, 0, 0, 0.5)", width=2),
                        name="Significant Negative Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the left of the {confidence_level}% confidence interval of the control group. \n\nThe uplift region is shaded red in the visualization to showcase the significant negative uplift. "

        else:
            if conv_rate_b > ciA[1]:
                # Adding confidence interval lines for B when the result is significant
                fig.add_shape(
                    type="line",
                    x0=ciA[0],
                    y0=0,
                    x1=ciA[0],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                    name="Confidence Interval A (Two-Tailed)",
                )
                fig.add_shape(
                    type="line",
                    x0=ciA[1],
                    y0=0,
                    x1=ciA[1],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                )
                fig.add_annotation(
                    x=ciA[0],
                    y=ymax_line,
                    text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[0], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="right",
                )
                fig.add_annotation(
                    x=ciA[1],
                    y=ymax_line,
                    text=f" <b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[1], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )

                # Filling the uplift region green to show that the result was significant
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=yb_fill,
                        fill="tozeroy",
                        fillcolor="rgba(128, 128, 128, 0.5)",
                        line=dict(color="rgba(0, 128, 0, 0.5)", width=2),
                        name="Insignificant Positive Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the right of the {confidence_level}% confidence interval of the control group."
                interpretation += "\n\nThe uplift is insignificant because unequal sample sizes of groups A and B result in different standard deviations for the probability distributions. The uplift region is shaded grey to showcase the same."

            elif conv_rate_b < ciA[0]:
                # Adding confidence interval lines for B when the result is significant
                fig.add_shape(
                    type="line",
                    x0=ciA[0],
                    y0=0,
                    x1=ciA[0],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                    name="Confidence Interval A (Two-Tailed)",
                )
                fig.add_shape(
                    type="line",
                    x0=ciA[1],
                    y0=0,
                    x1=ciA[1],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                )
                fig.add_annotation(
                    x=ciA[0],
                    y=ymax_line,
                    text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[0], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )
                fig.add_annotation(
                    x=ciA[1],
                    y=ymax_line,
                    text=f" <b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[1], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )
                # Filling the entire B region red to show that the we had negative conversions in test
                if test == "z":
                    xfill_b = np.linspace(x_b[0], ciA[0], 500)
                    yfill_b = stats.norm.pdf(xfill_b, conv_rate_b, sd_b)
                else:
                    xfill_b = np.linspace(x_b[0], ciA[0], 500)
                    yfill_b = stats.t.pdf(xfill_b, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=xfill_b,
                        y=yfill_b,
                        fill="tozeroy",
                        fillcolor="rgba(128, 128, 128, 0.5)",
                        line=dict(color="rgba(128, 0, 0, 0.5)", width=2),
                        name="Insignificant Negative Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the left of the {confidence_level}% confidence interval of the control group. \n\nThe uplift region is shaded grey in the visualization to showcase the insignificant negative uplift. "

            else:
                # Adding confidence interval lines for B when the result is insignificant
                fig.add_shape(
                    type="line",
                    x0=ciA[0],
                    y0=0,
                    x1=ciA[0],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                    name="Confidence Interval A (Two-Tailed)",
                )
                fig.add_shape(
                    type="line",
                    x0=ciA[1],
                    y0=0,
                    x1=ciA[1],
                    y1=ymax_line,
                    line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
                )
                fig.add_annotation(
                    x=ciA[0],
                    y=ymax_line,
                    text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[0], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="right",
                )
                fig.add_annotation(
                    x=ciA[1],
                    y=ymax_line,
                    text=f" <b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA[1], 2)}%</b>",
                    showarrow=False,
                    textangle=0,
                    xanchor="left",
                )
                # Filling the uplift region grey to show that the result was insignificant
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=yb_fill,
                        fill="tozeroy",
                        fillcolor="rgba(120,120, 120,0.3)",
                        line=dict(color="rgba(128, 128, 128, 0.5)", width=2),
                        name="Insignificant Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls within the {confidence_level}% confidence interval of the control group. \n\nThe uplift region is shaded grey in the visualization to showcase tha insignificant uplift. "

    # ASSUMING RIGHT TAILED ONLY
    elif tail == "one-tailed":
        interpretation += f"The single dotted line represents the upper bound of {confidence_level}% confidence level of the control group for the right-tailed test."

        if test == "z":
            critical_value = stats.norm.ppf(1 - alpha)
        else:
            critical_value = stats.t.ppf(1 - alpha, df)
        ciA = conv_rate_a + (critical_value * sd_a)
        ciB = conv_rate_b + (critical_value * sd_b)

        ci = 2 * ciB
        fig.add_shape(
            type="line",
            x0=ciA,
            y0=0,
            x1=ciA,
            y1=ymax_line,
            line=dict(color="rgba(255, 99, 71, 0.5)", dash="dot"),
            name="Confidence Interval A (One-Tailed)",
        )
        fig.add_annotation(
            x=ciA,
            y=ymax_line,
            text=f"<b>{int(100*(1-alpha))}% CI A <br>{round(100*ciA, 2)}%</b>",
            showarrow=False,
            textangle=0,
            xanchor="left",
        )
        if p_value < alpha:
            if conv_rate_b > ciA:
                x_fill = np.linspace(ciA, x_b[-1], 500)
                if test == "z":
                    y_fill = stats.norm.pdf(x_fill, conv_rate_b, sd_b)
                else:
                    y_fill = stats.t.pdf(x_fill, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=y_fill,
                        fill="tozeroy",
                        fillcolor="rgba(0, 128, 0, 0.3)",
                        line=dict(color="rgba(0, 128, 0, 0.5)", width=2),
                        name="Significant Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the right of the {confidence_level}% confidence level of the control group. \n\nThe uplift region is shaded green in the visualization to showcase the significant positive uplift. "

            else:
                x_fill = np.linspace(ciA, x_b[-1], 500)
                if test == "z":
                    y_fill = stats.norm.pdf(x_fill, conv_rate_b, sd_b)
                else:
                    y_fill = stats.t.pdf(x_fill, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=y_fill,
                        fill="tozeroy",
                        fillcolor="rgba(128,128,128,0.3)",
                        line=dict(color="rgba(128, 128, 128, 0.5)", width=2),
                        name="Insignificant Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls under the {confidence_level}% confidence level of the control group. \n\nThe uplift region is shaded grey in the visualization to represent the region where the conversion rate B should be to obtain significant results. "

        else:
            if conv_rate_b > ciA:
                x_fill = np.linspace(ciA, x_b[-1], 500)
                if test == "z":
                    y_fill = stats.norm.pdf(x_fill, conv_rate_b, sd_b)
                else:
                    y_fill = stats.t.pdf(x_fill, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=y_fill,
                        fill="tozeroy",
                        fillcolor="rgba(128,128,128,0.3)",
                        line=dict(color="rgba(0, 128, 0, 0.5)", width=2),
                        name="Insignificant Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls to the right of the {confidence_level}% confidence level of the control group."
                interpretation += "\n\nThe uplift is insignificant because unequal sample sizes of groups A and B result in different standard deviations for the probability distributions. The uplift region is shaded grey to showcase the same."

            else:
                x_fill = np.linspace(ciA, x_b[-1], 500)
                if test == "z":
                    y_fill = stats.norm.pdf(x_fill, conv_rate_b, sd_b)
                else:
                    y_fill = stats.t.pdf(x_fill, df_b, conv_rate_b, sd_b)
                fig.add_trace(
                    go.Scatter(
                        x=x_fill,
                        y=y_fill,
                        fill="tozeroy",
                        fillcolor="rgba(128,128,128,0.3)",
                        line=dict(color="rgba(128, 128, 128, 0.5)", width=2),
                        name="Insignificant Uplift",
                    )
                )
                interpretation += f" The Conversion rate of Group B falls under the {confidence_level}% confidence level of the control group. \n\nThe uplift region is shaded grey in the visualization to represent the region where the conversion rate B should be to obtain significant results. "

    # Set x-axis tick format to percentages
    fig.update_layout(xaxis_tickformat=".1%")
    # Add x and y labels and title
    fig.update_layout(
        xaxis_title="Conversion Rate (%)",
        yaxis_title="Probability Density Function",
        width=1200,
        height=700,
    )
    # Legend layout and size
    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.84,
            xanchor="right",
            x=0.98,
            font=dict(size=15),
        )
    )

    return {"Figure": fig, "Interpretation": interpretation}


def generate_conclusion(results, confidence_level, tail):
    conclusion = ""
    alpha = confidence_level
    absolute = results["Conversion Rate B"] * 100 - results["Conversion Rate A"] * 100
    abs = round(absolute, 2)
    level = (1 - alpha) * 100
    # Statistically significant
    if results["P-Value"] < alpha:
        if results["Conversion Rate A"] < results["Conversion Rate B"]:
            conclusion += (
                "\nThe treatment group(B) showed a "
                + str(abs)
                + "% absolute uplift over control group(A). \n"
            )
            conclusion += (
                str(level)
                + "% of the time, the outcome is due to the changes and not due to random chance. \n"
            )
            conclusion += "\nThis suggests that group B is the more effective strategy for increasing conversions. \n"
            return (
                "### Conclusion: \n"
                + "##### The test results are :green[statistically significant]."
                + conclusion
                + "\n"
                + results["Test"]
                + "\n"
            )

        if results["Conversion Rate A"] > results["Conversion Rate B"]:
            conclusion += (
                "\nThe treatment group(B) showed a "
                + str(abs)
                + "% absolute decrease over control group(A). \n"
            )
            conclusion += (
                str(level)
                + "% of the time, the outcome is due to the changes and not due to random chance. \n"
            )
            conclusion += "\nThis suggests that group B is not an effective strategy for increasing conversions. \n"
            return (
                "### Conclusion: \n"
                + "##### The test results are :green[statistically significant]."
                + conclusion
                + "\n"
                + results["Test"]
                + "\n"
            )

    # Statistically insignificant
    else:
        if results["Conversion Rate A"] < results["Conversion Rate B"]:
            conclusion += (
                "\nDespite treatment group(B) showing a "
                + str(abs)
                + "% absolute uplift over control group(A), it is not conclusive enough to make a decision.\n"
            )
            conclusion += "\nFurther investigation or a larger data may be needed for reliable insights. \n"
            return (
                " The test results are :red[statistically insignificant]."
                + conclusion
                + "\n"
                + results["Test"]
                + "\n"
            )

        if results["Conversion Rate A"] > results["Conversion Rate B"]:
            conclusion += (
                "\nThough the treatment group(B) showed a "
                + str(abs)
                + "% absolute decrease over control group(A), it is not conclusive enough to make a decision. \n"
            )
            conclusion += "\nFurther investigation or a larger data may be needed for reliable insights. \n"
            return (
                + "The test results are :red[statistically insignificant]."
                + conclusion
                + "\n"
                + results["Test"]
                + "\n"
            )


def generate_conclusion_mvt(
    results: dict, diff_in_cr: list, pvalues: list, alpha_level, tail
):
    conclusion = ""
    diff_in_cr = diff_in_cr
    significance = []
    for i in range(len(pvalues)):
        if pvalues[i] < alpha_level:
            significance.append("Significant")
        else:
            significance.append("Insignificant")

    disclaimer = "DISCLAIMER: This tool currently conducts a pairwise test for each pair of control and treatment groups without correcting for familywise error rate, and is therefore not entirely theoretically correct."
    disclaimer += " The appropriate way to go about a multivariate test would be to either conduct an ANOVA or Chi-squared Test (using a contingency table)."
    disclaimer += " If the null hypothesis (of equality) is rejected, pairwise comparisons can be performed using the Tukey-Kramer test or the Fisher's Exact Test respectively to find out which of the treatment groups differ significantly from the control."
    disclaimer += " This will be updated in future versions of the tool."

    # Statistically significant
    significant_groups = {}
    for i in range(len(significance)):
        if significance[i] == "Significant":
            significant_groups[i + 2] = pvalues[i]
        else:
            pass

    significant_lifts = {}
    for i in range(len(significant_groups)):
        significant_lifts[i + 2] = diff_in_cr[i]

    if len(significant_groups) == 0:
        # Statistically insignificant
        conclusion += "\nNone of the treatment groups showed a significant absolute increase or decrease over the control group(A), i.e, have a big enough change for it be conclusive enough to make a decision. \n"
        conclusion += "\nFurther investigation or a larger data may be needed for reliable insights.\n"
        return (
            "The test results are :red[statistically insignificant]."
            + conclusion
            + "\n"
            + results["Test"]
            + "\n"
            + disclaimer
        )
    else:
        max_uplift = max(significant_lifts, key=lambda x: significant_lifts[x])
        conclusion += (
            f"\nTreatment group {max_uplift} showed the greatest absolute uplift of "
            + str(significant_lifts[max_uplift] * 100)
            + "% over control group(A). \n"
        )
        conclusion += (
            str((1 - alpha_level) * 100)
            + "% of the time, the outcome is due to the changes and not due to random chance.\n"
        )
        conclusion += f"\nThis suggests that group {max_uplift} is the more effective strategy for increasing conversions.\n"
        return (
            "The test results are :green[statistically significant]."
            + conclusion
            + "\n"
            + results["Test"]
            + "\n"
            + disclaimer
        )


# Dynamic Input Function
def analysis_function(
    visitors_input, conversions_input, confidence_level: float, two_tail
):
    alpha_level = round(1 - confidence_level, 2)
    visitor_counts = []
    for i in range(visitors_input["arms"]):
        visitor_counts.append(visitors_input["data"][i]["value"])
    conversion_counts = []
    for i in range(conversions_input["arms"]):
        conversion_counts.append(conversions_input["data"][i]["value"])

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
        round(diff_in_cr[i] / conversion_rates[0], 2) for i in range(len(diff_in_cr))
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
        if ((N * pooled_props[i]) > 5) & ((N * (1 - pooled_props[i])) > 5):
            test = "NOTE: Z-test is being performed as the total count of conversions is sufficiently large.\n"
            if two_tail == "two-tailed":
                pvalues.append(2 * stats.norm.cdf(-np.abs(statistic_scores[i])))
            else:
                pvalues.append(stats.norm.cdf(statistic_scores[i]))
        else:
            test = "NOTE: t-test is being performed as the total count of conversions is pretty small.\n"
            if two_tail == "two-tailed":
                pvalues.append(
                    2 * (1 - stats.t.cdf(np.abs(statistic_scores[i]), dfs[i]))
                )
            else:
                pvalues.append(1 - stats.t.cdf(abs(statistic_scores[i]), dfs[i]))

    results = {
        "P-Value": pvalues[0],
        "Conversion Rate A": conversion_rates[0],
        "Conversion Rate B": conversion_rates[1],
        "Statistic": statistic_scores[0],
        "Test": test,
    }

    fig_dict = {}

    if len(visitor_counts) == 2:
        fig = plot1(
            results,
            visitor_counts[0],
            visitor_counts[1],
            conversion_counts[0],
            conversion_counts[1],
            (1 - alpha_level) * 100,
            two_tail,
        )

        fig_json = pi.to_json(fig["Figure"])
        fig_dict = json.loads(fig_json)

        conclusion = generate_conclusion(results, alpha_level, two_tail)

    else:
        fig = None
        conclusion = generate_conclusion_mvt(
            results, diff_in_cr, pvalues, alpha_level, two_tail
        )

    data_as_response = {
        "arms": len(visitor_counts),
        "conversion-rates": [
            {"arm": i + 1, "value": conversion_rates[i] * 100}
            for i in range(len(conversion_rates))
        ],
        "difference-conversion-rates": [
            {"arm": i + 2, "value": diff_in_cr[i] * 100} for i in range(len(diff_in_cr))
        ],
        "relative-uplift-values": [
            {"arm": i + 2, "value": uplifts[i] * 100} for i in range(len(uplifts))
        ],
        "standard-errors": [
            {"arm": i + 2, "value": standard_errors[i]}
            for i in range(len(standard_errors))
        ],
        "p-values": [{"arm": i + 2, "value": pvalues[i]} for i in range(len(pvalues))],
        "warnings": warnings,
        "conclusion": conclusion,
        "figure": fig_dict,
    }

    print(data_as_response)

    return data_as_response


# Expecting visitor and conversions dictionary to be in this format:
#     visitors_input =  {"arms":5,
#                     "data":[
#                         {
#                         "id":1,
#                         "value":23
#                         },
#                         {
#                         "id":2,
#                         "value":23
#                         },
#                         {
#                         "id":3,
#                         "value":23
#                         },
#                         {
#                         "id":4,
#                         "value":23
#                         },
#                         {
#                         "id":5,
#                         "value":23
#                         }
#                     ]
#                     }

#     conversions_input =  {"arms":5,
#                     "data":[
#                         {
#                         "id":1,
#                         "value":23
#                         },
#                         {
#                         "id":2,
#                         "value":23
#                         },
#                         {
#                         "id":3,
#                         "value":23
#                         },
#                         {
#                         "id":4,
#                         "value":23
#                         },
#                         {
#                         "id":5,
#                         "value":23
#                         }
#                     ]
#                     }

# Example
visitor_input = {
    "arms": 3,
    "data": [
        {"id": 1, "value": 1000},
        {"id": 2, "value": 1000},
        {"id": 3, "value": 1000},
    ],
}

conversion_input = {
    "arms": 3,
    "data": [{"id": 1, "value": 200}, {"id": 2, "value": 240}, {"id": 3, "value": 260}],
}
