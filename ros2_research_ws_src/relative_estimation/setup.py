from setuptools import setup

package_name = "relative_estimation"

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
    description="Truth-level relative-state estimation.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "truth_relative_state = relative_estimation.truth_relative_state_node:main",
        ],
    },
)
