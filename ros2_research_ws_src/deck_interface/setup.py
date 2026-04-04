from setuptools import find_packages, setup

package_name = "deck_interface"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "README.md"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="jia",
    maintainer_email="jia@example.com",
    description="ROS 2 relay for bridged truth topics.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "deck_truth_ingest = deck_interface.deck_truth_ingest_node:main",
            "landing_zone_state = deck_interface.landing_zone_state_node:main",
            "uav_truth_provider = deck_interface.transitional.uav_truth_provider_node:main",
            "truth_relay = deck_interface.deck_truth_ingest_node:main",
        ],
    },
)
