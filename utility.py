import json
import plotly
import plotly.express as px

def get_plotly_plot():
    wide_df = px.data.medals_wide()
    figure = px.bar(wide_df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
