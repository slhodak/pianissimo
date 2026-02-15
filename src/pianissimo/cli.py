import json
import os
from datetime import date

import click
from dotenv import load_dotenv

load_dotenv()

from pianissimo.conversation import run_conversation
from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill
from pianissimo.renderer import render_to_pdf, check_lilypond


@click.command()
@click.option("--output-dir", default="drills", help="Directory to save generated drills")
def main(output_dir: str):
    """Pianissimo — a sight-reading drill generator."""
    try:
        check_lilypond()
    except RuntimeError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    click.echo("Welcome to Pianissimo! How can I help you practice sight-reading today?")
    description = click.prompt(">")
    if not description:
        description = click.prompt(">")

    click.echo(f"Let me think about that...")
    spec = run_conversation(description)

    click.echo(f"\nGenerating drill...")
    score = generate_drill(spec)

    today = date.today().isoformat()
    slug = "".join(c if c.isalnum() or c == "-" else "-" for c in description[:30].lower()).strip("-")
    base_name = f"{today}-{slug}"
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    pdf_path = render_to_pdf(score, pdf_path)
    click.echo(f"[PDF saved to {pdf_path}]")

    spec_path = os.path.join(output_dir, f"{base_name}.json")
    with open(spec_path, "w") as f:
        json.dump(spec.to_dict(), f, indent=2)
    click.echo(f"[Spec saved to {spec_path}]")


if __name__ == "__main__":
    main()
