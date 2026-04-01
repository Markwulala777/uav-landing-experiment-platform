from setuptools import setup

package_name = "joint_bringup"

setup(
    name=package_name,
    version="0.0.1",
    packages=[],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", ["config/calm_truth.yaml", "config/moderate_truth.yaml"]),
        ("share/" + package_name + "/launch", ["launch/stage1_joint.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="jia",
    maintainer_email="jia@example.com",
    description="Launch entry points for the mixed UAV-USV stack.",
    license="MIT",
)
