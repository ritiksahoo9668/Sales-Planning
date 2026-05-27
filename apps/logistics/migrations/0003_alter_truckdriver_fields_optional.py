from django.db import migrations, models

import apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0002_rename_owner_name_truck_truck_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='truckdriver',
            name='aadhar_number',
            field=models.CharField(
                blank=True,
                max_length=12,
                validators=[apps.common.validators.validate_aadhar],
                verbose_name='Aadhar Number',
            ),
        ),
        migrations.AlterField(
            model_name='truckdriver',
            name='dl_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='DL Number'),
        ),
        migrations.AlterField(
            model_name='truckdriver',
            name='name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='truckdriver',
            name='phone',
            field=models.CharField(
                blank=True,
                max_length=20,
                validators=[apps.common.validators.validate_phone],
                verbose_name='Phone',
            ),
        ),
    ]
