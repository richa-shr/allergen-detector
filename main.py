# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from agent.graph import allergen_graph
# from dotenv import load_dotenv
# from concurrent.futures import ThreadPoolExecutor
# import asyncio
# import traceback

# load_dotenv()

# app = FastAPI()
# executor = ThreadPoolExecutor(max_workers=2)

# class ProductRequest(BaseModel):
#     url: str
#     allergens: list[str]

# @app.get("/")
# def root():
#     return {"status": "allergen detector is running"}

# @app.post("/check")
# async def check_product(request: ProductRequest):
#     loop = asyncio.get_event_loop()  # ← was missing
#     try:
#         result = await loop.run_in_executor(
#             executor,
#             lambda: allergen_graph.invoke({
#                 "url": request.url,
#                 "user_allergens": request.allergens,
#                 "ingredients": None,
#                 "is_safe": None,
#                 "allergens_found": None,
#                 "reason": None,
#                 "alternative_urls": None,
#                 "safe_alternatives": None
#             })
#         )
#         return {
#             "url": request.url,
#             "is_safe": result["is_safe"],
#             "allergens_found": result["allergens_found"],
#             "reason": result["reason"],
#             "safe_alternatives": result.get("safe_alternatives", [])
#         }
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import allergen_graph_phase1, allergen_graph_phase2
from dotenv import load_dotenv
import asyncio
import traceback
import threading
import uuid

load_dotenv()

app = FastAPI()

# In-memory job store
jobs = {}

class ProductRequest(BaseModel):
    url: str
    allergens: list[str]

@app.get("/")
def root():
    return {"status": "allergen detector is running"}

@app.post("/start-check")
async def start_check(request: ProductRequest):
    """Starts the check and returns a job_id immediately"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "loading"}

    def run_job():
        try:
            # Phase 1 — scrape + detect
            result = allergen_graph_phase1.invoke({
                "url": request.url,
                "user_allergens": request.allergens,
                "ingredients": None,
                "is_safe": None,
                "allergens_found": None,
                "reason": None,
                "alternative_urls": None,
                "safe_alternatives": None
            })

            jobs[job_id] = {
                "status": "allergen_checked",
                "url": request.url,
                "is_safe": result["is_safe"],
                "allergens_found": result["allergens_found"],
                "reason": result["reason"],
                "safe_alternatives": []
            }

            # Phase 2 — only if allergen found
            if result["is_safe"] is False:
                result2 = allergen_graph_phase2.invoke({
                    "url": request.url,
                    "user_allergens": request.allergens,
                    "ingredients": None,
                    "is_safe": None,
                    "allergens_found": None,
                    "reason": None,
                    "alternative_urls": None,
                    "safe_alternatives": None
                })
                jobs[job_id]["safe_alternatives"] = result2.get("safe_alternatives", [])

            jobs[job_id]["status"] = "done"

        except Exception as e:
            print(traceback.format_exc())
            jobs[job_id] = {"status": "error", "error": str(e)}

    threading.Thread(target=run_job).start()
    return {"job_id": job_id}

@app.get("/job-status/{job_id}")
async def job_status(job_id: str):
    """Popup polls this to get current status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]