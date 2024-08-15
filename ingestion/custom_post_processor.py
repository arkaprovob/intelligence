from typing import List, Optional

from llama_index.core import QueryBundle
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore


class LowercaseNodePostprocessor(BaseNodePostprocessor):

    def _postprocess_nodes(
            self,
            nodes: List[NodeWithScore],
            query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        # convert all text to lowercase
        print("in LowercaseNodePostprocessor ˆ_ˆ")
        for n in nodes:
            n.node.set_content(n.node.get_content().lower())

        return nodes