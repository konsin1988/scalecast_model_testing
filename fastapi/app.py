from fastapi import FastAPI, Response
import pandas as pd
import os

from scripts.dataAnalysis import DataAnalysis


analyser = DataAnalysis()
app = FastAPI()

@app.get('/health')
def heathcheck():
    return {"status": "healthy"}

@app.get('/dfhead/{dname}')
async def get_dfhead(dname: str | None = None):
    return  analyser.get_dfhead(dname)

@app.get('/main_plot/{dname}')
async def get_main_plot(dname: str | None = None):
    return Response(content=analyser.get_main_plot(dname, 'main'), media_type="image/png")

@app.get('/seasonal_decompose/{dname}')
async def get_seasonal_decompose_plot(dname: str | None = None):
    return Response(content=analyser.get_seasonal_decompose_plot(dname, 'seasonal'), media_type="image/png")
