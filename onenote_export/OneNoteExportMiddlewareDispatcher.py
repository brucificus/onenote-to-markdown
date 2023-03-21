import functools
from typing import Generic, Callable

from onenote import OneNoteApplication, OneNoteNode
from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewareContextFactory import OneNoteExportMiddlewareContextFactory
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
from .SimpleOneNoteExportMiddlewareFactory import SimpleOneNoteExportMiddlewareFactory
from .type_variables import TReturn


class OneNoteExportMiddlewareDispatcher(OneNoteExportMiddleware[OneNoteApplication, TReturn], Generic[TReturn]):
    def __init__(self,
                 combine_returns: Callable[[TReturn, TReturn], TReturn],
                 middleware_context_factory: OneNoteExportMiddlewareContextFactory,
                 *,
                 middlewares_by_type: dict[type, tuple[OneNoteExportMiddleware[OneNoteNode, TReturn], ...]] = {},
                 simple_middleware_factory: SimpleOneNoteExportMiddlewareFactory = None,
                 traverse_children_depth_first: bool = True,
                 ):
        self._combine_returns = combine_returns
        self._middleware_context_factory = middleware_context_factory

        simple_middleware_factory = simple_middleware_factory or SimpleOneNoteExportMiddlewareFactory()
        traverse_children = functools.partial(self._traverse_children, depth_first=traverse_children_depth_first)

        self._pipelines: dict[type, OneNoteExportMiddleware] = {}
        for exact_node_type, new_middlewares_for_type in middlewares_by_type.items():
            extant_middleware_for_type = (self._pipelines[exact_node_type],) if exact_node_type in self._pipelines else ()
            combined_new_middleware_for_type = simple_middleware_factory.chain(
                extant_middleware_for_type
                + new_middlewares_for_type
                + (traverse_children,)
            )
            self._pipelines[exact_node_type] = combined_new_middleware_for_type

    def __call__(self, context: OneNoteExportMiddlewareContext[OneNoteApplication], next_middleware: OneNoteExportMiddlewarePartial[OneNoteApplication, TReturn]) -> TReturn:
        return self._get_middleware_by_best_type_fit(context.node)(context, next_middleware)

    def _get_middleware_by_best_type_fit(self, node: OneNoteNode) -> OneNoteExportMiddleware[OneNoteNode, TReturn]:
        for node_type, middleware in self._pipelines.items():
            if node is node_type:
                return middleware

        for node_type, middleware in self._pipelines.items():
            if isinstance(node, node_type):
                return middleware

        raise TypeError(f'No middleware found for node of type {type(node)}')

    def _traverse_children(self, context: OneNoteExportMiddlewareContext[OneNoteNode], next_middleware: OneNoteExportMiddlewarePartial[OneNoteNode, TReturn], depth_first: bool = True) -> TReturn:
        accumulated_middleware_return = None

        if not depth_first:
            accumulated_middleware_return = next_middleware(context)

        for child in context.node.children:
            child_context = self._middleware_context_factory.create_context_for_traversal_transition_to_child(context, child)
            pipeline_for_child = self._get_middleware_by_best_type_fit(child_context.node)

            current_child_return = pipeline_for_child(child_context, lambda context: None)
            accumulated_middleware_return = self._combine_returns(accumulated_middleware_return, current_child_return)

        if depth_first:
            next_middleware_return = next_middleware(context)
            accumulated_middleware_return = self._combine_returns(accumulated_middleware_return, next_middleware_return)

        return accumulated_middleware_return
