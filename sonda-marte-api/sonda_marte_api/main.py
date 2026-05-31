from fastapi import FastAPI 
from sonda_marte_api.routers.endpoints_probe import router

app = FastAPI(
    title="API da Sonda em Marte",
    description="Nessa API é possivel controlar a sonda em Marte, recebendo comandos e retornando status.",
    version="1.0.0",
)  

app.include_router(router)
