import setuptools

setuptools.setup(
    name='params_toolbox',
    version="0.0.1",
    author="Lucas Frérot",
    author_email="lucas.frerot@protonmail.com",
    description="Utility scripts to manage parameters/output DB",
    packages=setuptools.find_packages(),
    scripts=['params_toolbox.sh'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
