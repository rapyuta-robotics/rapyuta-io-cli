from click_help_colors import HelpColorsGroup


class AliasedGroup(HelpColorsGroup):
    """A Click Group that supports command aliases and abbreviations."""

    def __init__(self, *args, **kwargs):
        # You can define aliases at the class level or pass them in
        self.aliases = kwargs.pop("aliases", {})
        super().__init__(*args, **kwargs)

    def get_command(self, ctx, cmd_name):
        # Step 1: Try to get the command normally (exact match)
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        # Step 2: Check if it's an explicit alias
        if cmd_name in self.aliases:
            return super().get_command(ctx, self.aliases[cmd_name])

        # Step 3: Check for abbreviations (startswith)
        matches = [
            x for x in self.list_commands(ctx) if x.lower().startswith(cmd_name.lower())
        ]
        if not matches:
            return None
        elif len(matches) == 1:
            return super().get_command(ctx, matches[0])

        # Multiple matches - fail with helpful message
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # Always return the command's name, not the alias
        cmd_name, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args
