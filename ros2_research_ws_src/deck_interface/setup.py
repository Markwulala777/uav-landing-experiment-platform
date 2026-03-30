from setuptools import setup

package_name = "deck_interface"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="jia",
    maintainer_email="jia@example.com",
    description="ROS 2 relay for bridged truth topics.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "truth_relay = deck_interface.truth_relay_node:main",
        ],
    },
)
