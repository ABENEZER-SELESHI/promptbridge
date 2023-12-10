from fastapi import FastAPI

from promptbridge import __version__
from promptbridge.config import load_config
from promptbridge.endpoints.system import router as system_router
from promptbridge.logger import setup_logging

app = FastAPI(title="PromptBridge", version=__version__)
config = load_config()
setup_logging(config.debug)
app.include_router(system_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "promptbridge", "version": __version__}
