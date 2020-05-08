from setuptools import setup

with open("requirements.txt") as f:
    requires = f.readlines()

setup(name="password_cli",
      version="1.0.0",
      description=("store and retrieve application "
                   "user names and passwords"),
      author="Richard Gerry",
      packages=["pw"],
      python_requires=">=3.5",
      install_requires=requires,
      entry_points={
          "console_scripts":[
              "pw = pw.__main__:main"
              ]
          }
      )
