# async_task_helpers
Simple asynchronous task helpers

## How to install
```shell
pip install async_task_helpers
```

## Features
### Loop tasks
```python
from async_task_helpers import loop

@loop(minutes=5, seconds=30)
async def loop_example():
    # This LoopTask will run in every 5 minute and 30 seconds.
    await some_async_task()
    await some_async_task2()
```


### Asynchronous Callbacks
```python
import asyncio
from async_task_helpers import async_callback_handler

async def universe_last_answer():
    print('Universe`s a whole and entire, final answer is...')
    await asyncio.sleep(1)
    print('42!')
    return 42


async def async_callback(result):
    await asyncio.sleep(5)
    print(f'I got the result of {result}!')
    

task = asyncio.create_task(
    async_callback_handler(
        universe_last_answer,
        async_callback
    ),
    name='Async Callback Test'
)
```