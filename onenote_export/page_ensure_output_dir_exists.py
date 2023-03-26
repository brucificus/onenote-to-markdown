import os

from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


def page_ensure_output_dir_exists(context: OneNotePageExportTaskContext):
    if not os.path.exists(context.output_dir):
        os.makedirs(context.output_dir, exist_ok=True)  # 'exist_ok' is needed for parallel execution.
