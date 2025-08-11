from fastapi import FastAPI, Response, APIRouter
from scripts.dataAnalysis import DataAnalysis
from scripts.linearModelsResearch import SKLearnModelsResearch


analyser = DataAnalysis()
sklearn_researcher = SKLearnModelsResearch()
app = FastAPI()
plot = APIRouter()

@app.get('/health')
def heathcheck():
    return {"status": "healthy"}

@app.get('/dfhead/{t_name}')
async def get_dfhead(t_name: str | None = None):
    return  analyser.get_dfhead(t_name)


@plot.get('/{f_name}/{t_name}')
async def get_main_plot(f_name: str, t_name: str | None = None):
    match f_name:
        case "main_plot":
            return Response(content=analyser.get_main_plot(t_name, "main_plot"), media_type="image/png")
        case 'seasonal_decompose': 
            return Response(content=analyser.get_seasonal_decompose_plot(t_name, 'seasonal_decompose'), media_type="image/png")
        case 'test_seasonality': 
            return Response(content=analyser.get_test_seasonality_plot(t_name, 'test_seasonality'), media_type="image/png")
        case 'month_boxplots': 
            return Response(content=analyser.get_month_boxplots(t_name, 'month_boxplots'), media_type="image/png")
        case 'acf_pacf': 
            return Response(content=analyser.get_acf_pacf_plots(t_name, 'acf_pacf'), media_type="image/png")
        case 'lag_plots': 
            return Response(content=analyser.get_lag_plots(t_name, 'lag_plots'), media_type="image/png")
        case 'detrended_plot':
            return Response(content=analyser.get_detrended_plot(t_name, 'detrended_plot'), media_type="image/png")
        case 'lasso_test':
            return Response(content=sklearn_researcher.lasso_test(t_name, 'detrended_plot'), media_type="image/png")


@app.get('/adf_test/{t_name}')
async def get_adf_test(t_name: str | None = None):
    return analyser.get_adf_test(t_name)

app.include_router(plot, prefix='/plot')

if __name__ == "__main__":
    app