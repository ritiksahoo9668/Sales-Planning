from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0002_alter_vendorprofile_gst_no_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='vendorprofile',
            index=models.Index(
                fields=['vendor_type', 'office_status'],
                name='vendors_ven_vendor__3066fd_idx',
            ),
        ),
    ]
