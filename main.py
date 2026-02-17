from fastapi import FastAPI
from finance_tracker import mongodb
from finance_tracker import transaction_router
from finance_tracker import category_router

class FinanceAPI:
    def __init__(self):
        try:
            self.app = FastAPI(title="Finance Tracker API")
            self.app.include_router(transaction_router)
            self.app.include_router(category_router)
            self.app.add_event_handler("startup", self.startup)
            self.app.add_event_handler("shutdown", self.shutdown)
        except Exception as e:
            print("App Init Error:", e)

    async def startup(self):
        try:
            await mongodb.connect()
        except Exception as e:
            print("Startup Error:", e)

    async def shutdown(self):
        try:
            await mongodb.close()
        except Exception as e:
            print("Shutdown Error:", e)

    def get_app(self):
        return self.app


api = FinanceAPI()
app = api.get_app()
