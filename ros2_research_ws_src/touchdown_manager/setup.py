from setuptools import setup

package_name = "touchdown_manager"

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
    description="Touchdown state and event monitoring.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "contact_monitor = touchdown_manager.contact_monitor_node:main",
            "truth_touchdown_monitor = touchdown_manager.contact_monitor_node:main",
        ],
    },
)
