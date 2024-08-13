swagger:
https://github.com/Azure/azure-rest-api-specs-pr/blob/RPSaaSMaster/specification/deviceregistry/resource-manager/Microsoft.DeviceRegistry/preview/2024-07-01-preview/deviceregistry.json

## Assets
id: `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.DeviceRegistry/assets/my-asset`

discovered assets are a different thing but have the same props: `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.DeviceRegistry/discoveredAssets/my-asset`
- the discovered asset is supposed to be created from the edge/cluster rather than cloud
- create/update/delete are still allowed via the API
- list via the regular vs discovered should yeild different asset lists


Main changes:
- datapoints are now under dataset
- addition of topic property
- removal of some other properties
- somehow event/dataset requirement is no longer there?

### asset

  create

	--asset [or --name]
	--instance
	--resource-group
	--endpoint-profile
	[optional]
	--custom-attribute
	--data-set-file
	--default-topic-path
	--default-topic-retention (`keep`, `never`) [may turn this into a bool flag]
	--description
	--disabled [flag]
	--display-name
	--documentation-uri
	--event [key=value pairs, `event_notifier`, `name` required]
	--event-file
	--external-asset-id
	--hardware-revision
	--instance-resource-group
	--instance-subscription
	--location
	--manufacturer
	--manufacturer-uri
	--model
	--product-code
	--serial-number
	--software-revision
	--dataset-publishing-interval
	--dataset-sampling-interval
	--dataset-queue-size
	--event-publishing-interval
	--event-sampling-interval
	--event-queue-size
	--tags

  delete

	--asset [or --name]
	--resource-group

  list

	[optional]
	--discovered [bool flag]
	--resource-group
	--endpoint-profile
	--instance
	--instance-resource-group [require for instance]
	--display-name
	--documentation-uri
	--external-asset-id
	--hardware-revision
	--instance-resource-group
	--instance-subscription
	--location
	--manufacturer
	--manufacturer-uri
	--model
	--product-code
	--serial-number
	--resource-query

  show

	--asset [or --name]
	--resource-group

  update

	--asset [or --name]
	--resource-group
	[optional]
	--custom-attribute
	--default-topic-path
	--default-topic-retention (`keep`, `never`) [may turn this into a bool flag]
	--description
	--disabled [flag]
	--display-name
	--documentation-uri
	--hardware-revision
	--instance-resource-group
	--instance-subscription
	--location
	--manufacturer
	--manufacturer-uri
	--model
	--product-code
	--serial-number
	--software-revision
	--dataset-publishing-interval
	--dataset-sampling-interval
	--dataset-queue-size
	--event-publishing-interval
	--event-sampling-interval
	--event-queue-size
	--tags

### asset dataset

  add

	--asset
	--resource-group
	--dataset [or --name]
	[optional]
	--data-point [key=value pairs, `data_source`, `name` required]
	--data-point-file
	--publishing-interval
	--sampling-interval
	--queue-size
	--topic-path
	--topic-retention (`keep`, `never`) [may turn this into bool flag]

  export

	--asset
	--resource-group
	[optional]
	--format (`json`, `yaml`, maybe `portal-csv`)
	--output-dir
	--replace

  import

	--asset
	--resource-group
	--input-file
	[optional]
	--replace

  list

	--asset
	--resource-group

  show

	--asset
	--resource-group
	--dataset [or --name]

  remove

	--asset
	--resource-group
	--dataset [or --name]

  update

	--asset
	--resource-group
	--dataset [or --name]
	[optional]
	--publishing-interval
	--sampling-interval
	--queue-size
	--topic-path
	--topic-retention (`keep`, `never`) [may turn this into bool flag]

### asset dataset datapoint

  add

	--asset
	--resource-group
	--dataset
	--data-point [or --name]
	--data-source
	[optional]
	--observability-mode (`none`, `counter`, `gauge`, `histogram`, `log`)
	--publishing-interval
	--sampling-interval
	--queue-size

  export

	--asset
	--resource-group
	--dataset
	[optional]
	--format (`json`, `yaml`, `portal-csv`)
	--output-dir
	--replace

  import

	--asset
	--resource-group
	--dataset
	--input-file
	[optional]
	--replace

  list

	--asset
	--resource-group
	--dataset

  remove

	--asset
	--resource-group
	--dataset
	--data-point [or --name]

  update

	--asset
	--resource-group
	--data-set
	--data-point [or --name]
	[optional]
	--observability-mode (`none`, `counter`, `gauge`, `histogram`, `log`)
	--publishing-interval
	--sampling-interval
	--queue-size

### asset event

  add

	--asset
	--resource-group
	--event [or --name]
	--event-notifier
	[optional]
	--observability-mode (`none`, `log`)
	--publishing-interval
	--sampling-interval
	--queue-size
	--topic-path
	--topic-retention (`keep`, `never`) [may turn this into bool flag]

  export

	--asset
	--resource-group
	[optional]
	--format (`json`, `yaml`, `portal-csv`)
	--output-dir
	--replace

  import

	--asset
	--resource-group
	--input-file
	[optional]
	--replace

  list

	--asset
	--resource-group

  remove

	--asset
	--resource-group
	--event [or --name]

  update

	--asset
	--resource-group
	--event [or --name]
	[optional]
	--observability-mode (`none`, `log`)
	--publishing-interval
	--sampling-interval
	--queue-size
	--topic-path
	--topic-retention (`keep`, `never`) [may turn this into bool flag]

## Asset Endpoint Profiles
id: `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.DeviceRegistry/assetEndpointProfiles/my-assetendpointprofile`

main changes: remove the cert subgroup, modify some create/update params.

Discovered asset endpoint profiles are different but have the same props:
id: `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.DeviceRegistry/discoveredAssetEndpointProfiles/my-assetendpointprofile`

### asset endpoint

  create

	--endpoint-profile [or --name]
	--instance
	--resource-group
	--target-address
	[optional]
	--location
	--instance-resource-group
	--instance-subscription
	--additional-configuration
	--profile-type
	--certificate-ref [use this, user/password-ref to determine auth-mode]
	--password-ref
	--user-ref
	--tags

  delete

	--endpoint-profile [or --name]
	--resource-group

  list/query

	[optional]
	--discovered [bool flag]
	--resource-group
	--instance
	--instance-resource-group [required if instance is used]
	--target-address
	--auth-mode
	--profile-type
	--resource-query

  show

	--endpoint-profile [or --name]
	--resource-group

  update

	--endpoint-profile [or --name]
	--resource-group
	[optional]
	--target-address
	--additional-configuration
	--profile-type
	--certificate-ref [use this, user/password-ref to determine auth-mode]
	--password-ref
	--user-ref
	--tags

## Schemas

Need to create schema registry first. Schema is a subresource. Schema version is a subresource of schema.

In the end, the id (for version) looks like this: `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.DeviceRegistry/schemaRegistries/my-schema-registry/schemas/my-schema/schemaVersions/1`

custom location is not needed...

### schema
  create

	--schema [or --name]
	--schema-registry
	--resource-group
	--format
	--schema-type
	[optional]
	--description
	--display-name
	--tags

  delete

	--schema [or --name]
	--resource-group

  show

	--schema [or --name]
	--resource-group

  list

	--resource-group
	--schema-registry
	[optional]
	--format
	--schema-type
	--display-name

### schema registry
  create

	--schema-registry [or --name]
	--resource-group
	--namespace
	--storage-container-uri
	[optional]
	--display-name
	--description
	--tags

  delete

	--schema-registry [or --name]
	--resource-group

  show

	--schema-registry [or --name]
	--resource-group

  list/query

	[optional]
	--resource-group
	--display-name
	--namespace
	--storage-container-uri
	--resource-query

  update

	--schema-registry [or --name]
	--resource-group
	[optional]
	--display-name
	--description
	--tags

### schema version
  create

	--schema-version [or --name]
	--schema
	--schema-registry
	--resource-group
	--content
	[optional]
	--description

  delete

	--schema-version [or --name]
	--schema
	--schema-registry
	--resource-group

  list

	--schema
	--schema-registry
	--resource-group

  show

	--schema-version [or --name]
	--schema
	--schema-registry
	--resource-group


## Billing containers?
### billing-containers [may prepend device-registry or asset to avoid confusion or just skip this]
  list/query

	[optional]
	--container-name
