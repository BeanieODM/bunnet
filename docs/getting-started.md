# Getting started

## Installing bunnet

You can simply install Bunnet from the [PyPI](https://pypi.org/project/bunnet/):

### PIP

```shell
pip install bunnet
```

### Poetry

```shell
poetry add bunnet
```

## Initialization

Getting Bunnet setup in your code is really easy:

1.  Write your database model as a Pydantic class but use `bunnet.Document` instead of `pydantic.BaseModel`.
2.  Initialize Motor, as Bunnet uses this as an async database engine under the hood.
3.  Call `bunnet.init_bunnet` with the Motor client and list of Bunnet models

The code below should get you started and shows some of the field types that you can use with bunnet.

```python
from typing import Optional

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from bunnet import Document, Indexed, init_bunnet


class Category(BaseModel):
    name: str
    description: str


# This is the model that will be saved to the database
class Product(Document):
    name: str                          # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(float)              # You can also specify that a field should correspond to an index
    category: Category                 # You can include pydantic models as well


# Call this from within your event loop to get bunnet setup.
async def init():
    # Create Motor client
    client = AsyncIOMotorClient("mongodb://user:pass@host:27017")

    # Init bunnet with the Product document class
    await init_bunnet(database=client.db_name, document_models=[Product])
```
