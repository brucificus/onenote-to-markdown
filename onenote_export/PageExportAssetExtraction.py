import abc
import pathlib

from typing import Optional, Callable, Sequence

from onenote_export.Pathlike import Pathlike


class PageExportAssetExtraction(abc.ABC):
    @abc.abstractmethod
    def extract_assets_to(self,
                          target_dir: Pathlike,
                          map_extraction_path: Optional[Callable[[pathlib.Path], Optional[pathlib.Path]]] = None,
                          ) -> Sequence[pathlib.Path]:
        """
        Extracts assets from the page export to the target directory.
        :param target_dir: The directory to extract assets to.
        :param map_extraction_path: A function that takes a path to an asset and returns the path to which the asset should be extracted. If None, the asset will not be extracted.
        :return: The paths to the extracted assets.
        """
        pass
