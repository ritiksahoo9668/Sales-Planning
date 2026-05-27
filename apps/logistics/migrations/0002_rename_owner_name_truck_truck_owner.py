from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='truck',
            old_name='owner_name',
            new_name='truck_owner',
        ),
    ]
