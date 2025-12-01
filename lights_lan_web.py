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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hue Lights Control</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #4a5568;
            margin-bottom: 40px;
            font-size: 2.5em;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        .item:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .item-info {
            flex-grow: 1;
        }
        .item-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #2d3748;
        }
        .item-state {
            color: #718096;
            margin-top: 5px;
        }
        .controls {
            display: flex;
            gap: 10px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 100px;
        }
        .on {
            background: linear-gradient(45deg, #48bb78, #38a169);
            color: white;
        }
        .on:hover {
            background: linear-gradient(45deg, #38a169, #2f855a);
            transform: scale(1.05);
        }
        .off {
            background: linear-gradient(45deg, #f56565, #e53e3e);
            color: white;
        }
        .off:hover {
            background: linear-gradient(45deg, #e53e3e, #c53030);
            transform: scale(1.05);
        }
        .all-on, .all-off {
            background: linear-gradient(45deg, #ed8936, #dd6b20);
            color: white;
            font-size: 1.1em;
            padding: 15px 30px;
        }
        .all-on {
            background: linear-gradient(45deg, #48bb78, #38a169);
        }
        .all-on:hover {
            background: linear-gradient(45deg, #38a169, #2f855a);
            transform: scale(1.05);
        }
        .all-off:hover {
            background: linear-gradient(45deg, #dd6b20, #c05621);
            transform: scale(1.05);
        }
        .message {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-weight: bold;
        }
        .success {
            background: #c6f6d5;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        .error {
            background: #fed7d7;
            color: #742a2a;
            border: 1px solid #feb2b2;
        }
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            h1 {
                font-size: 2em;
            }
            .item {
                flex-direction: column;
                align-items: stretch;
            }
            .controls {
                justify-content: center;
                margin-top: 15px;
            }
            button {
                flex: 1;
                min-width: 80px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hue Lights Control</h1>
        <div class="section">
            <h2>All Lights</h2>
            <form method="post" style="text-align: center;">
                <button type="submit" name="action" value="all_on" class="all-on">Turn On All Lights</button>
                <button type="submit" name="action" value="all_off" class="all-off">Turn Off All Lights</button>
            </form>
        </div>
        <div class="section">
            <h2>Groups</h2>
            {% for group_id, group in groups.items() %}
            <div class="item">
                <div class="item-info">
                    <div class="item-name">{{ group.name }}</div>
                    <div class="item-state">ID: {{ group_id }} | State: {{ 'On' if group.on else 'Off' }}</div>
                </div>
                <div class="controls">
                    <form method="post" style="display: inline;">
                        <input type="hidden" name="type" value="group">
                        <input type="hidden" name="id" value="{{ group_id }}">
                        <button type="submit" name="action" value="on" class="on">Turn On</button>
                        <button type="submit" name="action" value="off" class="off">Turn Off</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        <div class="section">
            <h2>Zones</h2>
            {% for zone_id, zone in zones.items() %}
            <div class="item">
                <div class="item-info">
                    <div class="item-name">{{ zone.name }}</div>
                    <div class="item-state">ID: {{ zone_id }} | State: {{ 'On' if zone.on else 'Off' }}</div>
                </div>
                <div class="controls">
                    <form method="post" style="display: inline;">
                        <input type="hidden" name="type" value="zone">
                        <input type="hidden" name="id" value="{{ zone_id }}">
                        <button type="submit" name="action" value="on" class="on">Turn On</button>
                        <button type="submit" name="action" value="off" class="off">Turn Off</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        {% if message %}
        <div class="message {{ 'success' if 'successfully' in message or 'turned' in message else 'error' }}">
            {{ message }}
        </div>
        {% endif %}
    </div>
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
            if action == "all_on":
                b.set_group(0, "on", True)
                message = "All lights turned on successfully!"
            elif action == "all_off":
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
