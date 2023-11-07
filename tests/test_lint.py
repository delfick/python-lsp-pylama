# coding: spec

import pathlib
import shutil
import tempfile
from textwrap import dedent
from unittest import mock

import pytest
from pylsp import lsp, uris
from pylsp.config.config import Config
from pylsp.workspace import Document, Workspace

from pylsp_pylama import plugin

rootdir = pathlib.Path(__file__).parent / ".."


@pytest.fixture()
def workspace(tmp_path):
    """Return a workspace."""
    workspace_root = tmp_path.resolve()
    shutil.copy(rootdir / "pylama.ini", workspace_root)
    ws = Workspace(workspace_root.as_uri(), mock.Mock())
    ws._config = Config(ws.root_uri, {}, 0, {})
    return ws


describe "Linting":

    class PerTest:
        def __init__(self, workspace):
            self.workspace = workspace

        def make_unsaved_document(self, doc_text):
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.workspace.root_path, suffix=".py", delete=False
            ) as temp_file:
                name = temp_file.name
            return Document(uris.from_fs_path(name), self.workspace, dedent(doc_text).strip())

        def make_saved_document(self, doc_text):
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.workspace.root_path, suffix=".py", delete=False
            ) as temp_file:
                name = temp_file.name
                temp_file.write(dedent(doc_text).strip())
            doc = Document(uris.from_fs_path(name), self.workspace)
            return doc

        def lint(self, doc):
            return plugin.pylsp_lint(self.workspace._config, self.workspace, doc)

    it "works on unsaved document with error", workspace:
        test_logic = self.PerTest(workspace)
        doc = test_logic.make_unsaved_document(
            """
            import pylsp

            t = "TEST"

            def using_const():
                a = 8 + 9
                return t
            """
        )
        diags = test_logic.lint(doc)
        assert diags == [
            {
                "source": "pylama",
                "range": {
                    "start": {"line": 0, "character": 1},
                    "end": {"line": 0, "character": 13},
                },
                "message": "[W0611] 'pylsp' imported but unused",
                "severity": 2,
                "code": "W0611",
                "tags": [lsp.DiagnosticTag.Unnecessary],
            },
            {
                "source": "pylama",
                "range": {
                    "start": {"line": 5, "character": 5},
                    "end": {"line": 5, "character": 14},
                },
                "message": "[W0612] local variable 'a' is assigned to but never used",
                "severity": 2,
                "code": "W0612",
                "tags": [lsp.DiagnosticTag.Unnecessary],
            },
        ]

    it "works on saved document with error", workspace:
        test_logic = self.PerTest(workspace)
        doc = test_logic.make_saved_document(
            """
            import pylsp

            t = "TEST"

            def using_const():
                a = 8 + 9
                return t
            """
        )
        diags = test_logic.lint(doc)
        assert diags == [
            {
                "source": "pylama",
                "range": {
                    "start": {"line": 0, "character": 1},
                    "end": {"line": 0, "character": 13},
                },
                "message": "[W0611] 'pylsp' imported but unused",
                "severity": 2,
                "code": "W0611",
                "tags": [lsp.DiagnosticTag.Unnecessary],
            },
            {
                "source": "pylama",
                "range": {
                    "start": {"line": 5, "character": 5},
                    "end": {"line": 5, "character": 14},
                },
                "message": "[W0612] local variable 'a' is assigned to but never used",
                "severity": 2,
                "code": "W0612",
                "tags": [lsp.DiagnosticTag.Unnecessary],
            },
        ]

    it "works on unsaved empty documents", workspace:
        test_logic = self.PerTest(workspace)
        diags = test_logic.lint(test_logic.make_unsaved_document(""))
        assert diags == []

    it "works on saved empty documents", workspace:
        test_logic = self.PerTest(workspace)
        diags = test_logic.lint(test_logic.make_saved_document(""))
        assert diags == []

    it "works on unsaved document without error", workspace:
        test_logic = self.PerTest(workspace)
        doc = test_logic.make_unsaved_document(
            """
            import os
            os.exit(1)
            """
        )

        diags = test_logic.lint(doc)
        assert diags == []

    it "works on saved document without error", workspace:
        test_logic = self.PerTest(workspace)
        doc = test_logic.make_saved_document(
            """
            import os
            os.exit(1)
            """
        )

        diags = test_logic.lint(doc)
        assert diags == []
