# chama a lógica do FastAPI para criar uma aplicação web e devolve a resposta

from fastapi import FastAPI 
from sonda_marte_api.rotas.endpoints_probe import router # Importa os modelos definidos para a API

app = FastAPI(
    title="API da Sonda em Marte",
    description="Nessa API é possivel controlar a sonda em Marte, recebendo comandos e retornando status.",
    version="1.0.0",
)  

app.include_router(router)  # Inclui as rotas definidas para a sonda
