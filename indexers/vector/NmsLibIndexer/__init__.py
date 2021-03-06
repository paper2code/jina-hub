__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Tuple

import numpy as np
from jina.executors.indexers.vector import BaseNumpyIndexer
from jina.executors.decorators import batching

class NmsLibIndexer(BaseNumpyIndexer):
    """nmslib powered vector indexer

    For documentation and explanation of each parameter, please refer to

        - https://nmslib.github.io/nmslib/quickstart.html
        - https://github.com/nmslib/nmslib/blob/master/manual/methods.md

    .. note::
        Nmslib package dependency is only required at the query time.
    """

    def __init__(self, space: str = 'cosinesimil', method: str = 'hnsw', print_progress: bool = False,
                 num_threads: int = 1,
                 *args, **kwargs):
        """
        Initialize an NmslibIndexer

        :param space: The metric space to create for this index
        :param method: The index method to use
        :param num_threads: The number of threads to use
        :param print_progress: Whether or not to display progress bar when creating index
        :param args:
        :param kwargs:
        """
        super().__init__(*args, compress_level=0, **kwargs)
        self.method = method
        self.space = space
        self.print_progress = print_progress
        self.num_threads = num_threads

    def build_advanced_index(self, vecs: 'np.ndarray'):
        import nmslib
        _index = nmslib.init(method=self.method, space=self.space)
        self.build_partial_index(vecs, _index)
        _index.createIndex({'post': 2}, print_progress=self.print_progress)
        return _index

    @batching(batch_size=512)
    def build_partial_index(self, vecs: 'np.ndarray', _index):
        _index.addDataPointBatch(vecs.astype(np.float32))

    def query(self, keys: 'np.ndarray', top_k: int, *args, **kwargs) -> Tuple['np.ndarray', 'np.ndarray']:
        # if keys.dtype != np.float32:
        #     raise ValueError('vectors should be ndarray of float32')
        ret = self.query_handler.knnQueryBatch(keys, k=top_k, num_threads=self.num_threads)
        idx, dist = zip(*ret)
        return self.int2ext_id[np.array(idx)], np.array(dist)
