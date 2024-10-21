# Copyright 2024 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

import click
from graphviz import Digraph


class GraphVisualizer(ABC):
    @abstractmethod
    def node(self, key: str, label: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def edge(self, from_node: str, to_node: str) -> None:
        pass

    @abstractmethod
    def visualize(self) -> None:
        pass


class Mermaid(GraphVisualizer):
    def __init__(self, format: str = "svg", direction: str = "LR") -> None:
        self._diagram = ["flowchart {}".format(direction)]
        self._format = format

    def node(self, key: str, label: Optional[str] = None) -> None:
        if label is None:
            label = key

        self._diagram.append("\t{}[{}]".format(self._mermaid_safe(key), label))

    def edge(self, from_node: str, to_node: str) -> None:
        self._diagram.append(
            "\t{} --> {}".format(
                self._mermaid_safe(from_node),
                self._mermaid_safe(to_node),
            )
        )

    def visualize(self) -> None:
        print("\n".join(self._diagram))
        click.launch(self._mermaid_link())

    def _mermaid_link(self):
        diagram = "\n".join(self._diagram).encode("ascii")
        data = base64.b64encode(diagram).decode("ascii")
        return "https://mermaid.ink/{}/{}".format(self._format, data)

    def _mermaid_safe(self, s: str) -> str:
        return s.replace(" ", "_")


class Graphviz(GraphVisualizer):
    def __init__(
        self,
        name: Optional[str] = None,
        format: str = "svg",
        direction: str = "TB",
        shape: str = "box",
    ) -> None:
        self._graph = Digraph(name=name)
        self._graph.format = format
        self._graph.attr("graph", overlap="False", rankdir=direction)
        self._graph.attr("node", shape=shape)

    def node(self, key: str, label: Optional[str] = None) -> None:
        self._graph.node(self._graphviz_safe(key), label=label)

    def edge(self, from_node: str, to_node: str) -> None:
        self._graph.edge(self._graphviz_safe(from_node), self._graphviz_safe(to_node))

    def visualize(self) -> None:
        tmp_file = tempfile.mktemp(".gv")
        self._graph.render(filename=tmp_file, view=True, cleanup=True)

    def _graphviz_safe(self, s: str) -> str:
        return s.replace(":", "/")
