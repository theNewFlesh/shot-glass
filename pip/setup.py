from setuptools import setup, find_packages

with open('version.txt') as f:
    VERSION = f.read().strip('\n')

with open('prod_requirements.txt') as f:
    PROD_REQUIREMENTS = f.read().split('\n')

with open('dev_requirements.txt') as f:
    DEV_REQUIREMENTS = f.read().split('\n')

with open('README.md') as f:
    README = f.read()
# ------------------------------------------------------------------------------

setup(
    name='shot-glass',
    packages=find_packages(where='./', exclude=['.*test.*.py', '.*.pyc']),
    package_dir={'shot-glass': 'shot-glass'},
    include_package_data=True,
    version=VERSION,
    license='MIT',
    description='A cloud native service for working with Blender geometry.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Alex Braun',
    author_email='alexander.g.braun@gmail.com',
    url='https://github.com/theNewFlesh/shot-glass',
    download_url='https://github.com/theNewFlesh/shot-glass/archive/' + VERSION + '.tar.gz',
    keywords=['blender', 'computer vision', 'geometry', '3D', 'cloud'],
    install_requires=PROD_REQUIREMENTS,
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.7',
    ],
    extras_require={
        "dev": DEV_REQUIREMENTS
    },
)
