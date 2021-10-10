cryptop
=======
cryptop is a lightweight command line based cryptocurrency portfolio.
Built on Python 3 and ncurses with simplicity in mind, cryptop updates in realtime.

.. image:: img\cryptop.png

Changes
------------

I've added the ability to add/subtract values from your wallet within the interface. 
This now requires a CryptoCompare.com API key due to rate limits enforced since the creation of this app.

Instead of it automatically refreshing, you now press 'F5' to refresh. This will save on your API calls and 
it really didn't need to be refreshing on an interval. 


Installation
------------

cryptop requires Python 3 to run, and has only been tested in Python 3.6 so far.

First clone this repo

.. code:: bash

    git clone https://github.com/GordianSimpul/cryptop

Then install cryptop through pip

.. code:: bash

    pip3 install -e cryptop .

cryptop can be installed manually, download the repo and run

.. code:: bash

    python setup.py install

pip and setup.py can be run with a --user flag if you would prefer not to sudo. Both require setuptools which is included in most python installs and many distros by default

Make sure $HOME/.local/bin is in your environment PATH variable. 

Usage
-----

Start from a terminal.

.. code:: bash

    cryptop [-k api_key]

Follow the on screen instructions to add/remove cryptocurrencies from your portfolio or add/subtract values from your current wallet. The api_key option is only necessary if you didn't specify it in the .crypto/config.ini file

Customisation
-------------

Cryptop creates two config files in a .cryptop folder in your home directory.

.crypto/config.ini contains theme configuration (text/background colors) and
options to change the output currency (default USD), update frequency, number of decimal places to display and maximum width for float values.

.. image:: img\fall.png

.. image:: img\aesth.png

.cryptop/wallet.json contains the coins and amounts you hold, you shouldn't need to edit it manually

Credits
-------

Uses the `cryptocompare.com API
<http://www.cryptocompare.com/>`_.

Tipjar
------

Help me reach my goal of contributing to all privacy-coin's ongoing development 

.. code:: bash

    XMR: 83NTepxXzoPjSN6cAKaoBvat5mqMWUW2C9RJKeu6kWu8LX5cXMBE2sFR4hedAiUwfzjQwHbEq9tyz148sB2qHqn4DB8tYQQ

.. code:: bash

    BTC: bc1qvfsqzfz4gud05p7mmgm7kwv6cx7p4k7tcd5sdn

Disclaimer
----------

I am not liable for the accuracy of this program’s output nor actions
performed based upon it.
