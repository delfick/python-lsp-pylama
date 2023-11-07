"""
Heavily based on https://github.com/python-lsp/python-lsp-server/blob/d47dc3c1fd1f2bafcc079006c3283e465b372f75/pylsp/plugins/pylint_lint.py
"""

import logging
import pathlib

from pylama import config as pylama_config
from pylama import main as pylama
from pylsp import hookimpl, lsp

try:
    from noseOfYeti import tokeniser
except ImportError:
    tokeniser = None


log = logging.getLogger(__name__)

DEPRECATION_CODES = {
    "W0402",  # Uses of a deprecated module %r
    "W1505",  # Using deprecated method %s()
    "W1511",  # Using deprecated argument %s of method %s()
    "W1512",  # Using deprecated class %s of module %s
    "W1513",  # Using deprecated decorator %s()
}
UNNECESSITY_CODES = {
    "W0611",  # Unused import %s
    "W0612",  # Unused variable %r
    "W0613",  # Unused argument %r
    "W0614",  # Unused import %s from wildcard import
    "W1304",  # Unused-format-string-argument
}


class PylamaLinter:
    def lint(self, document, settings):
        location = pathlib.Path.cwd() / document.path
        rootdir = pathlib.Path(document._workspace.root_path)

        args = list(settings.get("args") or [])
        if "--from-stdin" not in args:
            args.append("--from-stdin")

        if "--options" not in args and "-o" not in args:
            args.extend(["--options", pylama_config.get_default_config_file(rootdir)])

        options = pylama.parse_options([*args, str(location)], rootdir=rootdir)

        diagnostics = []
        for error in pylama.check_paths(
            options.paths,
            code=self._maybe_transform(document.source),
            options=options,
            rootdir=rootdir,
        ):
            # pylama lines index from 1, pylsp lines index from 0
            line = error.lnum - 1

            err_range = {
                "start": {
                    "line": line,
                    # Index columns start from 0
                    "character": error.col,
                },
                "end": {
                    "line": line,
                    # It's possible that we're linting an empty file. Even an empty
                    # file might fail linting if it isn't named properly.
                    "character": len(document.lines[line]) if document.lines else 0,
                },
            }

            if error.etype == "C":
                severity = lsp.DiagnosticSeverity.Information
            elif error.etype == "I":
                severity = lsp.DiagnosticSeverity.Information
            elif error.etype == "E":
                severity = lsp.DiagnosticSeverity.Error
            elif error.etype == "F":
                severity = lsp.DiagnosticSeverity.Error
            elif error.etype == "R":
                severity = lsp.DiagnosticSeverity.Hint
            elif error.etype == "W":
                severity = lsp.DiagnosticSeverity.Warning

            code = error.number

            diagnostic = {
                "source": "pylama",
                "range": err_range,
                "message": "[{}] {}".format(error.number, error.message),
                "severity": severity,
                "code": code,
            }

            if code in UNNECESSITY_CODES:
                diagnostic["tags"] = [lsp.DiagnosticTag.Unnecessary]
            if code in DEPRECATION_CODES:
                diagnostic["tags"] = [lsp.DiagnosticTag.Deprecated]

            diagnostics.append(diagnostic)
        return diagnostics

    def _maybe_transform(self, source):
        if tokeniser is None or not source:
            return source

        from noseOfYeti.tokeniser.spec_codec import regexes

        if not regexes["encoding_matcher"].search(source.split("\n", 1)[0]):
            return source

        return tokeniser.spec_codec.codec().translate(source)


linter = PylamaLinter()


@hookimpl
def pylsp_settings():
    return {
        "plugins": {
            "pylama": {
                "enabled": False,
                "args": [],
            }
        }
    }


@hookimpl
def pylsp_lint(config, workspace, document):
    with workspace.report_progress("lint: pylama"):
        settings = config.plugin_settings("pylama")
        log.debug("Got pylama settings: %s", settings)
        return linter.lint(document, settings=settings)
