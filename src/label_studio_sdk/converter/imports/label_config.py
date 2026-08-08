import re
from xml.sax.saxutils import escape

from label_studio_sdk.converter.imports.colors import COLORS


LABELS = """
  <{# TAG_NAME #} name="{# FROM_NAME #}" toName="image">
{# LABELS #}  </{# TAG_NAME #}>
"""

LABELING_CONFIG = """<View>
  <Image name="{# TO_NAME #}" value="$image"/>
{# BODY #}</View>
"""


def generate_label_config(
    categories, tags, to_name="image", from_name="label", filename=None
):
    def escape_xml_attr(value):
        return escape(str(value), {'"': "&quot;", "'": "&apos;"})

    def sanitize_tag_name(value):
        value = re.sub(r"[^A-Za-z0-9_.:-]", "", str(value))
        if not value:
            return "Labels"
        if not re.match(r"[A-Za-z_]", value[0]):
            value = f"_{value}"
        return value

    escaped_to_name = escape_xml_attr(to_name)

    labels = ""
    for key in sorted(categories.keys()):
        color = COLORS[int(key) % len(COLORS)]
        label = f'    <Label value="{escape_xml_attr(categories[key])}" background="rgba({color[0]}, {color[1]}, {color[2]}, 1)"/>\n'
        labels += label

    body = ""
    for from_name in tags:
        escaped_from_name = escape_xml_attr(from_name)
        escaped_tag_value = escape_xml_attr(tags[from_name])
        sanitized_tag_name = sanitize_tag_name(tags[from_name])
        tag_body = (
            str(LABELS)
            .replace("{# TAG_NAME #}", sanitized_tag_name)
            .replace("{# LABELS #}", labels)
            .replace("{# TO_NAME #}", escaped_to_name)
            .replace("{# FROM_NAME #}", escaped_from_name)
        )
        body += f'\n  <Header value="{escaped_tag_value}"/>' + tag_body

    config = (
        str(LABELING_CONFIG)
        .replace("{# BODY #}", body)
        .replace("{# TO_NAME #}", escaped_to_name)
    )

    if filename:
        with open(filename, "w") as f:
            f.write(config)

    return config
