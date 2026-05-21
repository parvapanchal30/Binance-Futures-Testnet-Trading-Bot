import os
from typing import Optional
from dotenv import load_dotenv
import typer
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    ValidationError,
)
from bot.client import BinanceFuturesClient
from bot.orders import place_and_report
from bot.logging_config import setup_logging

app = typer.Typer(add_completion=False)
logger = setup_logging()


def prompt_for_order() -> dict:
    typer.echo("Enter order details:")
    symbol = typer.prompt("Symbol (e.g. BTCUSDT)")
    side = typer.prompt("Side (BUY/SELL)")
    order_type = typer.prompt("Order type (MARKET/LIMIT)")
    quantity = typer.prompt("Quantity")
    price = None
    if order_type.strip().upper() == "LIMIT":
        price = typer.prompt("Price")
    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
    }


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        order(**prompt_for_order())


@app.command()
def order(
    symbol: str = typer.Option(..., help="Trading pair, e.g., BTCUSDT"),
    side: str = typer.Option(..., help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="MARKET or LIMIT"),
    quantity: float = typer.Option(..., help="Order quantity"),
    price: Optional[float] = typer.Option(None, help="Price (required for LIMIT)"),
):
    """Place an order on Binance Futures Testnet (USDT-M)."""
    try:
        s = validate_symbol(symbol)
        sd = validate_side(side)
        ot = validate_order_type(order_type)
        q = validate_quantity(quantity)
        p = validate_price(price, ot)
    except ValidationError as e:
        typer.secho(f"Invalid input: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # Load API keys from env
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    base_url = "https://demo-fapi.binance.com" 

    if not api_key or not api_secret:
        typer.secho("Missing BINANCE_API_KEY and/or BINANCE_API_SECRET in environment.", fg=typer.colors.RED)
        raise typer.Exit(code=3)

    endpoint = base_url
    typer.echo(f"Using Binance Futures endpoint: {endpoint}")
    client = BinanceFuturesClient(api_key, api_secret, base_url=endpoint)

    typer.secho("Order request:", fg=typer.colors.CYAN)
    typer.echo(f"  symbol: {s}")
    typer.echo(f"  side: {sd}")
    typer.echo(f"  type: {ot}")
    typer.echo(f"  quantity: {q}")
    if p is not None:
        typer.echo(f"  price: {p}")

    report = place_and_report(client, s, sd, ot, q, p)

    if not report.get("success"):
        typer.secho("Order failed:", fg=typer.colors.RED)
        typer.echo(f"  error: {report.get('error')}")
        raise typer.Exit(code=4)

    typer.secho("Order placed successfully:", fg=typer.colors.GREEN)
    typer.echo(f"  orderId: {report.get('orderId')}")
    typer.echo(f"  status: {report.get('status')}")
    typer.echo(f"  executedQty: {report.get('executedQty')}")
    typer.echo(f"  avgPrice: {report.get('avgPrice')}")


if __name__ == "__main__":
    app()
