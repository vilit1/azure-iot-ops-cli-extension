# coding=utf-8
# ----------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License file in the project root for license information.
# ----------------------------------------------------------------------------------------------

import pytest
from os import mkdir, path
from knack.log import get_logger
from typing import Dict, List, Optional, Tuple
from azext_edge.edge.common import OpsServiceType
from .helpers import (
    assert_file_names,
    check_workload_resource_files,
    get_file_map,
    process_top_levels,
    run_bundle_command,
    BASE_ZIP_PATH
)
from ....helpers import find_extra_or_missing_names

logger = get_logger(__name__)


def generate_bundle_test_cases() -> List[Tuple[str, bool, Optional[str]]]:
    # case = ops_service, mq_traces, bundle_dir
    cases = [(service, False, "support_bundles") for service in OpsServiceType.list()]
    cases.append((OpsServiceType.mq.value, True, None))
    return cases


@pytest.mark.parametrize("ops_service, mq_traces, bundle_dir", generate_bundle_test_cases())
def test_create_bundle(init_setup, bundle_dir, mq_traces, ops_service, tracked_files):
    """Test to focus on ops_service param."""

    command = f"az iot ops support create-bundle --broker-traces {mq_traces} " + "--ops-service {0}"
    if bundle_dir:
        command += f" --bundle-dir {bundle_dir}"
        try:
            mkdir(bundle_dir)
            tracked_files.append(bundle_dir)
        except FileExistsError:
            pass
    walk_result, _ = run_bundle_command(command=command.format(ops_service), tracked_files=tracked_files)
    # generate second bundle as close as possible
    if ops_service != OpsServiceType.auto.value:
        auto_walk_result, _ = run_bundle_command(
            command=command.format(OpsServiceType.auto.value),
            tracked_files=tracked_files
        )

    # Level 0 - top
    namespace = process_top_levels(walk_result, ops_service).aio

    # Level 1
    level_1 = walk_result.pop(path.join(BASE_ZIP_PATH, namespace))
    expected_services = _get_expected_services(walk_result, ops_service, namespace)
    assert sorted(level_1["folders"]) == sorted(expected_services)
    assert not level_1["files"]

    # Check and take out mq traces:
    if mq_traces and ops_service in [OpsServiceType.auto.value, OpsServiceType.mq.value]:
        mq_level = walk_result.pop(path.join(BASE_ZIP_PATH, namespace, OpsServiceType.mq.value, "traces"), {})
        if mq_level:
            assert not mq_level["folders"]
            assert_file_names(mq_level["files"])
            # make sure level 2 doesnt get messed up
            assert walk_result[path.join(BASE_ZIP_PATH, namespace, OpsServiceType.mq.value)]["folders"] == ["traces"]
            walk_result[path.join(BASE_ZIP_PATH, namespace, OpsServiceType.mq.value)]["folders"] = []

    # Level 2 and 3 - bottom
    actual_walk_result = (len(expected_services) + int(OpsServiceType.billing.value in expected_services))
    assert len(walk_result) == actual_walk_result

    for directory in walk_result:
        assert not walk_result[directory]["folders"]
        assert_file_names(walk_result[directory]["files"])

    # check service is within auto
    if ops_service != OpsServiceType.auto.value:
        expected_folders = [[]]
        if mq_traces and ops_service == OpsServiceType.mq.value:
            expected_folders.append(['traces'])
        for directory in walk_result:
            assert auto_walk_result[directory]["folders"] in expected_folders
            # make things easier if there is a different file
            auto_files = sorted(auto_walk_result[directory]["files"])
            ser_files = sorted(walk_result[directory]["files"])
            find_extra_or_missing_names(
                resource_type=f"auto bundle files not found in {ops_service} bundle",
                result_names=auto_files,
                expected_names=ser_files,
                ignore_extras=True,
                ignore_missing=True
            )


def test_create_bundle_otel(init_setup, tracked_files):
    """Test for ensuring file names and content. ONLY CHECKS otel."""
    # dir for unpacked files
    ops_service = OpsServiceType.auto.value
    command = f"az iot ops support create-bundle --ops-service {ops_service}"
    walk_result, bundle_path = run_bundle_command(command=command, tracked_files=tracked_files)
    file_map = get_file_map(walk_result, "otel")["aio"]

    expected_workload_types = ["deployment", "pod", "replicaset", "service"]
    assert set(file_map.keys()).issubset(set(expected_workload_types))
    check_workload_resource_files(
        file_objs=file_map,
        expected_workload_types=expected_workload_types,
        prefixes="aio-otel",
        bundle_path=bundle_path
    )


def _get_expected_services(
    walk_result: Dict[str, Dict[str, List[str]]], ops_service: str , namespace: str
) -> List[str]:
    expected_services = [ops_service]
    if ops_service == OpsServiceType.auto.value:
        # these should always be generated
        expected_services = OpsServiceType.list()
        expected_services.remove(OpsServiceType.auto.value)
        expected_services.append("otel")
        expected_services.sort()

    # device registry folder will not be created if there are no device registry resources
    if not walk_result.get(path.join(BASE_ZIP_PATH, namespace, OpsServiceType.deviceregistry.value))\
       and OpsServiceType.deviceregistry.value in expected_services:
        expected_services.remove(OpsServiceType.deviceregistry.value)
    expected_services.append("meta")
    return expected_services
