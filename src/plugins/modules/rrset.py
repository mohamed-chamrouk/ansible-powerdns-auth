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


class APIZoneRRSetWrapper(APIWrapper):
    def __init__(self, *, module, result, object_type, zone_id):
        super().__init__(module=module, result=result, object_type=object_type)
        self.zone_id = zone_id

    @api_exception_handler
    def listZone(self):  # noqa: N802
        return self.raw_api.listZone(
            server_id=self.server_id,
            zone_id=self.zone_id,
            rrsets=True,
        ).result()

    @api_exception_handler
    def listZones(self, **kwargs):  # noqa: N802
        return self.raw_api.listZones(server_id=self.server_id, **kwargs).result()

    @api_exception_handler
    def patchZone(self, **kwargs):  # noqa: N802
        return self.raw_api.patchZone(
            server_id=self.server_id,
            zone_id=self.zone_id,
            **kwargs,
        ).result()


def build_zone_result(api_client):
    api_zone = api_client.listZone()
    z = {
        "exists": True,
        **api_zone,
    }

    return api_zone, z


def safe_string_record(record_type, record, type_def):
    record_spec = type_def[record_type]

    safe_record = record

    if len(record_spec["options"]) > 2:
        for field in record_spec["options"].items():
            if field[0] in record and field[1]["type"] == "raw":
                value = safe_record[field[0]]
                safe_record[field[0]] = '"' + value.removeprefix('"').removesuffix('"') + '"'

    return safe_record


def main():
    module_args = {
        "state": {
            "type": "str",
            "default": "present",
            "choices": ["present", "absent"],
        },
        "name": {
            "type": "str",
            "required": True,
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
        "algorithm": {
            "type": "str",
            "default": "hmac-md5",
            "choices": [
                "hmac-md5",
                "hmac-sha1",
                "hmac-sha224",
                "hmac-sha256",
                "hmac-sha384",
                "hmac-sha512",
            ],
        },
        "keep": {
            "type": "bool",
            "default": False,
        },
        "ttl": {
            "type": "int",
            "default": 3600,
        },
        "type": {
            "type": "str",
        },
        "records": {
            "type": "list",
            "elements": "dict",
            "options": {
                "disabled": {
                    "type": "bool",
                    "default": False,
                },
                "content": {
                    "type": "str",
                    "required": True,
                },
            },
        },
        "A": {
            "type": "list",
            "elements": "dict",
            "options": {
                "address": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "AAAA": {
            "type": "list",
            "elements": "dict",
            "options": {
                "address": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "CAA": {
            "type": "list",
            "elements": "dict",
            "options": {
                "flags": {"type": "int", "required": False, "default": 0, "choices": [0, 1]},
                "tag": {"type": "str", "required": True},
                "value": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "CNAME": {
            "type": "list",
            "elements": "dict",
            "options": {
                "cname": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "DNSKEY": {
            "type": "list",
            "elements": "dict",
            "options": {
                "flags": {"type": "int", "required": True, "choices": [256, 257]},
                "protocol": {"type": "int", "required": True, "choices": [3]},
                "algorithm": {"type": "int", "required": True},
                "public_key": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "DS": {
            "type": "list",
            "elements": "dict",
            "options": {
                "key_tag": {"type": "int", "required": True},
                "algorithm": {"type": "int", "required": True},
                "digest_type": {"type": "int", "required": True, "choices": [1, 2, 3, 4]},
                "digest": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "HINFO": {
            "type": "list",
            "elements": "dict",
            "options": {
                "cpu": {"type": "raw", "required": True},
                "os": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "HTTPS": {
            "type": "list",
            "elements": "dict",
            "options": {
                "priority": {"type": "int", "required": True},
                "target": {"type": "str", "required": True},
                "params": {"type": "str", "required": False},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "LOC": {
            "type": "list",
            "elements": "dict",
            "options": {
                "latitude": {"type": "str", "required": True},
                "longitude": {"type": "str", "required": True},
                "altitude": {"type": "str", "required": True},
                "size": {"type": "str", "required": False, "default": "1.0m"},
                "horizontal_precision": {"type": "str", "required": False, "default": "10000.0m"},
                "vertical_precision": {"type": "str", "required": False, "default": "10.0m"},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "MX": {
            "type": "list",
            "elements": "dict",
            "options": {
                "preference": {"type": "int", "required": True},
                "exchange": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "NAPTR": {
            "type": "list",
            "elements": "dict",
            "options": {
                "order": {"type": "int", "required": True},
                "preference": {"type": "int", "required": True},
                "flags": {"type": "str", "required": True},
                "services": {"type": "str", "required": True},
                "regexp": {"type": "raw", "required": True},
                "replacement": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "NS": {
            "type": "list",
            "elements": "dict",
            "options": {
                "host": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "NSEC": {
            "type": "list",
            "elements": "dict",
            "options": {
                "next_domain": {"type": "str", "required": True},
                "type_bitmap": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "NSEC3": {
            "type": "list",
            "elements": "dict",
            "options": {
                "hash_algorithm": {"type": "int", "required": True, "choices": [1]},
                "flags": {"type": "int", "required": True, "choices": [0, 1]},
                "iterations": {"type": "int", "required": True},
                "salt": {"type": "str", "required": True},
                "next_hashed": {"type": "str", "required": True},
                "type_bitmap": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "NSEC3PARAM": {
            "type": "list",
            "elements": "dict",
            "options": {
                "hash_algorithm": {"type": "int", "required": True, "choices": [1]},
                "flags": {"type": "int", "required": True, "choices": [0, 1]},
                "iterations": {"type": "int", "required": True},
                "salt": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "PTR": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ptrdname": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "RP": {
            "type": "list",
            "elements": "dict",
            "options": {
                "mbox": {"type": "raw", "required": True},
                "txt": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "RRSIG": {
            "type": "list",
            "elements": "dict",
            "options": {
                "type_covered": {"type": "str", "required": True},
                "algorithm": {"type": "int", "required": True},
                "labels": {"type": "int", "required": True},
                "original_ttl": {"type": "int", "required": True},
                "signature_expiration": {"type": "str", "required": True},
                "signature_inception": {"type": "str", "required": True},
                "key_tag": {"type": "int", "required": True},
                "signer_name": {"type": "str", "required": True},
                "signature": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "SPF": {
            "type": "list",
            "elements": "dict",
            "options": {
                "strings": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "SOA": {
            "type": "list",
            "elements": "dict",
            "options": {
                "mname": {"type": "str", "required": True},
                "rname": {"type": "str", "required": True},
                "serial": {"type": "int", "required": False},
                "refresh": {"type": "int", "required": False},
                "retry": {"type": "int", "required": False},
                "expire": {"type": "int", "required": False},
                "minimum": {"type": "int", "required": False},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "SRV": {
            "type": "list",
            "elements": "dict",
            "options": {
                "priority": {"type": "int", "required": True},
                "weight": {"type": "int", "required": True},
                "port": {"type": "int", "required": True},
                "target": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "SSHFP": {
            "type": "list",
            "elements": "dict",
            "options": {
                "algorithm": {"type": "int", "required": True, "choices": [1, 2, 3, 4, 6]},
                "fp_type": {"type": "int", "required": True, "choices": [1, 2, 3]},
                "fingerprint": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "SVCB": {
            "type": "list",
            "elements": "dict",
            "options": {
                "priority": {"type": "int", "required": True},
                "target": {"type": "str", "required": True},
                "params": {"type": "str", "required": False},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "TLSA": {
            "type": "list",
            "elements": "dict",
            "options": {
                "usage": {"type": "int", "required": True, "choices": [0, 1, 2, 3]},
                "selector": {"type": "int", "required": True, "choices": [0, 1]},
                "matching_type": {"type": "int", "required": True, "choices": [0, 1, 2]},
                "cert_assoc_data": {"type": "str", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
        "TXT": {
            "type": "list",
            "elements": "dict",
            "options": {
                "strings": {"type": "raw", "required": True},
                "disabled": {"type": "bool", "required": False, "default": False},
            },
        },
    }

    record_types = [
        "A",
        "AAAA",
        "CAA",
        "CNAME",
        "DNSKEY",
        "DS",
        "HINFO",
        "HTTPS",
        "LOC",
        "MX",
        "NAPTR",
        "NS",
        "NSEC",
        "NSEC3",
        "NSEC3PARAM",
        "PTR",
        "RP",
        "RRSIG",
        "SPF",
        "SOA",
        "SRV",
        "SSHFP",
        "SVCB",
        "TLSA",
        "TXT",
    ]

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[(record_type, "records") for record_type in record_types]
        + [(record_type, "type") for record_type in record_types],
        required_one_of=[record_types + ["type"]],
        required_if=[("state", "absent", record_types + ["type"], True)],
    )

    state = module.params["state"]
    zone_name = module.params["zone_name"]

    result = {
        "changed": False,
    }

    # create an object to proxy the raw API object
    # and carry the server_id into all API calls
    # automatically, along with handling
    # predictable exceptions
    api_client = APIZoneRRSetWrapper(
        module=module, result=result, object_type="zones", zone_id=None
    )

    partial_zone_info = api_client.listZones(zone=zone_name)

    if len(partial_zone_info) == 0:
        module.fail_json(f"Failed to find zone named {zone_name}")
    else:
        # get the full zone info and populate the result dict
        zone_id = partial_zone_info[0]["id"]
        api_client.zone_id = zone_id
        zone_info, result["zone"] = build_zone_result(api_client)

    params = module.params
    changetype = "REPLACE" if params["state"] == "present" else "DELETE"
    rrset_record_types = list(set([p for p in params if params[p] is not None]) & set(record_types))

    # Check couldn't fit in AnsibleModule args
    type_classic = "type" in params and "records" in params
    if params["state"] == "present" and not (type_classic or rrset_record_types):
        module.fail_json("State is present but no valid record has been provided")

    if rrset_record_types:
        rrset_records = [
            {
                "type": type,
                "records": [safe_string_record(
                    type, record, {type: module_args[type] for type in record_types}
                ) for record in params[type]],
            }
            for type in rrset_record_types
        ]

        rrsets_struct = []
        records = []

        for rrset in rrset_records:
            for record in rrset["records"]:
                disabled = record.pop("disabled")
                records += [{"disabled": disabled, "content": " ".join(map(str, record.values()))}]

            rrsets_struct += [
                {
                    "name": params["name"],
                    "type": rrset["type"],
                    "ttl": params["ttl"],
                    "keep": params["keep"],
                    "changetype": changetype,
                    "records": records,
                }
            ]

            records = []
    else:
        rrsets_struct = [
            {
                "name": params["name"],
                "type": params["type"],
                "ttl": params["ttl"],
                "keep": params["keep"],
                "changetype": changetype,
                "records": params["records"] if "records" in params else [],
            }
        ]

    zone_struct = {}
    print(rrsets_struct)

    for rrset in rrsets_struct:
        # Retrieving existing rrset, there can only be one
        # that matches "name" and "type" values.
        existing_rrset = next(
            (
                r
                for r in zone_info["rrsets"]
                if r["name"] == rrset["name"] and r["type"] == rrset["type"]
            ),
            None,
        )

        rrset_changetype = rrset["changetype"]
        rrset_keep = rrset.pop(
            "keep"
        )  # Keeping the option out for cleaner zone_struct on subsequent unpacking

        if not existing_rrset or not rrset_keep:
            if rrset_changetype == "REPLACE":
                if rrset["type"] is not None:
                    zone_struct.setdefault("rrsets", []).append(rrset)
                else:
                    module.fail_json("No valid record found for rrset creation.")
            elif rrset_changetype == "DELETE":
                if existing_rrset:
                    zone_struct.setdefault("rrsets", []).append(rrset)
                else:
                    module.fail_json(
                        f"No matching rrset found for name: {rrset['name']} and type: {rrset['type']}"
                    )
        elif rrset["records"] == existing_rrset["records"]:
            # Despite keep being present, if existing records and given ones match
            # exactly then for changetype="DELETE",
            # the final operation is to delete the whole rrset.
            # If the changetype is "REPLACE",
            # nothing is done for the rest of the rrset
            if rrset_changetype == "DELETE":
                # Using .setdefault to avoid creating a key on dict zone_struct
                # and keep the dict empty for idempotency
                zone_struct.setdefault("rrsets", []).append(
                    {
                        "name": rrset["name"],
                        "type": rrset["type"],
                        "changetype": "DELETE",
                    }
                )
        else:
            if rrset_changetype == "REPLACE":
                # Building a list of unique union of existing and provided records
                new_records_list = existing_rrset["records"] + [
                    record for record in rrset["records"] if record not in existing_rrset["records"]
                ]
            else:
                # Building a list of remaining records
                # after removing provided ones from existing ones
                new_records_list = [] + [
                    r for r in existing_rrset["records"] if r not in rrset["records"]
                ]

            if new_records_list != existing_rrset["records"]:
                zone_struct.setdefault("rrsets", []).append(
                    {
                        **rrset,
                        "records": new_records_list,
                        "changetype": "REPLACE",
                    }
                )

    if module.check_mode:
        module.exit_json(**result)

    if zone_struct:
        api_client.patchZone(zone_struct=zone_struct)
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()
