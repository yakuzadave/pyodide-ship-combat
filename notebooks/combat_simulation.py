import marimo

__generated_with__ = marimo.__version__
app = marimo.App()


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
        It is designed to run in the browser (Pyodide/JupyterLite) or locally and does not require
        user input—orders, targeting, and hazards are all handled by the simulation engine.
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
        ```

        Local runs only need the dependencies from `requirements.txt` (including `marimo` for this
        notebook).
        """
    )


@app.cell
def __():
    import contextlib
    import io
    import logging
    import random

    from ship_combat.battle_sim import battle
    from ship_combat.fleet_setup import demo_fleets

    return battle, contextlib, demo_fleets, io, logging, random


@app.cell
def __(mo, demo_fleets):
    def describe_fleet(fleet):
        lines = []
        for ship in fleet:
            batteries = ", ".join(b.name for b in ship.weapons.batteries)
            lines.append(
                f"- **{ship.name}** ({ship.class_name}): hull {ship.hull}, "
                f"shield {ship.shield}, missiles {ship.weapons.missiles}, "
                f"AI: {ship.ai}. Weapons: {batteries}"
            )
        return "\n".join(lines)

    fleet_a_preview, fleet_b_preview = demo_fleets()

    mo.md(
        f"""
        ### Demo fleets

        **Fleet A**
        {describe_fleet(fleet_a_preview)}

        **Fleet B**
        {describe_fleet(fleet_b_preview)}
        """
    )


@app.cell
def __(mo):
    RANDOM_SEED = 7

    mo.md(f"Using deterministic random seed: **{RANDOM_SEED}**")
    return RANDOM_SEED


@app.cell
def __(mo, RANDOM_SEED, battle, contextlib, demo_fleets, io, logging, random):
    """Run a short battle and show the quick status plus statistics."""
    random.seed(RANDOM_SEED)
    fleet_a, fleet_b = demo_fleets()

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        logger = battle(
            fleet_a,
            fleet_b,
            rounds=2,
            log_level=logging.INFO,
            show_map=False,
            show_stats=False,
        )

    transcript = buffer.getvalue()
    report = logger.generate_report()

    mo.md(
        f"""
        ### Battle run (2 rounds)

        ```
        {transcript}
        ```

        ### Post-battle statistics

        ```
        {report}
        ```
        """
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ### Next steps

        * Adjust the random seed or number of rounds and re-run the final cell to explore different
          outcomes.
        * Swap in custom fleets by editing `ship_combat.fleet_setup.demo_fleets`.
        * Enable `show_map=True` in the simulation cell to render ASCII battle maps directly in the
          notebook output.
        """
    )


if __name__ == "__main__":
    app.run()
