#!/usr/bin/python
# SPDX-FileCopyrightText: 2025 Mohamed Chamrouk <mohamed.chamrouk@proton.me>
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

import sys

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kpfleming.powerdns_auth.plugins.module_utils.api_wrapper import (
    APIWrapper,
    api_exception_handler,
)

assert sys.version_info >= (3, 9), "This module requires Python 3.9 or newer."

DOCUMENTATION = """
%YAML 1.2
---

author:
  - Kevin P. Fleming (@kpfleming)
"""

EXAMPLES = """
%YAML 1.2
---
"""

RETURN = """
%YAML 1.2
---
"""


class APIZoneWrapper(APIWrapper):
    def __init__(self, *, module, result, object_type, zone_id):
        super().__init__(module=module, result=result, object_type=object_type)
        self.zone_id = zone_id

    @api_exception_handler
    def listZones(self, **kwargs):  # noqa: N802
        return self.raw_api.listZones(server_id=self.server_id, **kwargs).result()


class APICryptokeyWrapper(APIWrapper):
    def __init__(self, *, module, result, object_type, zone_id, cryptokey_id):
        super().__init__(module=module, result=result, object_type=object_type)
        self.zone_id = zone_id
        self.cryptokey_id = cryptokey_id

    @api_exception_handler
    def listCryptokeys(self):
        return self.raw_api.listCryptokeys(
            server_id=self.server_id,
            zone_id=self.zone_id,
        ).result()

    @api_exception_handler
    def createCryptokey(self, **kwargs):
        return self.raw_api.createCryptokey(
            server_id=self.server_id,
            zone_id=self.zone_id,
            **kwargs,
        ).result()

    @api_exception_handler
    def getCryptokey(self):
        return self.raw_api.getCryptokey(
            server_id=self.server_id, zone_id=self.zone_id, cryptokey_id=self.cryptokey_id
        ).result()

    @api_exception_handler
    def modifyCryptokey(self, **kwargs):
        return self.raw_api.modifyCryptokey(
            server_id=self.server_id, zone_id=self.zone_id, cryptokey_id=self.cryptokey_id, **kwargs
        ).result()

    @api_exception_handler
    def deleteCryptokey(self, **kwargs):
        return self.raw_api.deleteCryptokey(
            server_id=self.server_id, zone_id=self.zone_id, cryptokey_id=self.cryptokey_id
        ).result()


def main():
    module_args = {
        "state": {
            "type": "str",
            "default": "present",
            "choices": ["present", "absent", "exists"],
        },
        "zone_name": {
            "type": "str",
            "required": True,
        },
        "server_id": {
            "type": "str",
            "default": "localhost",
        },
        "api_url": {
            "type": "str",
            "default": "http://localhost:8081",
        },
        "api_spec_path": {
            "type": "str",
            "default": "/api/docs",
        },
        "api_key": {
            "type": "str",
            "required": True,
            "no_log": True,
        },
        "cryptokey_id": {
            "type": "str",
        },
        "cryptokey": {
            "type": "dict",
            "options": {
                "keytype": {"type": "str", "required": True, "choices": ["zsk", "ksk", "csk"]},
                "active": {"type": "bool", "default": False},
                "published": {"type": "bool", "default": True},
                "dnskey": {"type": "str", "required": False},
                "privatekey": {"type": "str", "required": False},
                "algorithm": {"type": "str", "required": False},
                "bits": {"type": "int", "default": 4096},
            },
        },
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=(("state", "present", ["cryptokey"]), ("state", "absent", ["cryptokey_id"])),
    )

    result = {
        "changed": False,
        "cryptokey": {},
        "cryptokeys": []
    }

    params = module.params
    state = params["state"]
    zone_name = params["zone_name"]

    api_zone_client = APIZoneWrapper(
        module=module, result=result, object_type="zones", zone_id=None
    )

    api_cryptokey_client = APICryptokeyWrapper(
        module=module, result=result, object_type="zonecryptokey", zone_id=None, cryptokey_id=None
    )

    partial_zone_info = api_zone_client.listZones(zone=zone_name)

    if len(partial_zone_info) == 0:
        module.fail_json(msg=f"No zone found for name {zone_name}", **result)

    zone_id = partial_zone_info[0]["id"]
    api_cryptokey_client.zone_id = zone_id

    existing_zone_keys = api_cryptokey_client.listCryptokeys()

    if state == "exists":
        result["exists"] = False
        if params["cryptokey_id"] is not None:
            api_cryptokey_client.cryptokey_id = params["cryptokey_id"]
            result["cryptokey"] = api_cryptokey_client.getCryptokey()
        else:
            result["cryptokeys"] = existing_zone_keys

        if result["cryptokey"] or result["cryptokeys"]:
            result["exists"] = True
    elif state == "present":
        cryptokey_def = params["cryptokey"]
        if params["cryptokey_id"] is None:
            if cryptokey_def["keytype"] is None:
                module.fail_json(msg="Missing keytype option in cryptokey definition", **result)

            generated_key_fields = ["algorithm"]
            imported_key_fields = ["dnskey", "privatekey"]
            common_fields = ["keytype", "active", "published"]

            if cryptokey_def["algorithm"] is not None:
                if "rsa" in cryptokey_def["algorithm"].lower():
                    generated_key_fields += ["bits"]
                result_fields = common_fields + generated_key_fields
            elif cryptokey_def["privatekey"] is not None and cryptokey_def["dnskey"] is not None:
                result_fields = common_fields + imported_key_fields
            else:
                module.fail_json(msg="Wrong options provided for cryptokey creation", **result)

            cryptokey = {field: cryptokey_def[field] for field in result_fields}

            api_cryptokey_client.createCryptokey(cryptokey=cryptokey)
        else:
            cryptokeys_ids = [str(key["id"]) for key in existing_zone_keys]

            if params["cryptokey_id"] in cryptokeys_ids:
                cryptokey = {
                    "active": cryptokey_def["active"],
                    "published": cryptokey_def["published"],
                }
            else:
                module.fail_json(
                    msg=f"Key of id {params['cryptokey_id']} not found for zone {params['zone_name']}",
                    **result,
                )

            api_cryptokey_client.cryptokey_id = params["cryptokey_id"]
            api_cryptokey_client.modifyCryptokey(cryptokey=cryptokey)

        result["changed"] = True
    else:
        cryptokeys_ids = [str(key["id"]) for key in existing_zone_keys]
        cryptokey_id = params["cryptokey_id"]

        if cryptokey_id in cryptokeys_ids:
            api_cryptokey_client.cryptokey_id = cryptokey_id
            api_cryptokey_client.deleteCryptokey()
        else:
            module.fail_json(
                msg=f"Key of id {params['cryptokey_id']} not found for zone {params['zone_name']}",
                **result,
            )

        result["changed"] = True

    if result["changed"]:
        result["cryptokeys"] = api_cryptokey_client.listCryptokeys()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
