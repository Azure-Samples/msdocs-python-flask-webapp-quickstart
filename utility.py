import json
import plotly
import plotly.express as px
import pandas as pd
from io import StringIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib

def get_plotly_plot():
    wide_df = px.data.medals_wide()
    figure = px.bar(wide_df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


def get_plotly_plot_wisam():
    # Create a 1x4 subplot figure with the desired subplot titles.
    fig = make_subplots(rows=1, cols=4, subplot_titles=[
        "Pressure Losses",
        "ECD & Cutting Loading",
        "Mud & Cutting Velocity",
        "WB Schematic & Drill.-String"
    ])

    ### Subplot 1: Plot_pres (Pressure Losses) ###
    main_df = read_section_from_file("./Plot_pres_Data.txt", "Main Pressure Line Data:")
    body_df = read_section_from_file("./Plot_pres_Data.txt", "Body Pressure Line Data:")

    for idx, row in main_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['x1'], row['x2']],
            y=[row['y1'], row['y2']],
            mode='lines+markers',
            line=dict(width=2),
            name=f"Main {int(row['i'])}",
            showlegend=False
        ), row=1, col=1)

    for idx, row in body_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['X1'], row['X2']],
            y=[row['y2'], row['y1']],  # note: order reversed as in MATLAB
            mode='lines+markers',
            line=dict(width=2, dash='dot'),
            name=f"Body {int(row['k'])}",
            showlegend=False
        ), row=1, col=1)

    fig.update_xaxes(title_text="Pressure [bar]", row=1, col=1)
    fig.update_yaxes(title_text="Measured Depth (MD) [m]", autorange="reversed", row=1, col=1)

    ### Subplot 2: Plot_oc_ecd_2 (ECD & Cutting Loading) ###
    filename_oc = "./Plot_oc_ecd_2_Data.txt"
    df_hLine6 = read_section_from_file(filename_oc, "hLine6 data (ECD vs Cum_Len_Arr):")
    df_hLine8 = read_section_from_file(filename_oc, "hLine8 data (rho_mud_a vs Cum_Len_Arr(end)):")
    df_hLine7 = read_section_from_file(filename_oc, "hLine7 data (Sec{m}.MudProperties.rho_mud vs index):")

    fig.add_trace(go.Scatter(
        x=df_hLine6["ECD"],
        y=df_hLine6["Cum_Len_Arr"],
        mode="lines+markers",
        name="ECD[kg/m3]",
        line=dict(color="blue", dash="dash"),
        marker=dict(symbol="circle")
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[df_hLine8["rho_mud_a"].iloc[0]],
        y=[df_hLine8["Cum_Len_Arr_end"].iloc[0]],
        mode="markers",
        name="APIcuttingload+rhomudin[kg/m3]",
        marker=dict(color="red", size=10, symbol="circle")
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=df_hLine7["MudProperties_rho_mud"],
        y=df_hLine7["Index"],
        mode="lines",
        name="rhomudin[kg/m3]",
        line=dict(color="black")
    ), row=1, col=2)

    fig.update_xaxes(title_text="Density [kg/m3]", row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=2)  # No Y-axis title

    ### Subplot 3: Plot_slip_2 (Cutting Velocity) ###
    df_slip = pd.read_csv("./Plot_slip_2_Data.txt", delimiter='\t', skipinitialspace=True)
    df_slip.columns = df_slip.columns.str.strip()  # Clean header names

    added_va = False
    added_vu = False
    added_vs = False

    for idx, row in df_slip.iterrows():
        y1 = row['y1']
        y2 = row['y2']
        va = row['V_a']
        vu = row['V_u']
        vs = row['V_s']

        fig.add_trace(go.Scatter(
            x=[va, va],
            y=[y1, y2],
            mode='lines',
            line=dict(color='green', width=2.0),
            showlegend=not added_va,
            name='Va[ft/min]'
        ), row=1, col=3)
        added_va = True

        fig.add_trace(go.Scatter(
            x=[vu, vu],
            y=[y1, y2],
            mode='lines',
            line=dict(color='red', width=1.25),
            showlegend=not added_vu,
            name='Vu[ft/min]'
        ), row=1, col=3)
        added_vu = True

        fig.add_trace(go.Scatter(
            x=[vs, vs],
            y=[y1, y2],
            mode='lines',
            line=dict(color='black', width=1.00),
            showlegend=not added_vs,
            name='Vs[ft/min]'
        ), row=1, col=3)
        added_vs = True

    fig.update_xaxes(title_text="Velocity [ft/min]", row=1, col=3)
    fig.update_yaxes(autorange="reversed", row=1, col=3)  # No Y-axis title

    ### Subplot 4: Combined Plot (WBS & DS: WB Schematic & Drill.-String) ###
    # Read WBS data from Plot_wbs_Data.txt
    left_df = read_section_from_file("./Plot_wbs_Data.txt", "Left Plot Data (X vs Y):")
    right_df = read_section_from_file("./Plot_wbs_Data.txt", "Right Plot Data (X vs Y):")
    # Read DS data from Plot_ds_Data.txt (assumes header: i x1 x2 y1 y2 x3 x4)
    df_ds = pd.read_csv("./Plot_ds_Data.txt", sep=r'\s+')

    # Create an HSV colormap (64 colors) using the new interface.
    cmap = matplotlib.colormaps["hsv"].resampled(64)

    fig.add_trace(go.Scatter(
        x=left_df["X"],
        y=left_df["Y"],
        mode="lines+markers",
        name="WBS Left"
    ), row=1, col=4)
    fig.add_trace(go.Scatter(
        x=right_df["X"],
        y=right_df["Y"],
        mode="lines+markers",
        name="WBS Right"
    ), row=1, col=4)

    added_ds_left = False
    added_ds_right = False

    for idx, row in df_ds.iterrows():
        i_val = row['i']
        x1 = row['x1']
        x2 = row['x2']
        y1 = row['y1']
        y2 = row['y2']
        x3 = row['x3']
        x4 = row['x4']
        # Compute mirrored values for right-hand side.
        x1b = -x1
        x2b = -x2
        x3b = -x3
        x4b = -x4
        # Compute line width based on tool wall thickness.
        tool_wall_th = x1 - x3
        if tool_wall_th <= 2:
            lw = tool_wall_th
        elif tool_wall_th <= 5:
            lw = tool_wall_th / 1.25
        else:
            lw = tool_wall_th / 2.5
        # Determine color (MATLAB uses map(i*3,:))
        color_index = int((i_val * 3 - 1) % 64)
        c_val = cmap(color_index)
        color_str = f"rgba({int(c_val[0] * 255)},{int(c_val[1] * 255)},{int(c_val[2] * 255)},{c_val[3]})"

        # DS left-hand side segments
        show_left = not added_ds_left
        if not added_ds_left:
            added_ds_left = True
        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode='lines',
            line=dict(color=color_str, width=lw),
            legendgroup="DS Left",
            showlegend=show_left,
            name="DS Left-hand side"
        ), row=1, col=4)
        fig.add_trace(go.Scatter(
            x=[x3, x4],
            y=[y1, y2],
            mode='lines',
            line=dict(color=color_str, width=lw),
            legendgroup="DS Left",
            showlegend=False
        ), row=1, col=4)

        # DS right-hand side segments
        show_right = not added_ds_right
        if not added_ds_right:
            added_ds_right = True
        fig.add_trace(go.Scatter(
            x=[x1b, x2b],
            y=[y1, y2],
            mode='lines',
            line=dict(color=color_str, width=lw),
            legendgroup="DS Right",
            showlegend=show_right,
            name="DS Right-hand side"
        ), row=1, col=4)
        fig.add_trace(go.Scatter(
            x=[x3b, x4b],
            y=[y1, y2],
            mode='lines',
            line=dict(color=color_str, width=lw),
            legendgroup="DS Right",
            showlegend=False
        ), row=1, col=4)

    fig.update_xaxes(title_text="WB Radius x2 [inch]", row=1, col=4)
    fig.update_yaxes(autorange="reversed", row=1, col=4)  # No Y-axis title

    # Overall layout settings.
    fig.update_layout(
        title="SPP, ECD, Slip Vel. & Geom.-Rep. VS. MD Plots Panel",
        width=1400,
        height=600,
        showlegend=True
    )

    # fig.show()
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def read_section_from_file(filename, section_name):
    """
    Reads a section from the file starting immediately after a line containing
    section_name and continuing until a blank line is encountered.
    Returns a DataFrame.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    section_lines = []
    in_section = False
    for line in lines:
        if section_name in line:
            in_section = True
            continue
        if in_section:
            if line.strip() == "":
                break
            section_lines.append(line)
    data_str = "".join(section_lines)
    try:
        df = pd.read_csv(StringIO(data_str), sep='\t')
    except Exception:
        df = pd.read_csv(StringIO(data_str), sep=r'\s+')
    return df
