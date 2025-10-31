from typing import Annotated,List, Union

from fastapi import FastAPI , Path ,Body,Cookie,FastApi,Form

from pydantic import BaseModel ,Field

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default = None, title = "Tje description of tje item", max_length=300
    )
    price: float = Field(gt = 0,description="The price must be greater thon zero")
    tax: Union[float, None] = None
    tags: List[str] = []


app = FastAPI()

@app.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    return{"username":username}


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}
'''
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"}
]
'''
@app.get("/items/")
async def read_items(ads_id:Annotated[str | None, Cookie()]):
    return{"ads_id": ads_id}

@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item

'''
@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get",ge=0,le=1000)], 
    q:str | None = None,
    item: Item | None = None):
                      
    results ={"item_id": item_id}
    if q:
        results.update({"q":q})
    if item:
        results.update({"item": item})
        return results
'''

@app.put("/items/{item_id}")
async def update_item(item_id:int,item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item" : item}
    return results
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default = None, title = "Tje description of tje item", max_length=300
    )
    price: float = Field(gt = 0,description="The price must be greater thon zero")
    tax: float | None = None