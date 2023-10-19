from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_dbapi

from app.core.logger import logger_factory

logger = logger_factory(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers the exception handlers for the FastAPI App.

    Args:
        app: the :class:`FastAPI` instance on which to register the exception handlers
    """
    #add connection is closed handler in case bdd is down
    @app.exception_handler(ConnectionRefusedError)
    async def ConnectionRefusedError_handler(request: Request, exc: ConnectionRefusedError) -> JSONResponse:
        msg = "Failed to connect to the Database"
        logger.critical(msg)
        return JSONResponse(status_code=500, content={"details": msg})

    @app.exception_handler(IntegrityError)
    async def UniqueViolationError_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        if isinstance(exc.orig, AsyncAdapt_asyncpg_dbapi.IntegrityError):
            msg = " ".join(str(exc.orig).split("\n")[1].split(" ")[3:]).replace("(", "").replace(")", "")
            logger.debug(exc.orig)  # type: ignore
            content = {
                "detail": [
                    {
                        "type": "value_error",
                        "msg": msg,
                    }
                ]
            }
            return JSONResponse(status_code=400, content=content)
        return JSONResponse(status_code=500, content="Internal Server Error")
