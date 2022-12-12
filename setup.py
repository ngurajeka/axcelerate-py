import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

install_requires = ['requests==2.25.0', ]

tests_require = [
    'requests',
    'pytest==6.1.2',
]

setuptools.setup(
    name='axcelerate',
    version='2.1.1',
    description='Axcelerate API Wrapper',
    url='https://github.com/ngurajeka/axcelerate-py',
    author='Ady Rahmat MA',
    author_email='ngurajeka.92@gmail.com',
    license='BSD',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require
)
