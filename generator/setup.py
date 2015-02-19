#!/usr/bin/env python
from setuptools import setup
setup(name='generator',
		version='.001',
		description='A very brittle static site generator for josephhader.comkj',
		author='gigawhitlocks',
		author_email='giggles@alum.hackerschool.com',
		entry_points={'console_scripts': ['gen_portfolio=generator.generate_site:main']},
		py_modules=['generator'])
