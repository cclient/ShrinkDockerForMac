from setuptools import setup
import shrink


setup(name='shrink',
      version=shrink.__version__,
      description=shrink.__description__,
      author=shrink.__author__,
      url='https://github.com/robintiwari/mongobackup',
      license=shrink.__license__,
      platforms=['all'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: Jython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Shrink Docker For Mac hyperkit VM disk',
      ],
      py_modules=['shrink'],
      )
