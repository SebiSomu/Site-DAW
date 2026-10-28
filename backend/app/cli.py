import click
from flask import Flask, current_app


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    @click.option("--demo", is_flag=True, help="Also create a demo client account with an address.")
    def seed_command(demo: bool) -> None:
        from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD, DatabaseSeeder

        report = DatabaseSeeder().run(include_demo_client=demo)
        click.echo(f"Seed complete: {report.summary()}")
        if not current_app.config["ADMIN_PASSWORD"]:
            click.echo("ADMIN_PASSWORD is not set in .env, so no admin account was created.")
        if demo:
            click.echo(f"Demo client: {DEMO_CLIENT_EMAIL} / {DEMO_CLIENT_PASSWORD}")
