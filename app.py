import json
from dataclasses import dataclass

import pandas as pd
import plotly
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, url_for
from flask import request, flash
from flask_caching import Cache
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length

from src.api import HousePriceIndexAPI
from src.dataframe import InputDataFrame
from src.forecaster import apply

app = Flask(__name__)

TEST_POSTCODE = "W42BE"
app.config['SECRET_KEY'] = '2372b3fd7ba315c374828f3a34f5bd0acae3d0019dcc058c'

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app.config.from_mapping(config)
cache = Cache(app)

postcodes = [{'postcode': TEST_POSTCODE}]


def dataframes(test: bool = True, postcode: str = TEST_POSTCODE, ) -> dict:
    """generate all the dataframes as a dictionary in test or real mode"""
    if test:
        df = pd.read_csv("resources/example.csv")
        in_df = InputDataFrame(dataframe=df)
        return apply(in_df)
    else:
        df = HousePriceIndexAPI(postcode).combine_dataframe()
        in_df = InputDataFrame(dataframe=df)
        return apply(in_df)


class PostCodeForm(FlaskForm):
    postcode = StringField('postcode', validators=[InputRequired(),
                                                   Length(min=5, max=100)])


@dataclass
class Postcode:
    postcode: str


@app.route('/', methods=["GET", "POST"])
def postcode():
    form = PostCodeForm(request.form)
    if request.method == 'POST':
        flash('Thanks for submitting')
        Postcode.postcode = form.postcode
        return redirect(url_for('index'))
    return render_template("postcode.html",form=form)


@app.route('/index', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/index/chart1')
@cache.cached(timeout=600)
def chart1():
    postcode_html = str(Postcode.postcode)
    soup = BeautifulSoup(postcode_html, 'html.parser')
    postcode = soup.find('input')['value']
    data_dict = dataframes(postcode=str(postcode), test=False)
    region = data_dict["region"]
    df_global = data_dict["hpi_global_df"]
    df_regional = data_dict["hpi_regional_df"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_global["ds"], y=df_global["y"], name="Actual (global)", mode="lines"))
    fig.add_trace(go.Scatter(x=df_global["ds"], y=df_global["yhat1"], name="Forecasted (global)", mode="lines"))
    fig.add_trace(go.Scatter(x=df_regional["ds"], y=df_regional["y"], name=f"Actual ({region})", mode="lines"))
    fig.add_trace(go.Scatter(x=df_regional["ds"], y=df_regional["yhat1"], name=f"Forecasted ({region})", mode="lines"))
    fig.update_layout(
        title="House Price Index over time", xaxis_title="Time", yaxis_title="House Price Index"
    )

    # fig = px.line(df, x="ds", y=df.columns[1, 2]).update_layout(xaxis_title="Time", yaxis_title="House Price Index")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "House Price Index"
    description = """
    The data has been trained, modeled and forecasted using the latest machine learning technology:
    https://neuralprophet.com/html/index.html
    
    House Price Index:
    For the UK HPI , the standard average house price is calculated by taking the average (geometric mean) price
    in January 2015 and then recalculating it in accordance with the index change 
    back in time and forward to the present day. A 3 month moving average has been applied to estimates 
    below the regional level.
    """
    return render_template('graph.html', graphJSON=graphJSON, header=header, description=description)


@app.route('/index/chart2')
@cache.cached(timeout=600)
def chart2():
    postcode_html = str(Postcode.postcode)
    soup = BeautifulSoup(postcode_html, 'html.parser')
    postcode = soup.find('input')['value']
    data_dict = dataframes(postcode=str(postcode), test=False)
    region = data_dict["region"]
    df_global = data_dict["prices_global_df"]
    df_regional = data_dict["prices_regional_df"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_regional["ds"], y=df_global["y"], name="Actual (UK)", mode="lines"))
    fig.add_trace(go.Scatter(x=df_global["ds"], y=df_global["yhat1"], name="Forecasted (UK)", mode="lines"))
    fig.add_trace(go.Scatter(x=df_regional["ds"], y=df_regional["y"], name=f"Actual ({region})", mode="lines"))
    fig.add_trace(go.Scatter(x=df_regional["ds"], y=df_regional["yhat1"], name=f"Forecasted ({region})", mode="lines"))
    fig.update_layout(
        title="Average Price over time", xaxis_title="Time", yaxis_title="£"
    )

    # fig = px.line(df, x="ds", y=df.columns[1, 2]).update_layout(xaxis_title="Time", yaxis_title="£")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Average Prices"
    description = """
    The data has been trained, modeled and forecasted using the latest machine learning technology:
    https://neuralprophet.com/html/index.html
    """
    return render_template('graph.html', graphJSON=graphJSON, header=header, description=description)
