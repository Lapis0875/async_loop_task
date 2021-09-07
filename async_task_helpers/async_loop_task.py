import asyncio
import typing
from datetime import timedelta
from sys import stderr

from .type_hint import CoroutineFunction


__all__ = (
    'LoopTask',
    'loop'
)


T = typing.TypeVar('T')


class ZeroSecondsTaskNotSupported(Exception):
    def __init__(self):
        super(ZeroSecondsTaskNotSupported, self).__init__('LoopTask with 0 seconds delay is not supported due to performance issue.')


class LoopTask:
    __slots__ = (
        'loop',
        '_callback',
        '_args',
        '_kwargs',
        '_ignored_exceptions',
        '_task',
        '_injected',
        '_days',
        '_hours',
        '_minutes',
        '_seconds',
        '_running',
        '_before_hook',
        '_after_hook'
    )

    def __init__(self, coro: CoroutineFunction, args, kwargs, days: int, hours: int, minutes: int, seconds: int):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()
        # Callback info
        self._callback = coro
        self._args = args
        self._kwargs = kwargs or {}     # You can use keyword-arguments dictionary as namespace to pass on callback functions (before&after invoke, callback)
        self._ignored_exceptions: list[typing.Type[Exception]] = []
        self._task = None
        self._injected: object = None   # Used on LoopTasks in object to resolve 'self' parameter.

        # Looping delay info
        self._days = days
        self._hours = hours
        self._minutes = minutes
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds

        # Flags
        self._running: bool = False

        # Hook coroutine functions.
        self._before_hook: typing.Optional[CoroutineFunction] = None
        self._after_hook: typing.Optional[CoroutineFunction] = None

    @property
    def total_delay(self) -> timedelta:
        return timedelta(days=self._days, hours=self._hours, minutes=self._minutes, seconds=self._seconds)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def args(self) -> tuple:
        return self._args

    @args.setter
    def args(self, new) -> None:
        self._args = new

    @property
    def kwargs(self) -> typing.Mapping:
        return self._kwargs

    @kwargs.setter
    def kwargs(self, new) -> None:
        self._kwargs = new

    def __get__(self, obj: T, objtype: typing.Type[T]) -> 'LoopTask':
        # Descriptor method used to define objects like `property`
        # Defined to support object.some_task (type: LoopTask) work with 'self' parameter.
        if obj is None:
            return self

        # logger.debug(f'Injecting `self` attribute of object {obj} in {self.task_name}')
        copy: LoopTask = LoopTask(
            coro=self._callback,
            args=self._args,
            kwargs=self._kwargs,
            days=self._days,
            hours=self._hours,
            minutes=self._minutes,
            seconds=self._seconds,
        )
        copy._injected = obj
        copy._before_hook = self._before_hook
        copy._after_hook = self._after_hook
        setattr(obj, self._callback.__name__, copy)
        return copy

    def __call__(self, *args, **kwargs) -> typing.Coroutine:
        """
        Call callback coroutine function without any hooks.
        :param args:
        :param kwargs:
        """
        return self._callback(*args, **kwargs)

    @property
    def task_name(self) -> str:
        return f'LoopTask({self._callback.__name__}, delay={self.total_delay})'

    def before_invoke(self, coro: CoroutineFunction):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError(f'LoopTask.before_invoke must be coroutine function, not {type(coro)}.')
        self._before_hook = coro

    def after_invoke(self, coro: CoroutineFunction):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError(f'LoopTask.after_invoke must be coroutine function, not {type(coro)}.')
        self._after_hook = coro

    async def _handle_exceptions(self, exc_type: typing.Type[Exception], exc_value: Exception, traceback):
        """
        Default exception handler. Can be replaced by `@LoopTask.handle_exception` decorator.
        :param exc_type: Exception type.
        :param exc_value: Exception object.
        :param traceback: Exception traceback object.
        """
        print(f'{exc_type.__name__} exception has been occurred while running youtube.LoopTask! Gracefully stop task.', file=stderr)
        self.cancel()

    async def _run(self):
        args = self._args or tuple()
        kwargs = self._kwargs or {}
        # print(f'{self.task_name} is started.')

        if self._before_hook:
            # print(f'{self.task_name}.before_hook called.')
            coro = self._before_hook(self._injected, *args, **kwargs) if self._injected is not None else self._before_hook(*args, **kwargs)
            await coro

        while True:
            try:
                # print(f'{self.task_name}.callback called.')
                coro = self._callback(self._injected, *args, **kwargs) if self._injected is not None else self._callback(*args, **kwargs)
                await coro
                # print(f'{self.task_name}.callback completed. Wait for next execution.')
            except self._ignored_exceptions as e:
                # print(f'{self.task_name} >>> Exception raised, but it is handled.', file=stderr)
                await self._handle_exceptions(e.__class__, e, e.__traceback__)
            finally:
                if not self._running:
                    # print(f'{self.task_name} is canceled. Break callback loop.')
                    break
                # print(f'{self.task_name} : sleep for {self.total_delay.total_seconds()} seconds.')
                await asyncio.sleep(delay=self.total_delay.total_seconds())

        if self._after_hook:
            # print(f'{self.task_name}.after_hook called.')
            coro = self._after_hook(self._injected, *args, **kwargs) if self._injected is not None else self._after_hook(*args, **kwargs)
            await coro
        # print(f'{self.task_name} is now closed.')

    def start(self, *args, **kwargs):
        if args:
            if self._args:
                self._args += args
            else:
                self._args = args
        if kwargs:
            if self._kwargs:
                self._kwargs.update(kwargs)
            else:
                self._kwargs = kwargs
        self._running = True
        self._task = self.loop.create_task(self._run(), name=self.task_name)
        return self._task

    def cancel(self):
        self._running = False


def loop(days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
    def wrapper(coro: CoroutineFunction):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('YoutubeEventLoop.LoopTask.callback must be coroutine function.')
        if not any((days, hours, minutes, seconds)):
            # total_delay = 0. Why we use this callback as LoopTask? just call it.
            raise ZeroSecondsTaskNotSupported()

        task: LoopTask = LoopTask(coro, None, None, days, hours, minutes, seconds)
        return task
    return wrapper
