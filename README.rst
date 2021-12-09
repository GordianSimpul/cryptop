cryptop
=======
cryptop is a lightweight command line based cryptocurrency portfolio.
Built on Python 3 and ncurses with simplicity in mind, cryptop updates in realtime.

.. image:: img\cryptop.png

version 1.0.0

Changes
------------

This now requires a CryptoCompare.com and CoinMarketCap.com API key because of rate limits and extra data points.

See the Credits section on how to get an API key.

Added option for extra decimal places in .cryptop/config.ini based on currency.locale

Fixed + add coin user error to just add coin instead of error.

Added Market Cap from CoinMarketCap. API required.

Reads wallet every refresh and entry. Enables cryptop to be run on multiple computers from within a sharedrive.

Less url requests. Coin list is fetched every 10 days, instead of 
every coin addition. Speeds up processing of app.


TODO
------------

* Instead of using CC for 24h +/-, data already fetched from CMC in quote. Use CMC quote data for less requests.
* Add average price paid within wallet. Requires an addition "history" wallet.
* More historical portfolio changes.
* Coin Value +/- with mrkt conditions.
* History interface to interact with coin additions / subtractions.


Installation
------------

cryptop requires Python 3 to run, and has only been tested in Python 3.6 so far.

First clone this repo

.. code:: bash

    git clone https://github.com/GordianSimpul/cryptop

Then install cryptop through pip

.. code:: bash

    cd cryptop
    pip3 install -e .

cryptop can be installed manually, download the repo and run

.. code:: bash

    python setup.py install

pip and setup.py can be run with a --user flag if you would prefer not to sudo. Both require setuptools which is included in most python installs and many distros by default

Make sure $HOME/.local/bin is in your environment PATH variable. 

Usage
-----

Start from a terminal.

.. code:: bash

    cryptop [-k api_key] [-l api_key]

Follow the on screen instructions to add/remove or add/subtract values from your current wallet. The api_key options are only necessary if you didn't specify it in the .cryptop/config.ini file.

.cryptop/config.ini

key=CryptoComare API KEY
key2=CoinMarketCap API KEY

Both of those need to edited o/w cryptop will not work.

Customisation
-------------

Cryptop creates two config files in a .cryptop folder in your home directory.

.cryptop/config.ini contains theme configuration (text/background colors) and
options to change the output currency (default USD), update frequency, number of decimal places to display and maximum width for float values.

.cryptop/wallet.json contains the coins and amounts you hold, you shouldn't need to edit it manually

Credits / API
-------------

Both are FREE.

Uses the `cryptocompare.com API
<http://www.cryptocompare.com/>`_.

Uses the `coinmarketcap.com API
<https://coinmarketcap.com/api>`_.

Tipjar
-------------

Help me reach my goal of contributing to the ongoing development of privacy coins

.. code:: bash

    XMR: 83NTepxXzoPjSN6cAKaoBvat5mqMWUW2C9RJKeu6kWu8LX5cXMBE2sFR4hedAiUwfzjQwHbEq9tyz148sB2qHqn4DB8tYQQ

.. code:: bash

    DERO: dERoNwMa3wEdMgG8bswFVzcjTqcBSicwGT8YQAeYkYrJ2ZAVZhp5uDqYayeaCehTUn8yWUmjnzxX95KY6pK6gSuj4qDevpJnDa

.. code:: bash

    BTC: bc1qvfsqzfz4gud05p7mmgm7kwv6cx7p4k7tcd5sdn



Disclaimer
----------

I am not liable for the accuracy of this program’s output nor actions
performed based upon it.
