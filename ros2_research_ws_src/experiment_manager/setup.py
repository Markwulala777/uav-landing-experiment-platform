from setuptools import setup

package_name = "experiment_manager"

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
    description="Scenario and output management for Phase 1.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "scenario_runner = experiment_manager.scenario_runner:main",
        ],
    },
)
