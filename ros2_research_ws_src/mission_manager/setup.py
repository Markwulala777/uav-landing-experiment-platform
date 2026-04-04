from setuptools import setup

package_name = "mission_manager"

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
    description="Mission-phase ownership and transition logic.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "phase_manager = mission_manager.phase_manager_node:main",
        ],
    },
)
