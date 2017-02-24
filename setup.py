from setuptools import setup

setup(
    name='pytest-pudb',
    license='MIT',
    description='Pytest PuDB debugger integration',
    author='Michael Elovskikh',
    author_email='wronglink@gmail.com',
    url='https://github.com/wronglink/pytest-pudb',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    version='0.4',
    py_modules=['pytest_pudb'],
    entry_points={'pytest11': ['pudb = pytest_pudb']},
    install_requires=['pytest>=2.0', 'pudb'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)
