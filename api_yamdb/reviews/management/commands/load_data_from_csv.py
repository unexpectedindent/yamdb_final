import os
from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)

DATA_EXISTS = 'Data already there is in database "{}"'


DATABASES = {
    'User': User,
    'Category': Category,
    'Genre': Genre,
    'Title': Title,
    'GenreTitle': GenreTitle,
    'Review': Review,
    'Comment': Comment,
}


class Command(BaseCommand):
    help = ('Load data to database from csv-files. '
            'Use command: "python manage.py load_data_from_csv".')

    def handle(self, *args, **options):
        for db_label, db in DATABASES.items():
            file_name = '.'.join([db_label.lower(), 'csv'])
            file_path = os.path.join(
                settings.STATIC_ROOT,
                'data',
                file_name
            )

            if db.objects.exists():
                print(DATA_EXISTS.format(db_label))
            elif not os.path.exists(file_path):
                print('File {} not exists.'.format(file_name))
            else:
                print('Loading data into "{}"...'.format(db_label))

                with open(file_path, mode='r', encoding='utf-8') as source:
                    try:
                        file_image = DictReader(source)
                    except Exception as e:
                        print(f'Can not read csv-file: {e}')
                        continue
                    cnt_loaded = 0
                    cnt_total = 0
                    errors = set()
                    for line in file_image:
                        cnt_total += 1
                        try:
                            db.objects.create(**line)
                            cnt_loaded += 1
                        except Exception as e:
                            errors = errors | e
                            continue
                    print(
                        'Loaded {} from {} rows'.format(
                            cnt_loaded,
                            cnt_total
                        )
                    )
                    print('Errors:', *errors)
