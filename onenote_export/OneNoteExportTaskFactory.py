import functools
import inspect
from logging import Logger
from typing import Dict, Iterable, Callable, Optional, Union

from onenote import OneNoteNode, OneNoteApplication, OneNotePage
from .OneNoteExportTaskContext import OneNoteExportTaskContext
from .OneNoteExportTaskContextFactory import OneNoteExportTaskContextFactory
from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNoteExportTaskLiteral import OneNoteExportTaskLiteral
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext
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

    def create_default_for_node_type(self, node: OneNoteNode, prerequisites: Iterable[OneNoteExportTaskBase]) -> Optional[OneNoteExportTaskBase]:
        if not self._should_export(node):
            return None
        if isinstance(node, OneNotePage):
            from .OneNotePageExporter import OneNotePageExporter
            task_class = OneNotePageExporter
            return self.create_from_spec(node, task_spec=task_class, prerequisites=prerequisites)
        return None

    def create_from_spec(self, node: OneNoteNode, task_spec: Union[Callable, OneNoteExportTaskBase], prerequisites: Iterable[OneNoteExportTaskBase]) -> OneNoteExportTaskBase:
        spec_is_task_class = inspect.isclass(task_spec) and issubclass(task_spec, OneNoteExportTaskBase)
        if not spec_is_task_class and not isinstance(task_spec, Callable):
            raise ValueError(f'Requires a OneNoteExportTaskBase subclass or callable, not {type(task_spec)}')

        get_context = lambda: self._get_or_create_context(node)
        get_logger = lambda: get_context().get_logger(f"{__name__}.{task_spec.__name__}")

        (task_ctor_args, task_ctor_kwargs) = prepare_action_params(
            task_spec,
            (
                InjectableParameter(('context', 'ctx', 'c'), (OneNoteExportTaskContext, OneNotePageExportTaskContext), get_context),
                InjectableParameter(('logger', 'log', 'l'), (Logger,), get_logger),
                InjectableParameter(('subtask_factory', 'task_factory', 'tf'), (OneNoteExportTaskFactory,), lambda: self),
            ),
            should_try_injection=lambda param: param.name != 'prerequisites'
        )

        if spec_is_task_class and 'prerequisites' in inspect.signature(task_spec.__init__).parameters:
            task_ctor_kwargs['prerequisites'] = prerequisites

        partialized = functools.partial(task_spec, *task_ctor_args, **task_ctor_kwargs)

        if spec_is_task_class:
            return partialized()
        if isinstance(task_spec, Callable):
            return OneNoteExportTaskLiteral(partialized, description=task_spec.__name__, prerequisites=prerequisites)
        raise ValueError(f'Unexpected task_spec type: {type(task_spec)}')

