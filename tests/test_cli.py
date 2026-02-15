from click.testing import CliRunner
from pianissimo.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "pianissimo" in result.output.lower() or "sight-reading" in result.output.lower()
