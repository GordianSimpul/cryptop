import curses
import os
import sys
import re
import shutil
import configparser
import json
import pkg_resources
import locale
from time import sleep
import requests
import requests_cache
from curses import KEY_F5
import argparse
import time
from sys import stdout
from apt_pkg import TIME

# GLOBALS!
BASEDIR = os.path.join(os.path.expanduser('~'), '.cryptop')
COINLIST = os.path.join(BASEDIR, 'coinlist.json')
STARTFILE = os.path.join(BASEDIR, 'startvalue.json')
DATAFILE = os.path.join(BASEDIR, 'wallet.json')
PORTFILE = os.path.join(BASEDIR, 'wallet_delta.json')
CONFFILE = os.path.join(BASEDIR, 'config.ini')
CONFIG = configparser.ConfigParser()
COIN_FORMAT = re.compile('[A-Z]{2,7},\d{0,}\.?\d{0,}')
CRYPTOP_VERSION = 'cryptop v1.0.0'
CCOMPARE_API_KEY = ''
CMC_API_KEY = ''
CMCQuote="https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=%s" 
CMCPriceChange="https://pro-api.coinmarketcap.com/v1/cryptocurrency/price-performance-stats/latest?symbole=%s&CMC_PRO_API_KEY=%s"
cmcqJSON = {} #CMC Quote, keep global so less requests to servers 
SORT_FNS = { 'coin' : lambda item: item[0],
             'price': lambda item: float(item[1][0]),
             'held' : lambda item: float(item[2]),
             'val'  : lambda item: float(item[1][0]) * float(item[2]) }
SORTS = list(SORT_FNS.keys())
COLUMN = SORTS.index('val')
ORDER = True

NEGRO = curses.COLOR_BLACK

COLORS = [curses.COLOR_BLUE, curses.COLOR_CYAN, curses.COLOR_GREEN,
          curses.COLOR_MAGENTA, curses.COLOR_RED, curses.COLOR_WHITE,curses.COLOR_YELLOW]

KEY_ESCAPE = 27
KEY_ZERO = 48
KEY_A = 65
KEY_Q = 81
KEY_R = 82
KEY_S = 83
KEY_C = 67
KEY_a = 97
KEY_q = 113
KEY_r = 114
KEY_s = 115
KEY_c = 99
KEY_PLUS = 43
KEY_MINUS = 45
KEY_plus = 107
KEY_minus = 109

def read_configuration(confpath):
    """Read the configuration file at given path."""
    # copy our default config file
    if not os.path.isfile(confpath):
        defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
        shutil.copyfile(defaultconf, CONFFILE)

    CONFIG.read(confpath)
    return CONFIG


def get_coin_list():
    global CMC_API_KEY
    cmc_coin_list_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY=%s" % CMC_API_KEY
    
    def inner():
        coinJSON = requests.get(cmc_coin_list_url)
        data = coinJSON.content
        with open(COINLIST, 'wb') as f:
            f.write(data)
    
    if os.path.exists(COINLIST):
        days = 10
        file_time = os.path.getmtime(COINLIST)
        if ((time.time() - file_time) / 3600 > 24*days):
            inner()
    else:
        inner()
    
    return
        
    

def if_coin(coin, url='https://www.cryptocompare.com/api/data/coinlist/'):
    
    '''Check if coin exists'''
    get_coin_list()
    
    with open(COINLIST, 'rb') as f:
        data = f.read()
    
    coin_list = json.loads(data) 
    
    for c in coin_list['data']:
        if coin in c['symbol']:
            return coin
    return 

def get_price(coin, curr=None):
    '''Get the data on coins'''
    global CCOMPARE_API_KEY
    global CMC_API_KEY
    
    headers_dict = {'X-CMC_PRO_API_KEY' : "%s" % CMC_API_KEY}
    curr = curr or CONFIG['api'].get('currency', 'USD')
    cc_price_list = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}&api_key=%s' % CCOMPARE_API_KEY
    price_matrix = []
    try:
        r = requests.get(cc_price_list.format(coin, curr))
        cmcq_r = requests.get(CMCQuote % coin, headers=headers_dict)
        
    except requests.exceptions.RequestException:
        return price_matrix
    
    try:
        data_raw = r.json()['RAW']
        global cmcqJSON
        cmcqJSON = cmcq_r.json()
        
        for c in coin.split(','):
            if c in data_raw.keys():
                price_matrix.append((float(data_raw[c][curr]['PRICE']),
                 float(data_raw[c][curr]['HIGH24HOUR']),
                 float(data_raw[c][curr]['LOW24HOUR'])))
            else:
                price_matrix.append((float(cmcqJSON['data'][c.upper()]['quote'][curr]['price']),
                                     float(0.0), float(0.0)))
        return price_matrix
    except Exception as e:
        sys.exit('Could not parse data: %s' % str(e))
    
def get_change(coin, curr="USD"):
    
    global cmcqJSON
    global CCOMPARE_API_KEY
    global CMC_API_KEY
    coin_change_amt = {}
    cc_change_url = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=%s&tsyms=%s&api_key=%s' 
    curr = curr or CONFIG['api'].get('currency', 'USD')
    curr = curr.upper()
    try:
        req = requests.get(cc_change_url % (coin, curr,CCOMPARE_API_KEY))
        hdata = req.json()
    except requests.exceptions.RequestException:
        for c in coin.split(','):
            coin_change_amt[c] = 0.0
        return coin_change_amt
    
    for c in coin.split(','):
        if c in hdata['RAW'].keys():
            coin_change_amt[c] = round(float(hdata['RAW'][c][curr]["CHANGEPCT24HOUR"]),2)
        else: 
            coin_change_amt[c] = round(float(cmcqJSON['data'][c]['quote'][curr]["percent_change_24h"]),2)
        if coin_change_amt[c] > 0: 
            coin_change_amt[c] = '+' + str(coin_change_amt[c]) + "%"
        else:
            coin_change_amt[c] = str(coin_change_amt[c]) + "%"
    return coin_change_amt
    
def get_theme_colors():
    ''' Returns curses colors according to the config'''
    def get_curses_color(name_or_value):
        try:
            return getattr(curses, 'COLOR_' + name_or_value.upper())
        except AttributeError:
            return int(name_or_value)

    theme_config = CONFIG['theme']
    return (get_curses_color(theme_config.get('text', 'yellow')),
        get_curses_color(theme_config.get('banner', 'yellow')),
        get_curses_color(theme_config.get('banner_text', 'black')),
        get_curses_color(theme_config.get('background', -1)))


def conf_scr():
    '''Configure the screen and colors/etc'''
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    text, banner, banner_text, background = get_theme_colors()
    curses.init_pair(2, text, background)
    curses.init_pair(3, banner_text, banner)

    j = 0
    for k in range(4,10):        
        curses.init_pair(k, NEGRO,COLORS[j])
        j += 1
        
    
    curses.halfdelay(10)
    
def mkcap_format(mkcap):
    mkcap = str(mkcap).split('.')[0]
    mkcaplen = len(mkcap)
    
    if mkcaplen== 4:
        mkcap = mkcap[0] + '.' +  mkcap[1:3] + "K"
        
    elif mkcaplen== 5:
        mkcap = mkcap[0:2] + '.' +  mkcap[2:4] + "K"
        
    elif mkcaplen== 6:
        mkcap = mkcap[0:3] + '.' +  mkcap[3:5] + "K"
        
    elif mkcaplen== 7:
        mkcap = mkcap[0] + '.' +  mkcap[1:3] + "M"
        
    elif mkcaplen== 8:
        mkcap = mkcap[0:2] + '.' +  mkcap[2:4] + "M"
        
    elif mkcaplen== 9:
        mkcap = mkcap[0:3] + '.' +  mkcap[3:5] + "M"
        
    elif mkcaplen== 10:
        mkcap = mkcap[0] + '.' +  mkcap[1:3] + "B"
        
    elif mkcaplen== 11:
        mkcap = mkcap[0:2] + '.' +  mkcap[2:4] + "B"
        
    elif mkcaplen== 12:
        mkcap = mkcap[0:3] + '.' +  mkcap[3:5] + "B"
        
    elif mkcaplen== 13:
        mkcap = mkcap[0] + '.' +  mkcap[1:3] + "T"
            
    else:
        print(mkcap)
    return mkcap
            
    

def str_formatter(coin, val, held, change,mkcap):
    '''Prepare the coin strings as per ini length/decimal place values'''
    locale._override_localeconv = {'frac_digits':CONFIG['theme'].getint('dec_places', 2)}
    max_length = CONFIG['theme'].getint('field_length', 13)
    dec_place = CONFIG['theme'].getint('dec_places', 3)
    avg_length = CONFIG['theme'].getint('dec_places', 2) + 10
    held_str = '{:>{},.8f}'.format(float(held), max_length)
    val_str = '{:>{},.{}f}'.format(float(held) * val[0], max_length, dec_place)
    return '  {:<7} {:>{}}  {:>{}}  {:>{}} {:>{}} {:>{}} {:>{}} {:>{}}'.format(coin,
        locale.currency(val[0], grouping=True)[:max_length], avg_length+1,
        held_str[:max_length], max_length + 3,
        locale.currency(float(held) * val[0], grouping=True)[:max_length], avg_length,
        locale.currency(val[1], grouping=True)[:max_length], avg_length,
        locale.currency(val[2], grouping=True)[:max_length], avg_length,
        change[:max_length], avg_length,
        mkcap_format(mkcap),avg_length)

def write_scr(stdscr, wallet, y, x):


    coin_distribution = {}
    char_distribution = {}
    charcar = '░'
    coinl = list(wallet.keys())
    heldl = list(wallet.values())
    
    if coinl:
        coinvl = get_price(','.join(coinl))
        coinchg = get_change(','.join(coinl))
    else:
        coinvl = []
        coinchg = []
    
    stdscr.erase()
    '''Write text and formatting to screen'''
    first_pad = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10)
    second_pad = ' ' * (CONFIG['theme'].getint('field_length', 13) - 2)
    third_pad =  ' ' * (CONFIG['theme'].getint('field_length', 13))
    fourth_pad = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10 - 2)
    fifth_pad = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10 - 3)
    last_pad = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10 - 5)
    tlast_pad = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10 - 5)
    
    if y >= 1:
        stdscr.addnstr(0, 0, CRYPTOP_VERSION, x, curses.color_pair(2))
    if y >= 2:
        header = '  COIN{}PRICE{}HELD {}VAL{}HIGH {}LOW {}CHANGE {}MKCAP   '.format(first_pad, second_pad, third_pad, fourth_pad, fifth_pad, last_pad, tlast_pad)
        stdscr.addnstr(1, 0, header, x, curses.color_pair(3))

    total = 0
    coinl = list(wallet.keys())
    heldl = list(wallet.values())
    if coinvl and coinchg:
        
        if y > 3:
            s = sorted(list(zip(coinl, coinvl, heldl)), key=SORT_FNS[SORTS[COLUMN]], reverse=ORDER)
            coinl = list(x[0] for x in s)
            coinvl = list(x[1] for x in s)
            heldl = list(x[2] for x in s)
            for coin, val, held in zip(coinl, coinvl, heldl):
                if coinl.index(coin) + 2 < y:
                    stdscr.addnstr(coinl.index(coin) + 2, 0,
                    str_formatter(coin, val, held,coinchg[coin],float(cmcqJSON['data'][coin]['quote']['USD']['market_cap'])), x, curses.color_pair(2))
                total += float(held) * val[0]
                
        for coin, val, held in zip(coinl, coinvl, heldl):
            #coin_distribution[coin] = float((float(held) * val[0])/total)
            portfolio_pct = float((float(held) * val[0])/total)
            char_distribution[coin] = int(portfolio_pct*x)
            coin_distribution[coin] = round(portfolio_pct*100,2)
            
    if y > len(coinl)*2 + 3:
        k = 0
        j = 3 
        for ckey in char_distribution.keys():
            if j % 10 == 0:
                j = 3;  
            stdscr.addnstr(y - len(coinl) - 4 + k,0, ckey  + ' '*(4 - len(ckey))+ charcar*char_distribution[ckey],x,curses.color_pair(j))
            stdscr.addstr(str(coin_distribution[ckey]) + '%', curses.color_pair(2))
            k += 1
            j += 1
        stdscr.addnstr(y - 3, 0, 'Total Holdings: {:10}    '
            .format(locale.currency(total, grouping=True)), x, curses.color_pair(3))
        stdscr.addnstr(y - 2, 0,
            '[F5]Refresh [A] Add/update coin [R] Remove coin [S] Sort [C] Cycle sort [0\Q]Exit', x,
            curses.color_pair(2))
        stdscr.addnstr(y - 1,0, '[+] Add To Coin [-] Subtract From Coin',x,curses.color_pair(2))

def init_wallet_delta(wallet):
    coinl = list(wallet.keys())
    heldl = list(wallet.values())
    
    if coinl:
        coinvl = get_price(','.join(coinl))

def read_wallet():
    ''' Reads the wallet data from its json file '''
    try:
        with open(DATAFILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        # missing or malformed wallet
        write_wallet({}, DATAFILE)
        return {}

def read_wallet_delta():
    try:
        with open(PORTFILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}
    '''
        # missing or malformed wallet
        if os.path.exists(DATAFILE):
            wallet_delta = read_wallet()
            write_wallet(wallet_delta,PORTFILE)
            return wallet_delta
        else:
            return {}
    '''
        
def write_wallet(wallet, DATAFILE):
    ''' Write wallet data to its json file '''
    with open(DATAFILE, 'w') as f:
        json.dump(wallet, f)


def get_string(stdscr, prompt):
    '''Requests and string from the user'''
    curses.echo()
    stdscr.clear()
    stdscr.addnstr(0, 0, prompt, -1, curses.color_pair(2))
    curses.curs_set(1)
    stdscr.refresh()
    in_str = stdscr.getstr(1, 0, 20).decode()
    curses.noecho()
    curses.curs_set(0)
    stdscr.clear()
    curses.halfdelay(10)
    return in_str


def add_coin(coin_amount, wallet):
    ''' Add a coin and its amount to the wallet '''
    coin_amount = coin_amount.upper()
    if not COIN_FORMAT.match(coin_amount):
        return wallet

    coin, amount = coin_amount.split(',')

    if not if_coin(coin):
        return wallet

    if not amount:
        amount = "0"

    wallet[coin] = amount
    return wallet

def change_value_to_coin(coin_amount, wallet, subtract):
    coin_amount = coin_amount.upper()
    if not COIN_FORMAT.match(coin_amount):
        return wallet

    coin, amount = coin_amount.split(',')

    if not if_coin(coin):
        return wallet

    if not amount:
        amount = "0"
    if coin in wallet.keys():    
        if subtract:
            if float(wallet[coin]) >= float(amount):
                wallet[coin] = float(wallet[coin]) - float(amount)
            else:
                wallet[coin] = 0
        else:
            wallet[coin] = float(wallet[coin]) + float(amount)
    else:
        wallet[coin] = float(amount)
    return wallet

def remove_coin(coin, wallet):
    ''' Remove a coin and its amount from the wallet '''
    # coin = '' if window is resized while waiting for string
    if coin:
        coin = coin.upper()
        wallet.pop(coin, None)
    return wallet

def mainc(stdscr):
    inp = 0
    wallet = read_wallet()
    y, x = stdscr.getmaxyx()
    conf_scr()
    stdscr.bkgd(' ', curses.color_pair(2))
    stdscr.clear()
    message = "REFRESHING ⟳"
    #stdscr.nodelay(1)
    # while inp != 48 and inp != 27 and inp != 81 and inp != 113:
    k = 1
    while inp not in {KEY_ZERO, KEY_ESCAPE, KEY_Q, KEY_q}:
        try:
            if k == 1:
                write_scr(stdscr, wallet, y, x)
                k += 1
        except curses.error:
            pass
        inp = stdscr.getch()
        #if inp != curses.KEY_RESIZE:
        #    break
        y, x = stdscr.getmaxyx()
        if inp == KEY_F5:
            try:
                wallet = read_wallet()
                stdscr.addstr(int(y/2)-1, int(x/2) - int(len(message)),
                               message, curses.color_pair(3)|curses.A_BOLD)
                stdscr.refresh()
                write_scr(stdscr, wallet, y, x)
            except curses.error:
                pass
        if inp in {KEY_PLUS, KEY_plus}:
            if y > 2:
                data = get_string(stdscr,
                        'Enter in format Symbol,Amount e.g. BTC,10')
                wallet = read_wallet()
                wallet = change_value_to_coin(data,wallet, False)
                write_wallet(wallet,DATAFILE)
                stdscr.erase()
                write_scr(stdscr, wallet, y, x)

        if inp in {KEY_MINUS, KEY_minus}:
            if y > 2:
                data = get_string(stdscr,
                        'Enter in format Symbol,Amount e.g. BTC,10')
                wallet = read_wallet()
                wallet = change_value_to_coin(data,wallet, True)
                write_wallet(wallet,DATAFILE)
                stdscr.erase()
                write_scr(stdscr, wallet, y, x)

        if inp in {KEY_a, KEY_A}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter in format Symbol,Amount e.g. BTC,10')
                wallet = read_wallet()
                wallet = add_coin(data, wallet)
                write_wallet(wallet, DATAFILE)
                write_scr(stdscr, wallet, y, x)

        if inp in {KEY_r, KEY_R}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter the symbol of coin to be removed, e.g. BTC')
                wallet = read_wallet()
                wallet = remove_coin(data, wallet)
                write_wallet(wallet, DATAFILE)
                write_scr(stdscr, wallet, y, x)

        if inp in {KEY_s, KEY_S}:
            if y > 2:
                global ORDER
                ORDER = not ORDER

        if inp in {KEY_c, KEY_C}:
            if y > 2:
                global COLUMN
                COLUMN = (COLUMN + 1) % len(SORTS)

def main():
    if os.path.isfile(BASEDIR):
        sys.exit('Please remove your old configuration file at {}'.format(BASEDIR))
    os.makedirs(BASEDIR, exist_ok=True)

    global CONFIG
    CONFIG = read_configuration(CONFFILE)
    locale.setlocale(locale.LC_MONETARY, CONFIG['locale'].get('monetary', ''))

    requests_cache.install_cache(cache_name='api_cache', backend='memory',
        expire_after=int(CONFIG['api'].get('cache', 10)))

    parser = argparse.ArgumentParser(description=CRYPTOP_VERSION)
    parser.add_argument('-k', '--cc-api-key', default=os.environ.get('CCOMPARE_API_KEY'),help='CryptoCompare API key (key) (OR edit config.ini in ~/.cryptop folder)')
    parser.add_argument('-l', '--cmc-api-key', default=os.environ.get('CMC_API_KEY'),help='CoinMarketCap API key (key2) (OR edit config.ini in ~/.cryptop folder)')
    global CCOMPARE_API_KEY
    global CMC_API_KEY
    CCOMPARE_API_KEY = CONFIG['api'].get('key', '')
    CMC_API_KEY      = CONFIG['api'].get('key2', '')
    
    args = parser.parse_args()
    
    if not args.cc_api_key and not CCOMPARE_API_KEY:
        parser.error('Please specify an API key for CryptoCompare')
    
    if not args.cmc_api_key and not CMC_API_KEY:
        parser.error('Please Specify an API key for CoinMarketCap')
    
    if args.cc_api_key and not CCOMPARE_API_KEY:
        CCOMPARE_API_KEY = args.cc_api_key
    
    if args.cmc_api_key and not CMC_API_KEY:
        CMC_API_KEY = args.cmc_api_key
    
    get_coin_list()
    curses.wrapper(mainc)


if __name__ == "__main__":
    main()
