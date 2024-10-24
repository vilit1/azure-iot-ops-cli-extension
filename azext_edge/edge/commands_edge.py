# coding=utf-8
# ----------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License file in the project root for license information.
# ----------------------------------------------------------------------------------------------

import json
from os.path import exists
from pathlib import PurePath
from typing import Any, Dict, Iterable, List, Optional, Union

from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger

from .common import OpsServiceType
from .providers.base import DEFAULT_NAMESPACE, load_config_context
from .providers.check.common import ResourceOutputDetailLevel
from .providers.edge_api.orc import ORC_API_V1
from .providers.orchestration.common import (
    DEFAULT_SERVICE_PRINCIPAL_SECRET_DAYS,
    DEFAULT_X509_CA_VALID_DAYS,
    KEYVAULT_ARC_EXTENSION_VERSION,
    KubernetesDistroType,
    MqMemoryProfile,
    MqServiceType,
)
from .providers.orchestration.resources import Instances
from .providers.support.base import get_bundle_path

logger = get_logger(__name__)


def support_bundle(
    cmd,
    log_age_seconds: int = 60 * 60 * 24,
    ops_service: str = OpsServiceType.auto.value,
    bundle_dir: Optional[str] = None,
    include_mq_traces: Optional[bool] = None,
    context_name: Optional[str] = None,
) -> Union[Dict[str, Any], None]:
    load_config_context(context_name=context_name)
    from .providers.support_bundle import build_bundle

    bundle_path: PurePath = get_bundle_path(bundle_dir=bundle_dir)
    return build_bundle(
        ops_service=ops_service,
        bundle_path=str(bundle_path),
        log_age_seconds=log_age_seconds,
        include_mq_traces=include_mq_traces,
    )


def check(
    cmd,
    detail_level: int = ResourceOutputDetailLevel.summary.value,
    pre_deployment_checks: Optional[bool] = None,
    post_deployment_checks: Optional[bool] = None,
    as_object=None,
    context_name=None,
    ops_service: str = OpsServiceType.mq.value,
    resource_kinds: List[str] = None,
    resource_name: str = None,
) -> Union[Dict[str, Any], None]:
    load_config_context(context_name=context_name)
    from .providers.checks import run_checks

    # by default - run prechecks if AIO is not deployed
    run_pre = not ORC_API_V1.is_deployed() if pre_deployment_checks is None else pre_deployment_checks
    run_post = True if post_deployment_checks is None else post_deployment_checks

    # only one of pre or post is explicity set to True
    if pre_deployment_checks and not post_deployment_checks:
        run_post = False
    if post_deployment_checks and not pre_deployment_checks:
        run_pre = False

    return run_checks(
        ops_service=ops_service,
        detail_level=detail_level,
        as_list=not as_object,
        resource_name=resource_name,
        pre_deployment=run_pre,
        post_deployment=run_post,
        resource_kinds=resource_kinds,
    )


def verify_host(
    cmd,
    no_progress: Optional[bool] = None,
):
    from .providers.orchestration import run_host_verify

    run_host_verify(render_progress=not no_progress)
    return


def init(
    cmd,
    cluster_name: str,
    resource_group_name: str,
    instance_name: Optional[str] = None,
    instance_description: Optional[str] = None,
    cluster_namespace: str = DEFAULT_NAMESPACE,
    keyvault_spc_secret_name: str = DEFAULT_NAMESPACE,
    custom_location_name: Optional[str] = None,
    location: Optional[str] = None,
    show_template: Optional[bool] = None,
    simulate_plc: Optional[bool] = None,
    container_runtime_socket: Optional[str] = None,
    kubernetes_distro: str = KubernetesDistroType.k8s.value,
    no_block: Optional[bool] = None,
    no_progress: Optional[bool] = None,
    mq_memory_profile: str = MqMemoryProfile.medium.value,
    mq_service_type: str = MqServiceType.cluster_ip.value,
    mq_backend_partitions: int = 2,
    mq_backend_workers: int = 2,
    mq_backend_redundancy_factor: int = 2,
    mq_frontend_workers: int = 2,
    mq_frontend_replicas: int = 2,
    mq_frontend_server_name: str = "mq-dmqtt-frontend",
    mq_listener_name: str = "listener",
    mq_broker_name: str = "broker",
    mq_authn_name: str = "authn",
    mq_broker_config_file: Optional[str] = None,
    mq_insecure: Optional[bool] = None,
    dataflow_profile_instances: int = 1,
    disable_secret_rotation: Optional[bool] = None,
    rotation_poll_interval: str = "1h",
    csi_driver_version: str = KEYVAULT_ARC_EXTENSION_VERSION,
    csi_driver_config: Optional[List[str]] = None,
    service_principal_app_id: Optional[str] = None,
    service_principal_object_id: Optional[str] = None,
    service_principal_secret: Optional[str] = None,
    service_principal_secret_valid_days: int = DEFAULT_SERVICE_PRINCIPAL_SECRET_DAYS,
    keyvault_resource_id: Optional[str] = None,
    tls_ca_path: Optional[str] = None,
    tls_ca_key_path: Optional[str] = None,
    tls_ca_dir: Optional[str] = None,
    tls_ca_valid_days: int = DEFAULT_X509_CA_VALID_DAYS,
    template_path: Optional[str] = None,
    no_deploy: Optional[bool] = None,
    no_tls: Optional[bool] = None,
    disable_rsync_rules: Optional[bool] = None,
    context_name: Optional[str] = None,
    ensure_latest: Optional[bool] = None,
) -> Union[Dict[str, Any], None]:
    from .common import INIT_NO_PREFLIGHT_ENV_KEY
    from .providers.orchestration import deploy
    from .util import (
        assemble_nargs_to_dict,
        is_env_flag_enabled,
        read_file_content,
        url_safe_random_chars,
    )

    no_preflight = is_env_flag_enabled(INIT_NO_PREFLIGHT_ENV_KEY)

    if all([no_tls, not keyvault_resource_id, no_deploy, no_preflight]):
        logger.warning("Nothing to do :)")
        return

    load_config_context(context_name=context_name)

    # cluster namespace must be lowercase
    cluster_namespace = str(cluster_namespace).lower()
    cluster_name_lowered = cluster_name.lower()
    # TODO - @digimaun
    safe_cluster_name = cluster_name_lowered.replace("_", "-")

    if not instance_name:
        instance_name = f"{safe_cluster_name}-ops-instance"

    if not custom_location_name:
        custom_location_name = f"{cluster_name_lowered}-{url_safe_random_chars(5).lower()}-ops-init-cl"

    if tls_ca_path:
        if not tls_ca_key_path:
            raise InvalidArgumentValueError("When using --ca-file, --ca-key-file is required.")

        if not exists(tls_ca_path):
            raise InvalidArgumentValueError("Provided CA file does not exist.")

        if not exists(tls_ca_key_path):
            raise InvalidArgumentValueError("Provided CA private key file does not exist.")

    if csi_driver_config:
        csi_driver_config = assemble_nargs_to_dict(csi_driver_config)

    # TODO - @digimaun
    mq_broker_config = None
    if mq_broker_config_file:
        mq_broker_config = json.loads(read_file_content(file_path=mq_broker_config_file))

    return deploy(
        cmd=cmd,
        cluster_name=cluster_name,
        cluster_namespace=cluster_namespace,
        instance_name=instance_name,
        instance_description=instance_description,
        cluster_location=None,  # Effectively always fetch connected cluster location
        custom_location_name=custom_location_name,
        resource_group_name=resource_group_name,
        location=location,
        show_template=show_template,
        container_runtime_socket=container_runtime_socket,
        kubernetes_distro=str(kubernetes_distro),
        simulate_plc=simulate_plc,
        no_block=no_block,
        no_progress=no_progress,
        no_tls=no_tls,
        no_preflight=no_preflight,
        no_deploy=no_deploy,
        disable_rsync_rules=disable_rsync_rules,
        mq_broker_config=mq_broker_config,
        mq_memory_profile=str(mq_memory_profile),
        mq_service_type=str(mq_service_type),
        mq_backend_partitions=int(mq_backend_partitions),
        mq_backend_workers=int(mq_backend_workers),
        mq_backend_redundancy_factor=int(mq_backend_redundancy_factor),
        mq_frontend_replicas=int(mq_frontend_replicas),
        mq_frontend_workers=int(mq_frontend_workers),
        mq_frontend_server_name=str(mq_frontend_server_name),
        mq_listener_name=str(mq_listener_name),
        mq_broker_name=str(mq_broker_name),
        mq_authn_name=str(mq_authn_name),
        mq_insecure=mq_insecure,
        dataflow_profile_instances=int(dataflow_profile_instances),
        keyvault_resource_id=keyvault_resource_id,
        keyvault_spc_secret_name=str(keyvault_spc_secret_name),
        disable_secret_rotation=disable_secret_rotation,
        rotation_poll_interval=str(rotation_poll_interval),
        csi_driver_version=str(csi_driver_version),
        csi_driver_config=csi_driver_config,
        service_principal_app_id=service_principal_app_id,
        service_principal_object_id=service_principal_object_id,
        service_principal_secret=service_principal_secret,
        service_principal_secret_valid_days=int(service_principal_secret_valid_days),
        tls_ca_path=tls_ca_path,
        tls_ca_key_path=tls_ca_key_path,
        tls_ca_dir=tls_ca_dir,
        tls_ca_valid_days=int(tls_ca_valid_days),
        template_path=template_path,
    )


def delete(
    cmd,
    cluster_name: str,
    resource_group_name: str,
    confirm_yes: Optional[bool] = None,
    no_progress: Optional[bool] = None,
    force: Optional[bool] = None,
):
    from .providers.orchestration import delete_ops_resources

    return delete_ops_resources(
        cmd=cmd,
        cluster_name=cluster_name,
        resource_group_name=resource_group_name,
        confirm_yes=confirm_yes,
        no_progress=no_progress,
        force=force,
    )


def show_instance(cmd, instance_name: str, resource_group_name: str, show_tree: Optional[bool] = None) -> dict:
    return Instances(cmd).show(name=instance_name, resource_group_name=resource_group_name, show_tree=show_tree)


def list_instances(cmd, resource_group_name: Optional[str] = None) -> Iterable[dict]:
    return Instances(cmd).list(resource_group_name)


def update_instance(
    cmd,
    instance_name: str,
    resource_group_name: str,
    tags: Optional[str] = None,
    instance_description: Optional[str] = None,
    **kwargs,
) -> dict:
    return Instances(cmd).update(
        name=instance_name,
        resource_group_name=resource_group_name,
        tags=tags,
        description=instance_description,
        **kwargs,
    )
