import logging
import os
import random

import hou

from houdini_snippets.files import get_versioned_filepath

logger = logging.getLogger(__name__)


def node_selection() -> tuple[hou.Node] | None:
    return hou.selectedNodes()


def save_selected_nodes(path: str, name: str = "snippet") -> None:
    selected_nodes = node_selection()
    category = selected_nodes[0].type().category().name()

    filepath = get_versioned_filepath(path, name, category)
    save_nodes(selected_nodes, filepath)
    logger.info(f"{name}.hip saved to {filepath}")


def save_nodes(selected_nodes: tuple[hou.OpNode], filepath: str) -> None:
    parents = set(node.parent() for node in selected_nodes)

    if len(parents) > 1:
        logger.debug("More than one node type selected")
        return

    parent = list(parents)[0]

    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    parent.saveItemsToFile(selected_nodes, filepath)


def get_network_pane() -> hou.OpNode | None:
    network_pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

    if network_pane is not None:
        return network_pane.pwd()
    else:
        logger.debug("No network panel found")
        return


def load_nodes_from_file(
        path: str,
        add_network_box: bool = False,
        randomize_network_box_colors: bool = False
) -> None:
    parent = get_network_pane()
    hou.clearAllSelected()

    parent.loadItemsFromFile(path)
    nodes = hou.selectedNodes()

    if add_network_box:
        base = os.path.basename(path)
        network_box_name, ext = os.path.splitext(base)

        network_box = parent.createNetworkBox()
        network_box.setComment(network_box_name)

        for node in nodes:
            network_box.addItem(node)

        network_box.fitAroundContents()

        if randomize_network_box_colors:
            network_box.setColor(
                hou.Color(random.random(), random.random(), random.random())
            )
