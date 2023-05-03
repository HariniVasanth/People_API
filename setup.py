import setuptools

setuptools.setup(
      name='planon',
      version='0.0.1',
      description='Collection of Python modules/submodules for standardizing how connections and interactions with various systems are handled.',
      author='Dartmouth College - Campus Services Technology Services',
      author_email='csts@groups.dartmouth.edu',
      packages=setuptools.find_packages(),
      license='MIT',
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires='>=3.9',
      install_requires = ["requests", "pydantic"],
      zip_safe=False
)