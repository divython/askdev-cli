from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="askdev",
    version="1.0.0",
    description="Android Error CLI Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="askdev contributors",
    url="https://github.com/divython/askdev-cli",
    packages=["askdev"],
    install_requires=[
        "typer[all]",
        "python-dotenv",
        "requests",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "askdev=askdev.cli:run_main",
            "ad=askdev.cli:run_main"
        ]
    },
    include_package_data=True,
    package_data={"": ["error_db.json"]},
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Utilities"
    ],
    keywords="android error cli ai fix log stacktrace",
)
