from setuptools import setup

package_name = "frame_audit"

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
    description="Frame audit checks for Phase 1.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "truth_frame_audit = frame_audit.truth_frame_audit:main",
        ],
    },
)
