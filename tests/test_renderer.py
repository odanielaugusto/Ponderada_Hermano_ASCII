import pytest

from ascii_art import render_text


def test_render_text_uses_five_rows() -> None:
    art = render_text("CI")

    assert len(art.splitlines()) == 5


def test_render_text_accepts_custom_fill() -> None:
    art = render_text("A", fill="*")

    assert "*" in art
    assert "#" not in art


def test_render_text_keeps_words_separated() -> None:
    art = render_text("A B")

    assert len(art.splitlines()[0]) > len(render_text("AB").splitlines()[0])


def test_render_text_rejects_multi_character_fill() -> None:
    with pytest.raises(ValueError, match="fill"):
        render_text("A", fill="[]")


def test_render_text_rejects_negative_gap() -> None:
    with pytest.raises(ValueError, match="gap"):
        render_text("A", gap=-1)


def test_render_text_supports_multiple_lines() -> None:
    art = render_text("A\nB")

    assert "\n\n" in art
    assert len(art.split("\n\n")) == 2
