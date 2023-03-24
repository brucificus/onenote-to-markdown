from logging import info as log
from typing import Callable
import pathlib

from onenote import \
    OneNoteApplication,\
    OneNoteNode,\
    OneNoteUnfiledNotes,\
    OneNoteOpenSections,\
    OneNoteNotebook,\
    OneNotePage,\
    OneNoteSectionGroup,\
    OneNoteSection
from .SimpleOneNoteExportMiddlewareFactory import SimpleOneNoteExportMiddlewareFactory
from .OneNoteExportMiddleware import OneNoteExportMiddleware
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewareContextFactory import OneNoteExportMiddlewareContextFactory
from .OneNoteExportMiddlewareDispatcher import OneNoteExportMiddlewareDispatcher
from .OneNotePageExporter import OneNotePageExporter
from .Pathlike import Pathlike


class OneNoteExporter:
    def __init__(self,
                 root_middleware: OneNoteExportMiddleware[OneNoteApplication, None],
                 create_middleware_context_for_application: Callable[[OneNoteApplication], OneNoteExportMiddlewareContext[OneNoteApplication]]
    ):
        self._root_middleware = root_middleware
        self._create_middleware_context_for_application = create_middleware_context_for_application

    def execute_export(self, application: OneNoteApplication) -> None:
        middleware_context = self._create_middleware_context_for_application(application)
        return self._root_middleware(middleware_context, lambda context: None)


def create_default_onenote_exporter(
    root_output_dir: Pathlike,
    page_relative_assets_dir: Pathlike,
    convert_node_name_to_path_component: Callable[[str], pathlib.Path],
    should_export: Callable[[OneNoteNode], bool] = lambda node: True
) -> 'OneNoteExporter':
    def combine_middleware_returns(a, b):
        if a is not None and b is None:
            return (a,)
        if a is None and b is not None:
            return (b,)
        if a is None and b is None:
            return ()
        if a is tuple and b is tuple:
            return a + b
        if a is tuple:
            return a + (b,)
        if b is tuple:
            return (a,) + b
        return (a, b)

    mf = SimpleOneNoteExportMiddlewareFactory()

    head_middlewares_by_type = {
        OneNoteApplication: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda logger: logger.info('🪟 Found OneNote Application')),
            mf.preempt(lambda logger: logger.info('🚫 Skipping OneNote Application'))
        ),
        OneNoteUnfiledNotes: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda logger: logger.info('📂 Found Unfiled Notes')),
            mf.preempt(lambda logger: logger.info('🚫 Skipping Unfiled Notes'))
        ),
        OneNoteOpenSections: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda context, logger: logger.info(f'📑 Found Open Sections: {context.node.name}')),
            mf.preempt(lambda logger: logger.info(f'🚫 Skipping Open Sections: {context.node.name}'))
        ),
        OneNoteNotebook: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda context, logger: logger.info(f'📒 Found Notebook: {context.node.name}')),
            mf.preempt(lambda context, logger: logger.info(f'🚫 Skipping Notebook: {context.node.name}'))
        ),
        OneNoteSectionGroup: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda context, logger: logger.info(f'📑 Found Section Group: {context.node.name}')),
            mf.preempt(lambda context, logger: logger.info(f'🚫 Skipping Section Group: {context.node.name}'))
        ),
        OneNoteSection: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda context, logger: logger.info(f'📑 Found Section: {context.node.name}')),
            mf.preempt(lambda context, logger: logger.info(f'🚫 Skipping Section: {context.node.name}'))
        ),
        OneNotePage: mf.either_or(
            lambda context: should_export(context.node),
            mf.before(lambda context, logger: logger.info(f'️📃 Found Page: {context.node.name}')),
            mf.preempt(lambda context, logger: logger.info(f'🚫 Skipping Page: {context.node.name}'))
        )
    }

    middleware_context_factory = OneNoteExportMiddlewareContextFactory(
        root_output_dir=root_output_dir,
        page_relative_assets_dir=page_relative_assets_dir,
        convert_node_name_to_path_component=convert_node_name_to_path_component,
    )

    root_middleware = OneNoteExportMiddlewareDispatcher(
        combine_returns=combine_middleware_returns,
        middleware_context_factory=middleware_context_factory,
        middlewares_by_type={
            OneNoteApplication: (head_middlewares_by_type[OneNoteApplication],),
            OneNoteUnfiledNotes: (head_middlewares_by_type[OneNoteUnfiledNotes],),
            OneNoteOpenSections: (head_middlewares_by_type[OneNoteOpenSections],),
            OneNoteNotebook: (head_middlewares_by_type[OneNoteNotebook],),
            OneNoteSectionGroup: (head_middlewares_by_type[OneNoteSectionGroup],),
            OneNoteSection: (head_middlewares_by_type[OneNoteSection],),
            OneNotePage: (
                head_middlewares_by_type[OneNotePage],
                OneNotePageExporter(),
            ),
        },
    )

    return OneNoteExporter(
        root_middleware=root_middleware,
        create_middleware_context_for_application=middleware_context_factory.create_context_for_application
    )
