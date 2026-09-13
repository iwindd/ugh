"""Hermes plugin wiring for ugh-cloud."""

from .command import handle_ugh


def register(ctx):
    ctx.register_command(
        "ugh",
        handler=lambda raw: handle_ugh(raw, ctx=ctx),
        description="Upload profile skills to ugh-cloud GitHub pull requests",
    )
