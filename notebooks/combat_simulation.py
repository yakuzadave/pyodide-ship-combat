import marimo

__generated_with__ = marimo.__version__
app = marimo.App()
DEFAULT_SEED = 7
DEFAULT_ROUNDS = 3


@app.cell
def __():
    import marimo as mo

    return mo


@app.cell
def __(mo):
    mo.md(
        r"""
        # Fleet combat simulation (marimo)

        This notebook walks through the automated fleet battle simulation that powers the project.
        It runs fully in the browser (Pyodide/JupyterLite) or locally without user input—orders,
        targeting, and hazards are handled by the simulation engine. Use the controls below to tweak
        seeds, rounds, and logging, then explore the transcript, report, and charts.
        """
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Runtime dependencies

        The simulator dynamically installs `py-rolldice` when running under Pyodide. In a browser
        context include:

        ```python
        import micropip
        await micropip.install("py-rolldice")
        await micropip.install("plotly")
        ```

        Local runs only need the dependencies from `requirements.txt` (including `marimo` and
        `plotly` for this notebook).
        """
    )


@app.cell
def __():
    import contextlib
    import io
    import logging
    import random

    import plotly.graph_objects as go

    from ship_combat.battle_sim import battle
    from ship_combat.fleet_setup import demo_fleets

    return battle, contextlib, demo_fleets, go, io, logging, random


@app.cell
def __(mo):
    rounds = mo.ui.slider(
        start=1,
        stop=6,
        value=DEFAULT_ROUNDS,
        step=1,
        label="Rounds to simulate",
    )
    seed = mo.ui.number(value=DEFAULT_SEED, step=1, label="Random seed")
    log_level = mo.ui.select(
        options={
            "INFO": "Info (balanced)",
            "DEBUG": "Debug (verbose)",
            "WARNING": "Warnings only",
        },
        value="INFO",
        label="Log level",
    )
    show_map = mo.ui.switch(value=False, label="Show ASCII map each round")
    show_stats = mo.ui.switch(value=True, label="Print textual stats to transcript")

    mo.vstack(
        [
            mo.md("### Controls"),
            mo.md("Tweak these knobs, then run the battle cell below."),
            mo.hstack([rounds, seed, log_level], gap="1rem", wrap=True),
            mo.hstack([show_map, show_stats], gap="1rem", wrap=True),
        ],
        gap="0.5rem",
    )

    return log_level, rounds, seed, show_map, show_stats


@app.cell
def __(demo_fleets, mo):
    def fleet_rows(fleet):
        return [
            {
                "Ship": ship.name,
                "Class": ship.class_name,
                "Hull": ship.hull,
                "Shield": ship.shield,
                "AI": ship.ai,
                "Missiles": ship.weapons.missiles,
            }
            for ship in fleet
        ]

    fleet_a_preview, fleet_b_preview = demo_fleets()
    fleet_tabs = mo.ui.tabs(
        {
            "Fleet A": mo.ui.table(fleet_rows(fleet_a_preview), page_size=6),
            "Fleet B": mo.ui.table(fleet_rows(fleet_b_preview), page_size=6),
        }
    )

    mo.vstack(
        [
            mo.md(
                r"""
                ### Demo fleets

                Expand the tabs for a quick roster preview before launching the simulation.
                """
            ),
            fleet_tabs,
        ],
        gap="0.75rem",
    )


@app.cell
def __(battle, contextlib, demo_fleets, io, log_level, logging, mo, random, rounds, seed, show_map, show_stats):
    def safe_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    seed_value = safe_int(seed.value, DEFAULT_SEED)
    rounds_value = safe_int(rounds.value, DEFAULT_ROUNDS)
    log_level_value = str(log_level.value or "INFO")

    random.seed(seed_value)
    fleet_a, fleet_b = demo_fleets()

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        logger = battle(
            fleet_a,
            fleet_b,
            rounds=rounds_value,
            log_level=getattr(logging, log_level_value),
            show_map=bool(show_map.value),
            show_stats=bool(show_stats.value),
        )

    transcript = buffer.getvalue()
    report = logger.generate_report()

    mo.vstack(
        [
            mo.md(
                f"""
                ### Battle run
                * Rounds: **{rounds_value}**
                * Seed: **{seed_value}**
                * Log level: **{log_level_value}**
                * ASCII map: **{show_map.value}**
                """
            ),
            mo.ui.tabs(
                {
                    "Transcript": mo.md(f"```\n{transcript}\n```"),
                    "Post-battle report": mo.md(f"```\n{report}\n```"),
                }
            ),
        ],
        gap="0.75rem",
    )

    return logger, transcript


@app.cell
def __(go, mo, logger=None):
    logger = logger or globals().get("logger")
    content = mo.md("Run the simulation above to populate visuals.")
    if logger:
        stats = logger.stats
        ship_names = list(stats.ship_damage_dealt.keys())
        if not ship_names:
            content = mo.md("No weapon fire occurred; rerun with more rounds for visuals.")
        else:
            damage_dealt = [stats.ship_damage_dealt.get(name, 0) for name in ship_names]
            damage_taken = [stats.ship_damage_taken.get(name, 0) for name in ship_names]
            damage_fig = go.Figure()
            damage_fig.add_trace(go.Bar(x=ship_names, y=damage_dealt, name="Damage dealt"))
            damage_fig.add_trace(go.Bar(x=ship_names, y=damage_taken, name="Damage taken"))
            damage_fig.update_layout(
                barmode="group",
                title="Per-ship damage",
                template="plotly_dark",
                xaxis_title="Ship",
                yaxis_title="HP",
            )

            fleet_labels = ["Fleet A", "Fleet B"]
            accuracy_fig = go.Figure()
            accuracy_fig.add_trace(
                go.Bar(
                    x=fleet_labels,
                    y=[stats.get_accuracy("a"), stats.get_accuracy("b")],
                    name="Accuracy (%)",
                )
            )
            accuracy_fig.add_trace(
                go.Bar(
                    x=fleet_labels,
                    y=[stats.get_critical_rate("a"), stats.get_critical_rate("b")],
                    name="Critical hit rate (%)",
                )
            )
            accuracy_fig.update_layout(
                barmode="group",
                title="Shot quality",
                template="plotly_dark",
                yaxis_title="Percent",
                yaxis_range=[0, 100],
            )

            content = mo.vstack(
                [
                    mo.md("### Visual summaries"),
                    mo.ui.tabs(
                        {
                            "Damage by ship": damage_fig,
                            "Accuracy vs crits": accuracy_fig,
                        }
                    ),
                ],
                gap="0.75rem",
            )

    content


@app.cell
def __(mo, logger=None):
    logger = logger or globals().get("logger")
    content = mo.md("Run the simulation to view the last 25 combat events.")
    if logger and logger.events:
        rows = [
            {
                "Round": event.round_num,
                "Phase": event.phase,
                "Ship": event.ship or "",
                "Target": event.target or "",
                "Event": event.event_type,
                "Damage": event.damage,
            }
            for event in logger.events[-25:]
        ]

        content = mo.vstack(
            [
                mo.md("### Recent combat events"),
                mo.ui.table(rows, page_size=10),
            ],
            gap="0.75rem",
        )

    content


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Next steps

        * Adjust the random seed or number of rounds and re-run the battle cell to explore different
          outcomes.
        * Swap in custom fleets by editing `ship_combat.fleet_setup.demo_fleets`.
        * Enable `show_map=True` to render ASCII battle maps directly in the notebook output.
        * Extend the visuals by adding more tabs—for example, per-phase heat maps or missile tallies.
        """
    )


if __name__ == "__main__":
    app.run()
