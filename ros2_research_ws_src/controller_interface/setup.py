from setuptools import setup

package_name = "controller_interface"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "README.md"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="jia",
    maintainer_email="jia@example.com",
    description="Reference selection, tracking commands, and PX4 offboard bridge.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "reference_mux = controller_interface.reference_mux_node:main",
            "tracking_controller = controller_interface.tracking_controller_node:main",
            "px4_offboard_bridge = controller_interface.px4_offboard_bridge_node:main",
        ],
    },
)
