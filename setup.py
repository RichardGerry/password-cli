from setuptools import setup

setup(name="password_cli",
      version="1.0.0",
      description=("store and retrieve application "
                   "user names and passwords"),
      author="Richard Gerry",
      packages=["pw"],
      python_requires=">=3.5",
      entry_points={
          "console_scripts":[
              "pw = pw.__main__:main"
              ]
          }
      )
