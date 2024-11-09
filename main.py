import asyncio
import sys
from typing import Any

from rich.panel import Panel

from code_review.v0_original import run as run_v0
from code_review.v1_dropin_replacement import run as run_v1
from code_review.v2_extract_types import run as run_v2
from code_review.v3_use_examples import run as run_v3
from code_review.v4_extract_guidelines import run as run_v4
from outropy.client.api import OutropyApi
from util import outropy_api_key, console, outropy_api_host

examples: dict[str, Any] = {
    'v0': run_v0,
    'v1': run_v1,
    'v2': run_v2,
    'v3': run_v3,
    'v4': run_v4,
}


async def main(o: OutropyApi, example: str) -> None:
    if example == 'all':
        console.log(f"Running [b]all[/b] examples: [b]{[k for k in examples.keys()]}[/b]")
        for example_to_run in examples:
            await run_example(example_to_run, o)
        return
    else:
        await run_example(example, o)


async def run_example(example: str, o: OutropyApi) -> None:
    try:
        header = Panel.fit(f"Running example [b]{example}[/b]", style="bold white on purple", border_style="black")

        console.print(header)
        if example not in examples:
            console.log(f"Example [b]{example}[/b] not found, available examples are [b]all[/]b or: [b]{examples.keys()}[/]")
        else:
            await examples[example](o)
    except Exception as e:
        console.print(f"[red]Error running example [b]{example}[/b]: {e}[/red]")
        return
    console.print(f"[green]Example [b]{example}[/b] completed")


if __name__ == '__main__':
    # Convenience main function to run the script in isolation
    api_key = outropy_api_key()
    api_host = outropy_api_host()
    console.log(f"Using Outropy API key [b]{api_key}[/b] and host [b]{api_host}[/b]")
    outropy = OutropyApi(api_key, api_host)
    to_run = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in examples else 'all'
    asyncio.run(main(outropy, to_run))
