#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["phue", "flask"]
# ///

from flask import Flask, request, render_template_string
from phue import Bridge

app = Flask(__name__)

# Initialize bridge (loads from config if available)
b = Bridge()
b.connect()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hue Lights Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 30px; }
        .item { border: 1px solid #ccc; padding: 10px; margin: 5px 0; }
        button { margin: 5px; }
        .on { background-color: #4CAF50; color: white; }
        .off { background-color: #f44336; color: white; }
    </style>
</head>
<body>
    <h1>Control Hue Lights</h1>
    <div class="section">
        <h2>All Lights</h2>
        <form method="post">
            <button type="submit" name="action" value="all_off">Turn Off All Lights</button>
        </form>
    </div>
    <div class="section">
        <h2>Groups</h2>
        {% for group_id, group in groups.items() %}
        <div class="item">
            <strong>{{ group.name }}</strong> (ID: {{ group_id }}) - State: {{ 'On' if group.on else 'Off' }}
            <form method="post" style="display: inline;">
                <input type="hidden" name="type" value="group">
                <input type="hidden" name="id" value="{{ group_id }}">
                <button type="submit" name="action" value="on" class="on">Turn On</button>
                <button type="submit" name="action" value="off" class="off">Turn Off</button>
            </form>
        </div>
        {% endfor %}
    </div>
    <div class="section">
        <h2>Zones</h2>
        {% for zone_id, zone in zones.items() %}
        <div class="item">
            <strong>{{ zone.name }}</strong> (ID: {{ zone_id }}) - State: {{ 'On' if zone.on else 'Off' }}
            <form method="post" style="display: inline;">
                <input type="hidden" name="type" value="zone">
                <input type="hidden" name="id" value="{{ zone_id }}">
                <button type="submit" name="action" value="on" class="on">Turn On</button>
                <button type="submit" name="action" value="off" class="off">Turn Off</button>
            </form>
        </div>
        {% endfor %}
    </div>
    {% if message %}
    <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        item_type = request.form.get("type")
        item_id = request.form.get("id")
        try:
            if action == "all_off":
                b.set_group(0, "on", False)
                message = "All lights turned off successfully!"
            elif item_type == "group" and item_id:
                if action == "on":
                    b.set_group(int(item_id), "on", True)
                    message = f"Group {item_id} turned on."
                elif action == "off":
                    b.set_group(int(item_id), "on", False)
                    message = f"Group {item_id} turned off."
            elif item_type == "zone" and item_id:
                if action == "on":
                    b.set_group(
                        int(item_id), "on", True
                    )  # Zones are treated as groups in phue
                    message = f"Zone {item_id} turned on."
                elif action == "off":
                    b.set_group(int(item_id), "on", False)
                    message = f"Zone {item_id} turned off."
        except Exception as e:
            message = f"Error: {e}"
    # Separate groups and zones
    try:
        print(f"Debug: b.groups = {b.groups}, type = {type(b.groups)}")
        if hasattr(b, "groups"):
            if isinstance(b.groups, dict):
                groups = {
                    gid: g
                    for gid, g in b.groups.items()
                    if getattr(g, "type", None) != "Zone"
                }
                zones = {
                    gid: g
                    for gid, g in b.groups.items()
                    if getattr(g, "type", None) == "Zone"
                }
            elif isinstance(b.groups, list):

                def get_group_type(g):
                    try:
                        return g.type
                    except:
                        return None

                groups = {
                    g.group_id: g for g in b.groups if get_group_type(g) != "Zone"
                }
                zones = {g.group_id: g for g in b.groups if get_group_type(g) == "Zone"}
            else:
                groups = {}
                zones = {}
        else:
            groups = {}
            zones = {}
    except Exception as e:
        print(f"Debug: Exception in loading groups: {e}")
        groups = {}
        zones = {}
    return render_template_string(
        HTML_TEMPLATE, groups=groups, zones=zones, message=message
    )


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    app.run(host="0.0.0.0", port=port, debug=False)
