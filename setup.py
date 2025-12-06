from setuptools import setup

setup(
    name="php-rs-analyzer",
    version="1.0.0",
    py_modules=["php_rs_analyzer"],
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "php-rs-analyzer = php_rs_analyzer:main"
        ]
    },
    author="Oussama Larhnimi",
    description="PHP Reverse Shell Analyzer & Payload Generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
