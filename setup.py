from setuptools import setup, find_packages

setup(
    name="aetherchain",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=3.4.8",
    ],
    author="AetherChain Team",
    description="A decentralized operating system implementation based on the AetherChain white paper",
    python_requires=">=3.6",
)