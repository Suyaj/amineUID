""" init """

from gsuid_core.sv import Plugins

Plugins(name="amineUID", force_prefix=['am', 'AM', 'wiki', 'jm'], allow_empty_prefix=False)
