import os

file_dir = os.path.dirname(os.path.realpath(__file__))

CORE_LOCALE_PATH = (
    os.path.join(file_dir, 'locale'),
)

CORE_TEMPLATE_DIRS = (
    os.path.join(file_dir, "reporting/templates"),
)