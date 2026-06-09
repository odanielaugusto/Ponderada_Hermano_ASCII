from ascii_art.cli import main


def test_cli_prints_direct_text(capsys) -> None:
    exit_code = main(["--text", "ok", "--no-animate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "#" in captured.out


def test_cli_asks_for_input(monkeypatch, capsys) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "ci")

    exit_code = main(["--no-animate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "#" in captured.out
