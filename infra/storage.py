import pulumi_openstack as openstack


db_volume = openstack.blockstorage.Volume(
    "db-volume",
    name="db-data-volume",
    size=50,
    volume_type="NVMe",
    description="Persistent volume for database storage"
)