from setuptools import setup

package_name = "landing_decision"

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
    description="Landing-window and advisory logic.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "window_status = landing_decision.window_status_node:main",
            "decision_advisory = landing_decision.decision_advisory_node:main",
        ],
    },
)
