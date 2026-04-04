from setuptools import setup

package_name = "safety_manager"

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
    description="Safety monitoring and optional reference filtering.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "safety_monitor = safety_manager.safety_monitor_node:main",
            "reference_filter = safety_manager.reference_filter_node:main",
            "truth_safety_monitor = safety_manager.safety_monitor_node:main",
        ],
    },
)
