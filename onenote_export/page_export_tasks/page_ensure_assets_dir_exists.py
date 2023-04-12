import os

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


def page_ensure_assets_dir_exists(context: OneNotePageExportTaskContext):
    assets_dir = context.output_dir / context.assets_dir
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.
