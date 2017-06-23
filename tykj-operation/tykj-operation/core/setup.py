from setuptools import setup, find_packages
setup(
    name='estore-core',
    version='1.0',
    packages=find_packages(),
    license='',
    long_description=open('README.txt').read(),
    author='estore',
    author_email='support@xxx.com',
    maintainer='estore',
    url='http://www.xxx.com/',
    package_data = {
            "estorecore": ['locale/zh_CN/LC_MESSAGES/*.mo'],
            "estorecore.reporting": ['templates/*.html'],
            "estorecore.utils": ['*.png', 'verify_code/*.ttf', 'verify_code/*.list'],
        }
)
