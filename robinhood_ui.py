import click
import json
import robin_stocks as rh
import robinhood_ui as ui


@click.group()
def main():
    content = open('robinhood_login.json').read()
    config = json.loads(content)
    rh.login(config['username'], config['password'])
    print("hello from main")


@main.command(help='Gets a stock quote for one or more symbols')
@click.argument('symbols', nargs=-1)
def quote(symbols):
    quotes = rh.get_quotes(symbols)
    for quote in quotes:
        ui.success("{} | {}".format(quote['symbol'], quote['ask_price']))


@main.command(help='Gets quotes for all stocks in your watchlist')
def watchlist():
    with open('watchlist') as f:
        symbols = f.read().splitlines()

    quotes = rh.get_quotes(symbols)
    print(quotes)


@main.command(help='Buy quantity of stocks')
@click.argument('quantity', type=click.INT)
@click.argument('symbol', type=click.STRING)
@click.option('--limit', type=click.FLOAT)
def buy(quantity, symbol, limit):
    if limit is not None:
        ui.success("buying {} of {} at {}".format(quantity, symbol, limit))
        result = rh.order_buy_limit(symbol, quantity, limit)
    else:
        ui.success("buying {} of {} at market price".format(quantity, symbol))
        result = rh.order_buy_market(symbol, quantity)
    if 'ref_id' in result:
        ui.success(result)
    else:
        ui.error(result)



@main.command(help='Sell quantity of stocks')
@click.argument('quantity', type=click.INT)
@click.argument('symbol', type=click.STRING)
@click.option('--limit', type=click.FLOAT)
def sell(quantity, symbol, limit):
    if limit is not None:
        ui.success("buying {} of {} at {}".format(quantity, symbol, limit))
        result = rh.order_sell_limit(symbol, quantity, limit)
    else:
        ui.success("buying {} of {} at market price".format(quantity, symbol))
        result = rh.order_sell_market(symbol, quantity)
    if 'ref_id' in result:
        ui.success(result)
    else:
        ui.error(result)

    pass


if __name__ == '__main__':
    main()
