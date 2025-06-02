from setuptools import find_packages
from setuptools import setup

setup(
    name="gmail-rule-engine",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "python-dateutil",
        "python-dotenv",
        "jsonschema"
    ],
    entry_points={
        "console_scripts": [
            "gmailre = app.main:cli",
        ],
    },
    author="aravindhshiva",
    description="CLI tool to load and store Gmail messages",
    python_requires=">=3.10",
)
