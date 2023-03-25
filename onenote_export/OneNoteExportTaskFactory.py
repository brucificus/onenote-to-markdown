from logging import Logger
from typing import Dict, Iterable, Callable, Optional

from onenote import OneNoteNode, OneNoteApplication, OneNotePage
from .OneNoteExportTaskContext import OneNoteExportTaskContext
from .OneNoteExportTaskContextFactory import OneNoteExportTaskContextFactory
from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext
from .OneNotePageExporter import OneNotePageExporter
from .simple_injector import prepare_action_params, InjectableParameter


class OneNoteExportTaskFactory:
    def __init__(self,
                 context_factory: OneNoteExportTaskContextFactory,
                 should_export: Callable[[OneNoteNode], bool] = lambda node: True,
                 ):
        if not isinstance(context_factory, OneNoteExportTaskContextFactory):
            raise ValueError(f'export_context_factory must be an instance of OneNoteExportMiddlewareContextFactory, not {type(context_factory)}')
        self._contexts: Dict[OneNoteNode, OneNoteExportTaskContext[OneNoteNode]] = {}
        self._context_factory = context_factory
        self._should_export = should_export

    def _get_or_create_context(self, node: OneNoteNode) -> OneNoteExportTaskContext[OneNoteNode]:
        if node not in self._contexts:
            if isinstance(node, OneNoteApplication):
                new_context = self._context_factory.create_context_for_application(node)
            else:
                parent_context = self._get_or_create_context(node.parent)
                new_context = self._context_factory.create_context_for_traversal_transition_to_child(parent_context, node)
            self._contexts[node] = new_context
            return new_context
        return self._contexts[node]

    def create_task(self, node: OneNoteNode, prerequisites: Iterable[OneNoteExportTaskBase]) -> Optional[OneNoteExportTaskBase]:
        get_context = lambda: self._get_or_create_context(node)

        if not self._should_export(node):
            return None
        if isinstance(node, OneNotePage):
            task_class = OneNotePageExporter
            get_logger = lambda: get_context().get_logger(f"{__name__}.{task_class.__name__}")
            (task_ctor_args, task_ctor_kwargs) = prepare_action_params(
                task_class,
                (
                    InjectableParameter(('context', 'ctx', 'c'), (OneNoteExportTaskContext, OneNotePageExportTaskContext), get_context),
                    InjectableParameter(('logger', 'log', 'l'), (Logger,), get_logger),
                ),
                should_try_injection=lambda param: param.name != 'prerequisites'
            )
            action = task_class(*task_ctor_args, **task_ctor_kwargs, prerequisites=prerequisites)
            return action
        return None
