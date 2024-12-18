# Generated by Django 3.2.25 on 2024-11-17 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('SME', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyerSellerMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_required', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('additional_details', models.TextField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirements', to='SME.company')),
            ],
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SellerProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_available', models.DecimalField(decimal_places=2, max_digits=10)),
                ('minimum_order_quantity', models.DecimalField(decimal_places=2, default=1, max_digits=10)),
                ('available_from', models.DateField()),
                ('available_until', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SellerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller_profile', to='SME.company')),
            ],
        ),
        migrations.RemoveField(
            model_name='companymaterialrequirement',
            name='company',
        ),
        migrations.RemoveField(
            model_name='companymaterialrequirement',
            name='material',
        ),
        migrations.RemoveField(
            model_name='emailcommunication',
            name='company',
        ),
        migrations.RemoveField(
            model_name='emailcommunication',
            name='material',
        ),
        migrations.RemoveField(
            model_name='emailcommunication',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='emailcommunication',
            name='template',
        ),
        migrations.RemoveField(
            model_name='emailschedule',
            name='material',
        ),
        migrations.RemoveField(
            model_name='emailschedule',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='emailschedule',
            name='template',
        ),
        migrations.RemoveField(
            model_name='marketopportunity',
            name='company',
        ),
        migrations.RemoveField(
            model_name='marketopportunity',
            name='material',
        ),
        migrations.RemoveField(
            model_name='marketopportunity',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='primary_user',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='users',
        ),
        migrations.RemoveField(
            model_name='suppliermaterial',
            name='material',
        ),
        migrations.RemoveField(
            model_name='suppliermaterial',
            name='supplier',
        ),
        migrations.AlterUniqueTogether(
            name='usersuppliermapping',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='usersuppliermapping',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='usersuppliermapping',
            name='user',
        ),
        migrations.RenameField(
            model_name='rawmaterial',
            old_name='common_uses',
            new_name='typical_uses',
        ),
        migrations.RemoveField(
            model_name='rawmaterial',
            name='category',
        ),
        migrations.RemoveField(
            model_name='rawmaterial',
            name='typical_specifications',
        ),
        migrations.RemoveField(
            model_name='user',
            name='reset_token',
        ),
        migrations.RemoveField(
            model_name='user',
            name='reset_token_expires',
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('seller', 'Seller'), ('buyer', 'Buyer'), ('admin', 'Admin')], default='seller', max_length=10),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='material_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='sme_user_groups', related_query_name='user', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='sme_user_permissions', related_query_name='user', to='auth.Permission'),
        ),
        migrations.DeleteModel(
            name='BuyerCompany',
        ),
        migrations.DeleteModel(
            name='CompanyMaterialRequirement',
        ),
        migrations.DeleteModel(
            name='EmailCommunication',
        ),
        migrations.DeleteModel(
            name='EmailSchedule',
        ),
        migrations.DeleteModel(
            name='EmailTemplate',
        ),
        migrations.DeleteModel(
            name='MarketOpportunity',
        ),
        migrations.DeleteModel(
            name='RawMaterialCategory',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
        migrations.DeleteModel(
            name='SupplierMaterial',
        ),
        migrations.DeleteModel(
            name='UserSupplierMapping',
        ),
        migrations.AddField(
            model_name='sellerprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller_profile', to='SME.user'),
        ),
        migrations.AddField(
            model_name='sellerproduct',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offered_by', to='SME.rawmaterial'),
        ),
        migrations.AddField(
            model_name='sellerproduct',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='SME.sellerprofile'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_emails', to='SME.user'),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='to_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_emails', to='SME.company'),
        ),
        migrations.AddField(
            model_name='companyrequirement',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='required_by', to='SME.rawmaterial'),
        ),
        migrations.AddField(
            model_name='buyersellermatch',
            name='buyer_requirement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='SME.companyrequirement'),
        ),
        migrations.AddField(
            model_name='buyersellermatch',
            name='seller_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='SME.sellerproduct'),
        ),
    ]