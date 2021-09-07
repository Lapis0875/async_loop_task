from typing import Union, Callable, Coroutine, Any

__all__ = (
    'AnyNumber',
    'Function',
    'CoroutineFunction',
    'AnyFunction',
)

AnyNumber = Union[int, float]
Function = Callable[..., Any]
CoroutineFunction = Callable[..., Coroutine]
AnyFunction = Union[Function, CoroutineFunction]
