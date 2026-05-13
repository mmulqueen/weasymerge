from weasymerge import load_template


def test_renders_basic_template(tmp_path):
    tpl = tmp_path / "hello.html.j2"
    tpl.write_text("Hello {{ row.Name }}")

    template = load_template(str(tpl))
    assert template.render(row={"Name": "Alice"}) == "Hello Alice"


def test_autoescape_is_on(tmp_path):
    tpl = tmp_path / "hello.html.j2"
    tpl.write_text("{{ row.Name }}")

    template = load_template(str(tpl))
    rendered = template.render(row={"Name": "<script>alert(1)</script>"})
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_autoescape_applies_regardless_of_extension(tmp_path):
    # load_template hard-codes autoescape=True, so even a .txt template escapes.
    tpl = tmp_path / "note.txt"
    tpl.write_text("{{ row.Name }}")

    template = load_template(str(tpl))
    assert template.render(row={"Name": "<b>x</b>"}) == "&lt;b&gt;x&lt;/b&gt;"


def test_include_resolves_relative_to_template_dir(tmp_path):
    (tmp_path / "partial.html.j2").write_text("<p>partial: {{ row.Name }}</p>")
    main = tmp_path / "main.html.j2"
    main.write_text('{% include "partial.html.j2" %}')

    template = load_template(str(main))
    assert template.render(row={"Name": "Alice"}) == "<p>partial: Alice</p>"
