""" init """

from gsuid_core.sv import Plugins

Plugins(name="amineUID", force_prefix=['am', 'AM'], allow_empty_prefix=False)
