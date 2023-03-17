import functools
from typing import Generic, Callable

from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
from .type_variables import TNode, TReturn


class SimpleOneNoteExportMiddlewareFactory(Generic[TNode, TReturn]):
    @staticmethod
    def _execute_middlewares(
        middlewares: tuple[OneNoteExportMiddleware[TNode, TReturn], ...],
        context: OneNoteExportMiddlewareContext[TNode],
        next_middleware: OneNoteExportMiddlewarePartial[TNode, TReturn]
    ) -> TReturn:
        if not middlewares:
            return next_middleware(context)

        for middleware in reversed(middlewares):
            if not middleware:
                continue
            next_middleware = functools.partial(middleware, next_middleware=next_middleware)

        return next_middleware(context)

    def chain(self,
              middlewares: tuple[OneNoteExportMiddleware[TNode, TReturn], ...]
              ) -> OneNoteExportMiddleware[TNode, TReturn]:
        """Creates and returns a middleware that represents a chain of middlewares constructed from those provided,
        ordered from left to right.
        """
        return functools.partial(SimpleOneNoteExportMiddlewareFactory._execute_middlewares, middlewares)


    def before(self,
               action: OneNoteExportMiddlewarePartial[TNode, TReturn]
               ) -> OneNoteExportMiddleware[TNode, TReturn]:
        """Creates and returns a middleware that executes the provided 'action' before the next middleware in the current
        chain.
        """
        def middleware(
            context: OneNoteExportMiddlewareContext[TNode],
            next_middleware: OneNoteExportMiddlewarePartial[TNode, TReturn]
        ) -> TReturn:
            action(context)  # TODO: Don't throw away this TReturn. Accumulate/combine TReturn values and return result.
            return next_middleware(context)
        return middleware


    def preempt(self,
                action: OneNoteExportMiddlewarePartial[TNode, TReturn]
                ) -> OneNoteExportMiddleware[TNode, TReturn]:
        """Creates and returns a middleware that executes the given 'action' but never executes the following
        middlewares in the current chain.
        """
        def middleware(
            context: OneNoteExportMiddlewareContext[TNode],
            next_middleware: OneNoteExportMiddlewarePartial[TNode, TReturn]
        ) -> TReturn:
            return action(context)
        return middleware

    def either_or(self,
                  condition: Callable[[OneNoteExportMiddlewareContext[TNode]], bool],
                  middleware_if: OneNoteExportMiddleware[TNode, TReturn],
                  middleware_else: OneNoteExportMiddleware[TNode, TReturn]
                  ) -> OneNoteExportMiddleware[TNode, TReturn]:
        """Creates and returns a middleware that executes the provided middleware 'middleware_if' when 'condition' evaluates
        to true, otherwise executes the provided 'middleware_else' middleware.
        """
        def middleware(
            context: OneNoteExportMiddlewareContext[TNode],
            next_middleware: OneNoteExportMiddlewarePartial[TNode, TReturn]
        ) -> TReturn:
            if condition(context):
                return middleware_if(context, next_middleware)
            return middleware_else(context, next_middleware)
        return middleware



    def try_finally(self,
                    middleware_try: OneNoteExportMiddleware[TNode, TReturn],
                    action_finally: OneNoteExportMiddlewarePartial[TNode, TReturn],
                    ) -> OneNoteExportMiddleware[TNode, TReturn]:
        """Creates and returns a middleware that executes the provided 'middleware_try' (with the rest of its chain) and
        then always executes the provided 'action_finally' afterward, regardless of whether an exception was thrown.
        """
        def middleware(
            context: OneNoteExportMiddlewareContext[TNode],
            next_middleware: OneNoteExportMiddlewarePartial[TNode, TReturn]
        ) -> TReturn:
            try:
                return middleware_try(context, next_middleware)
            finally:
                action_finally(context)  # TODO: Don't throw away this TReturn. Accumulate/combine TReturn values and return result.
        return middleware
