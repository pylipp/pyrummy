from setuptools import setup, find_packages

setup(
        name="pyrummy",
        version="0.1",
        description="Rummy Computer written in Python",
        url="http://github.com/pylipp/pyrummy",
        author="Philipp Metzner",
        author_email="beth.aleph@yahoo.de",
        license="GPLv3",
        #classifiers=[],
        packages=find_packages(exclude=["test", "doc"]),
        entry_points = {
            "console_scripts": ["pyrummy = pyrummy.game:main"]
            },
        install_requires=[]
        )
