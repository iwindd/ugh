"""Hermes plugin wiring for ugh."""

from .command import handle_ugh


def register(ctx):
    ctx.register_command(
        "ugh",
        handler=lambda raw: handle_ugh(raw, ctx=ctx),
        description="Upload profile skills to ugh GitHub pull requests",
    )
